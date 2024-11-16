"""
Defines the left-corner parser object
"""
from loguru import logger
from dataclasses import dataclass
from lc_rule import LCRule
from mg import MG, Feature, LexItem, parse_features

UNKNOWN_POS = 99
UNKNOWN_STYPE = '.'

@dataclass
class Expression:
    left: int # left position
    right: int # right position
    stype: str # : or ::
    features: list[Feature]
    movers: list[Feature]

    def __str__(self):
        return f"({self.left}-{self.right}{self.stype} {self.features} {self.movers})"

    def __repr__(self):
        return str(self)


@dataclass
class Term:
    exp: Expression
    output_exp: Expression = None

    def is_single(self) -> bool:
        return self.output_exp is None

    def __str__(self):
        if self.output_exp:
            return f"{self.exp} => {self.output_exp}"
        return f"{self.exp}"

    def __repr__(self):
        return str(self)

@dataclass
class Configuration:
    current_pos: int
    remaining_input: list[str]
    queue: list[Term]

    def get_queue_string(self):
        elements = '\t'.join([str(q) for q in self.queue])
        return f"§{elements}§"
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Pos:{self.current_pos},\tInput: {self.remaining_input},\tQueue:{self.get_queue_string()}"

class LCParser:
    def __init__(self, grammar : MG):
        self.grammar = grammar
        self.logger = logger

    def log_stack(self, stack):
        stack_str = 'STACK:\n'
        for config, applied_rules in stack:
            stack_str += f"Config: {config}, Rules: {applied_rules}\n"
        self.logger.warning(stack_str)

    def generate_parsing_rules(self):
        """
        Generate the appropriate rules for the parsing process.
        Based on the lexicon, add the relevant empty-shift rules (e.g., shift([], [=v,c])).
        :return: A list of parsing rules.
        """
        parsing_rules = self.grammar.rules
        for item in self.grammar.lexicon:
            # Add the empty-shift rule for each feature
            if item.element == '':
                # we abuse ':' as a separator between the lexical item and its features
                parsing_rules.append(LCRule(f"shift([]:[{item.features}])"))
        return parsing_rules


    def parse(self, input_str : list[str], rules : list[LCRule] =None):
        """
        Parse the input string using the provided rules.
        This is of course different from the Prolog version, we do not define parse_steps()
        which calls itself recursively, but instead we use a stack to keep track of the configurations.
        That is why we don't keep track of the count per successful derivation, but we can add it if needed.
        :param input_str: The input string to parse as a list of tokens, (e.g., ['John', 'likes', 'Mary'])
        :param rules: Optional rules to use for parsing; if not provided, use the grammar's rules.
        :return: A list of successful configurations and the applied rules.
        """
        parsing_rules = rules or self.generate_parsing_rules()
        self.logger.info(f"Parsing the sentence: {input_str}")
        self.logger.info(f"Using the rules: {parsing_rules}")
        self.logger.info(f"Using the grammar: {self.grammar}")

        initial_config = Configuration(0, input_str, [])
        stack = [(initial_config, [])]
        results = []

        while stack:
            config, applied_rules = stack.pop()
            self.logger.error(f"Popping config {config} with {len(applied_rules)} applied rules {applied_rules}")
            if self.is_success(config):
                results.append((config, applied_rules))
                continue

            # Explore applying each rule to the current configuration
            for rule in parsing_rules:

                # Skip the empty-shift rule if it has already been applied
                if rule.is_empty_shift() and rule in applied_rules:
                    self.logger.info(f"Skipping rule: {rule} as it has already been applied!")
                    continue

                new_config = self.apply_rule(rule, config) # step()
                # if we passed the step (i.e., the oracle check passed), add the new configuration to the stack
                if new_config != config:
                    count = len(applied_rules) + 1
                    self.logger.warning(f"{count}. {rule} {new_config.remaining_input}\n{new_config.queue}")
                    stack.append((new_config, applied_rules + [rule]))
                    self.log_stack(stack)

        return results


    def is_success(self, config : Configuration):
        return False

    def apply_rule(self, rule : LCRule, config : Configuration) -> Configuration:
        """
        Applies a parsing rule to the current configuration.
        :param rule: The rule to apply.
        :param config: The current parser state.
        :return: Updated configuration after applying the rule.
        """
        self.logger.info(f"Got rule: {rule}, config: {config}")
        new_pos = config.current_pos
        new_input = config.remaining_input
        new_queue = config.queue
        result : Term = None

        # Apply a shift rule
        if rule.is_empty_shift(): # can be applied at any time
            # get the features of the empty lexical item
            fs = rule.inner_part.split(':')[1].strip('[]')
            result = self.empty_shift(fs, config.current_pos)

        elif rule.is_shift(): # based on remaining input
            result, new_pos, new_input = self.shift(config.remaining_input, config.current_pos)

        # Apply the LC rule to the queue's focus element
        elif rule.is_lc():
            if not config.queue:
                self.logger.info("No focus element in the queue! returning same config")
                return config

            focus, *remaining_queue = config.queue  # unpack the queue
            result = self.lc(rule, focus)
            new_queue = remaining_queue

        # Apply the inner lc rule; than composeOrNot()
        elif rule.is_comp():
            self.logger.info(f"apply_rule(): Rule type is comp")
        else:
            raise ValueError(f"apply_rule(): Unknown rule type: {rule}")


        if result is None:
            self.logger.info("No result after applying the rule! returning same config")
            return config

        # Update queue with the result if oracle check passes
        if self.oracle_ok(new_queue, result):
            self.logger.info("Passed the oracle check! returning new config")
            return Configuration(new_pos, new_input, [result] + new_queue)

        # If the oracle fails, return the configuration unchanged for now
        self.logger.info("Failed the oracle check! returning same config")
        return config


    def empty_shift(self, fs, pos) -> Term:
        """
        Empty shift operation: moves an empty element to the queue.
        shift(Input,Input,shift([],Fs),Pos,Pos,(Pos,Pos,'::',Fs,[])) :- ([]::Fs).

        :param fs: Features of the empty element, as concatenated string (e.g., '=v,+wh,c')
        :param pos: Current position in the input.
        :return: The new result term.
        """
        self.logger.info(f"fs = [{fs}], pos = {pos}")
        features = parse_features(fs)
        result = Expression(pos, pos, '::', features, [])
        return Term(result)

    def shift(self, input_data, pos) -> (Term, int, list[str]):
        """
        Shift operation: moves an element from input to the queue.
        shift([W|Input],Input,shift([W],Fs),Pos0,Pos,(Pos0,Pos,'::',Fs,[])) :- ([W]::Fs), Pos is Pos0+1.

        :param input_data: List of tokens representing the remaining input.
        :param pos: Current position in the input.
        :return: A tuple with the result of shift (new queue element), updated position,
                 and the remaining input after the shift.
        """
        if not input_data:
            return None, pos, input_data

        W = input_data[0]
        new_input = input_data[1:]

        # TODO: make sure to include the correct features for the token and use it later on
        # For simplicity, assume each token has features associated with it in the lexicon.
        new_pos = pos + 1
        fs = self.grammar.get_lexicon_item(W).features
        result = Expression(pos, new_pos, '::', fs, [])
        return Term(result), new_pos, new_input



    def lc(self, rule, focus : Term) -> Term:
        """
        Apply the appropriate LC rule to the focus element.
        :param rule: The LC rule to apply.
        :param focus: The focus element in the queue.
        :return: The new result term; None if the rule does not apply.
        """
        # Apply the appropriate LC rule to the focus element
        if rule.lc_rule == 'lc1':
            if rule.inner_part == 'merge1':
                return self.lc1_merge1(focus)
            elif rule.inner_part == 'merge2':
                return self.lc1_merge2(focus)
            elif rule.inner_part == 'merge3':
                return self.lc1_merge3(focus)
            elif rule.inner_part == 'move1':
                return self.lc1_move1(focus)
            elif rule.inner_part == 'move2':
                return self.lc1_move2(focus)
        elif rule.lc_rule == 'lc2':
            if rule.inner_part == 'merge2':
                return self.lc2_merge2(focus)
            elif rule.inner_part == 'merge3':
                return self.lc2_merge3(focus)

    def lc1_merge1(self, focus : Term) -> Term:
        """
        (Left, Mid, '::', [=F|Gamma], []),
        ( (Mid, Right, _,  [F], Alphas) -> (Left, Right, ':', Gamma, Alphas) )).

        :param focus:
        :return:
        """
        self.logger.info(f"focus={focus}")

        # Make sure the focus is a single expression
        if not focus.is_single():
            return None
        B = focus.exp

        # Validate match for lc1(merge1)
        #
        if (B.stype != '::') or (not B.features) or (B.features[0].prefix != '=') or (B.movers):
            return None

        left, mid, right = B.left, B.right, UNKNOWN_POS

        # Extract the feature being selected
        f = B.features[0].feature  # take 'f' from '=f'
        gamma = B.features[1:]  # Remaining features after `=F`

        C = Expression(mid, right, UNKNOWN_STYPE, [Feature(f)], [Feature('_M')])
        A = Expression(left, right, ':', gamma, [Feature('_M')])
        return Term(C, A)


    def compose_or_not(self, rule, result, queue):
        """
        Composition operation based on rule.
        :param rule: The rule applied.
        :param result: Result from shift or LC rule application.
        :param queue: Current queue.
        :return: Updated result after composition.
        """
        return result  # Modify as composition rules are defined

    def oracle_ok(self, new_queue, result):
        return True

    # def print_config(self, count, rule, config):
    #    print(f"{count}. {rule}")
    #    print(config)


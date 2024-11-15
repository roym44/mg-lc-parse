"""
Defines the left-corner parser object
"""
from dataclasses import dataclass
from lc_rule import LCRule
from mg import MG

@dataclass
class Expression:
    left: int
    right: int
    tp: str
    features: str # TODO: list[str]
    movers: str

    def __str__(self):
        return f"({self.left}-{self.right}{self.tp} {self.features} {self.movers})"

    def __repr__(self):
        return str(self)


@dataclass
class Term:
    exp: Expression
    output_exp: Expression = None

    def __str__(self):
        if self.output_exp:
            return f"{self.exp} -> {self.output_exp}"
        return f"{self.exp}"

    def __repr__(self):
        return str(self)

@dataclass
class Configuration:
    current_pos: int
    remaining_input: list[str]
    queue: list[Term]

    def get_queue_string(self):
        elements = '\n\t'.join([str(q) for q in self.queue])
        return f"[{elements}]"
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Pos:{self.current_pos},\tInput: {self.remaining_input},\n\tQueue:{self.get_queue_string()}\n"

class LCParser:
    def __init__(self, grammar : MG):
        self.grammar = grammar

    def generate_parsing_rules(self):
        """
        Generate the appropriate rules for the parsing process.
        Based on the lexicon, add the relevant empty-shift rules (e.g., shift([], [=v,c])).
        :return: A list of parsing rules.
        """
        parsing_rules = self.grammar.rules
        empty_string_features = self.grammar.lexicon[""]
        # Add the empty-shift rule for each feature
        for f in empty_string_features:
            # we abuse ':' as a separator between the lexical item and its features
            parsing_rules.append(LCRule(f"shift([]:[{f}])"))
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
        print(f"Parsing the sentence: {input_str}, Using the rules: {parsing_rules}")

        initial_config = Configuration(0, input_str, [])
        stack = [(initial_config, [])]
        results = []

        while stack:
            print(f"--- Stack ---: {stack}")
            config, applied_rules = stack.pop()
            if self.is_success(config):
                results.append((config, applied_rules))
                continue

            # Explore applying each rule to the current configuration
            for rule in parsing_rules:
                # Skip the empty-shift rule if it has already been applied
                if rule.is_empty_shift() and rule in applied_rules:
                    print(f"Skipping rule: {rule} as it has already been applied")
                    continue

                print(f"Applying rule: {rule} to config: {config}")
                new_config = self.apply_rule(rule, config) # step()

                # if we passed the step (i.e., the oracle check passed), add the new configuration to the stack
                if new_config != config:
                    stack.append((new_config, applied_rules + [rule]))

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
        new_pos = config.current_pos
        new_input = config.remaining_input
        new_queue = config.queue
        result : Term = None

        # Apply a shift rule
        if rule.is_empty_shift(): # can be applied at any time
            print("empty-shift")
            fs = rule.inner_part.split(':')[1]
            result = self.empty_shift(fs, config.current_pos)
        elif rule.is_shift(): # based on remaining input
            print("shift")
            result, new_pos, new_input = self.shift(config.remaining_input, config.current_pos)

        # Apply the LC rule to the queue's focus element
        elif rule.is_lc():
            print("lc")
            focus, *remaining_queue = config.queue  # unpack the queue
            result = self.lc(rule, focus)
            new_queue = remaining_queue

        # Apply the inner lc rule; than composeOrNot()
        elif rule.is_comp():
            print("comp")
        else:
            raise ValueError(f"Unknown rule type: {rule}")


        # Update queue with the result if oracle check passes
        if self.oracle_ok(new_queue, result):
            return Configuration(new_pos, new_input, [result] + new_queue)
        # If the oracle fails, return the configuration unchanged for now
        return config


    def empty_shift(self, fs, pos) -> Term:
        result = Expression(pos, pos, '::', fs, '')
        return Term(result)

    def shift(self, input_data, position):
        """
        Shift operation: moves an element from input to the queue.

        :param input_data: List of tokens representing the remaining input.
        :param position: Current position in the input.
        :return: A tuple with the result of shift (new queue element), updated position,
                 and the remaining input after the shift.
        """
        if input_data:  # Ensure there's something to shift
            shifted_token = input_data[0]

            # Create the new queue element as a tuple including position, span, features, etc.
            # TODO: make sure to include the correct features for the token and use it later on
            # For simplicity, assume each token has features associated with it in the lexicon.
            result = (position, position + 1, '::', [shifted_token], [])
            new_position = position + 1
            remaining_input = input_data[1:]

            return result, new_position, remaining_input
        else:
            # If there's nothing left to shift, return None or handle it as needed
            return None, position, input_data

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
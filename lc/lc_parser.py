"""
Defines the lc parser object
"""
from copy import deepcopy
from loguru import logger
from typing import List
from dataclasses import dataclass

from grammar.lexicon import Feature, parse_features
from grammar.mg import MG
from lc.lc_rule import LCRule
from lc.lc_configuration import *

CHAIN_EXPRESSION = Expression(stype=CHAIN_PLACEHOLDER)
Queue = List[Term]

@dataclass
class Configuration:
    current_pos: int
    remaining_input: list[str]
    queue: Queue

    def get_queue_string(self):
        elements = '\t'.join([str(q) for q in self.queue])
        return f"§{elements}§"


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
                parsing_rules.append(LCRule(f"shift([]:{item.features})".replace(' ', '')))
        return parsing_rules


    def parse(self, input_str : list[str], rules : list[LCRule] =None, manual=False):
        """
        Parse the input string using the provided rules.
        This is of course different from the Prolog version, we do not define parse_steps()
        which calls itself recursively, but instead we use a stack to keep track of the configurations.
        That is why we don't keep track of the count per successful derivation, but we can add it if needed.
        :param input_str: The input string to parse as a list of tokens, (e.g., ['John', 'likes', 'Mary'])
        :param rules: Optional rules to use for parsing; if not provided, use the grammar's rules.
        :param manual: Apply rules in a linear, manual order (as in the paper).
        :return: A list of successful configurations and the applied rules.
        """
        parsing_rules = rules or self.generate_parsing_rules()
        self.logger.info(f"Parsing the sentence: {input_str}")
        self.logger.info(f"Using the rules: {parsing_rules}")
        self.logger.info(f"Using the grammar: {self.grammar}")

        initial_config = Configuration(0, input_str, [])
        stack = [(initial_config, [])]
        results = []
        config_count = 0

        while stack:
            config, applied_rules = stack.pop()
            config_count += 1
            count = len(applied_rules)
            self.logger.error(f"Popping {config} No.{config_count} with {count} applied rules {applied_rules}")
            if self.is_success(config):
                results.append((config, applied_rules))
                continue

            if manual:
                if not parsing_rules:
                    continue
                rule = parsing_rules.pop(0)
                new_config = self.apply_rule(rule, config)  # step()
                # if we passed the step (i.e., the oracle check passed), add the new configuration to the stack
                if new_config != config:
                    self.logger.warning(f"{count + 1}. {rule} {new_config.remaining_input}\n{new_config.get_queue_string()}")
                    stack.append((new_config, applied_rules + [rule]))
                    self.log_stack(stack)
                continue

            # Explore applying each rule to the current configuration
            for rule in parsing_rules:
                # Skip the empty-shift rule if it has already been applied
                if rule.is_empty_shift() and rule in applied_rules:
                    self.logger.info(f"Skipping rule: {rule} as it has already been applied!")
                    continue

                if applied_rules and (rule.is_empty_shift() or rule.is_shift()) and \
                        (applied_rules[-1].is_empty_shift() or applied_rules[-1].is_shift()):
                    self.logger.info(f"Skipping rule: {rule} because it follows a shift rule!")
                    continue

                new_config = self.apply_rule(rule, config) # step()
                # if we passed the step (i.e., the oracle check passed), add the new configuration to the stack
                if new_config != config:
                    self.logger.warning(f"{count + 1}. {rule} {new_config.remaining_input}\n{new_config.get_queue_string()}")
                    stack.append((new_config, applied_rules + [rule]))
                    self.log_stack(stack)

        self.logger.info(f"Finished parsing. Found {len(results)} successful derivations, "
                         f"after {config_count} configurations.")
        return results


    def is_success(self, config : Configuration) -> bool:
        """
        Success if input is fully consumed and queue contains a single, valid structure
        :param config: The current parser state.
        :return: True if the configuration is successful, False otherwise.
        """
        if config.remaining_input:
            return False

        if len(config.queue) != 1:
            return False

        # Check span covers the entire input and no movers remain
        final_exp = config.queue[0].exp
        if (final_exp.left != 0) or (final_exp.right != config.current_pos) or (final_exp.movers):
            return False

        # Check that the features match the grammar's start category
        if (len(final_exp.features) != 1) or (final_exp.features[0] != self.grammar.start_category):
            return False

        return True

    def apply_rule(self, rule : LCRule, config : Configuration) -> Configuration:
        """
        Applies a parsing rule to the current configuration.
        :param rule: The rule to apply.
        :param config: The current parser state.
        :return: Updated configuration after applying the rule.
        """
        self.logger.info(f"Got rule: {rule}, config: {config}")
        new_pos, new_input = config.current_pos, config.remaining_input
        updated_queue = config.queue
        result : Term = None

        # ~~~ STEP 1: HANDLE SHIFT/LC RULES ~~~

        # Apply a shift rule - no changes for (pos, input), update (original queue)
        if rule.is_empty_shift(): # can be applied at any time
            # get the features of the empty lexical item
            fs = rule.inner_part.split(':')[1].strip('[]')
            result = self.empty_shift(fs, config.current_pos)

        # Apply a shift rule - new (pos, input), update (original queue)
        elif rule.is_shift(): # based on remaining input
            result, new_pos, new_input = self.shift(config.remaining_input, config.current_pos)

        # Apply the LC rule to the focus - no changes for (pos, input), new (queue)
        elif rule.is_lc():
            if not config.queue:
                self.logger.info("No focus element in the queue! returning same config")
                return config
            focus, *remaining_queue = config.queue  # unpack the queue
            result = self.lc(rule, focus)
            new_pos, new_input = config.current_pos, config.remaining_input
            updated_queue = remaining_queue

        if result is None:
            self.logger.info(f"No result after applying {rule}! returning same config")
            return config

        # ~~~ STEP 2: HANDLE COMPOSITION ~~~

        # Apply the comp rule - no changes for (pos, input), new (queue)
        if rule.is_comp():
            # we have the result waiting for us to complete a prediction
            # we further update the queue (removing top element)
            result, updated_queue = self.comp(rule, result, updated_queue)
            if result is None:
                self.logger.info(f"No result after applying {rule}! returning same config")
                return config

        # insert the new result to the updated queue (after being processed by all the rules)
        new_queue = [result] + updated_queue

        if self.oracle_ok(new_queue, result):
            self.logger.info("Passed the oracle check! returning new config")
            return Configuration(new_pos, new_input, new_queue)

        self.logger.info("Failed the oracle check! returning same config")
        return config


    def empty_shift(self, fs : str, pos : int) -> Term:
        """
        Empty shift operation: moves an empty element to the queue.
        shift(Input,Input,shift([],Fs),Pos,Pos,(Pos,Pos,'::',Fs,[])) :- ([]::Fs).
        :param fs: Features of the empty element, as concatenated string (e.g., '=v,+wh,c')
        :param pos: Current position in the input.
        :return: The new result term.
        """
        self.logger.info(f"fs = [{fs}], pos = {pos}")
        # probably the only usage of parse_features() since we specify features in empty-shift in that format
        features = parse_features(fs)
        result = Expression(pos, pos, '::', features, [])
        return Term(result)

    def shift(self, input_data : list[str], pos : int) -> (Term, int, list[str]):
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
        new_pos = pos + 1
        fs = self.grammar.get_lexicon_item(W).features

        result = Expression(pos, new_pos, '::', fs, [])
        return Term(result), new_pos, new_input

    def lc(self, rule : LCRule, focus : Term) -> Term:
        """
        Apply the appropriate LC rule to the focus element.
        :param rule: The LC rule to apply.
        :param focus: The focus element in the queue.
        :return: The new result term; None if the rule does not apply.
        """
        self.logger.info(f"focus={focus}")
        # Make sure the focus is a single expression
        if not focus.is_single():
            return None
        exp = focus.exp

        # Apply the appropriate LC rule to the focus element
        if rule.lc_rule == 'lc1':
            if rule.inner_part == 'merge1':
                return self.lc1_merge1(exp)
            elif rule.inner_part == 'merge2':
                return self.lc1_merge2(focus)
            elif rule.inner_part == 'merge3':
                return self.lc1_merge3(focus)
            elif rule.inner_part == 'move1':
                return self.lc1_move1(exp)
            elif rule.inner_part == 'move2':
                return self.lc1_move2(focus)
        elif rule.lc_rule == 'lc2':
            if rule.inner_part == 'merge2':
                return self.lc2_merge2(exp)
            elif rule.inner_part == 'merge3':
                return self.lc2_merge3(exp)

    def lc1_merge1(self, B : Expression) -> Term:
        """
        s (Left, Mid, '::', [=F|Gamma], []),
        ( t (Mid, Right, _,  [F], Alphas) -> st (Left, Right, ':', Gamma, Alphas) ))
        """
        # Validate match for lc1(merge1)
        if (B.stype != '::') or (not B.features) or (not B.features[0].is_selector()) or (B.movers):
            return None

        left, mid, right = B.left, B.right, UNKNOWN_POS

        # Extract the feature being selected
        f = B.features[0].feature  # take 'f' from '=f'
        gamma = B.features[1:]  # Remaining features after '=F'
        alphas = [CHAIN_EXPRESSION]

        C = Expression(mid, right, UNKNOWN_STYPE, [Feature(f)], alphas)
        A = Expression(left, right, ':', gamma, alphas)
        return Term(C, A)

    def lc1_move1(self, B : Expression) -> Term:
        """
        (Mid, Right, ':', [+F|Fs], Movers0),
        (Left, Right, ':', Fs, Movers) ) :- select((Left,Mid,[-F]), Movers0, Movers).
        """
        # Validate match for lc1(move1)
        if (not B.movers) or (not B.features[0].is_licensor()) or (not B.movers[0].features[0].is_licensee()):
            return None

        mid, right = B.left, B.right
        f = B.features[0].feature # take 'f' from '+f'
        fs = B.features[1:] # remaining features after '+f'

        # find the licensee in the movers list
        mover = None
        movers0 = B.movers
        for m in movers0:
            if (m.right == mid) and (m.features[0].feature == f) and (m.features[0].is_licensee()):
                mover = m
                movers0.remove(m)
                break
        if mover is None:
            return None

        A = Expression(mover.left, right, ':', fs, movers0)
        return Term(A)


    def lc2_merge2(self, C : Expression) -> Term:
        """
        t (Left, Mid, _, [F], Iotas),
        ( s ( Mid, Right, ':',  [=F|Gamma], Alphas) -> ts (Left, Right, ':', Gamma, Movers) ))
        """
        # TODO: Validate match for lc2_merge2?

        left, mid, right = C.left, C.right, UNKNOWN_POS

        # Extract the feature being selected
        f = C.features[0].feature  # take 'f'
        iotas = C.movers
        gamma = [Feature('v')] # TODO: should be taken from a rule in the grammar
        alphas = [CHAIN_EXPRESSION]
        movers = alphas + iotas

        B = Expression(mid, right, ':', [Feature(f, "=")] + gamma, alphas)
        A = Expression(left, right, ':', gamma, movers)
        return Term(B, A)

    def lc2_merge3(self, C : Expression) -> Term:
        """
        t (Left0, Right0, _, [F,-G|Fs], Iotas) ,
        ( s (Left, Right, T, [=F|Gamma], Alphas) -> s, t (Left, Right, ':', Gamma, Movers) ) )
        """
        # Validate match for lc2(merge3)
        if (len(C.features) < 2) or (not C.features[1].is_licensee()):
            return None

        left0, right0 = C.left, C.right

        # Extract the feature being selected
        f = C.features[0].feature  # take 'f'
        G = C.features[1].feature  # take 'G' from '-G'
        iotas = C.movers
        gamma = [FEATURE_PLACEHOLDER]
        alphas = [CHAIN_EXPRESSION]

        # we don't put alphas in the movers of B, based on the steps 8-9 in the example derivation
        B = Expression(UNKNOWN_POS, UNKNOWN_POS, UNKNOWN_STYPE, [Feature(f, "=")] + gamma, [])
        t = Expression(left0, right0, ':', [Feature(G, "-")], iotas)
        # here we don't put alphas in movers since we have [t] as the next in the chain
        A = Expression(UNKNOWN_POS, UNKNOWN_POS, ':', gamma, [t])
        return Term(B, A)


    def comp(self, rule : LCRule, result : Term, queue : Queue) -> (Term, Queue):
        self.logger.info(f"result={result}")
        self.logger.info(f"queue={queue}")

        if rule.comp_rule == 'c':
            # Make sure the result is (exp)
            if not result.is_single():
                return None, queue
            exp = result.exp
            return self.c(exp, queue)

        # Make sure the result is (exp -> exp)
        if result.is_single():
            return None, queue

        if rule.comp_rule == 'c1':
            return self.c1(result, queue)
        elif rule.comp_rule == 'c2':
            return self.c2(result, queue)
        elif rule.comp_rule == 'c3':
            return self.c3(result, queue)



    def select(self, exp : Expression, queue : Queue, left=True) -> Term:
        for term in queue:
            if term.is_single():
                continue
            # found on left side
            if left and term.exp == exp:
                return term
            # found on right side
            if term.output_exp == exp:
                return term
        return None


    def c(self, A : Expression, queue : Queue) -> (Term, Queue):
        """
        % compose completed result
        composeOrNot(R,A,c(R),B,Queue0,Queue) :- select((A -> B), Queue0, Queue),
        """
        # look for (A' => B) in the queue
        APrimetB = deepcopy(self.select(A, queue, left=True))
        if APrimetB is None:
            return None, queue
        queue.remove(APrimetB)
        APrime, B = APrimetB.exp, APrimetB.output_exp
        APrime.match(A)
        B.match(APrime)

        return Term(B), queue

    def c1(self, AtB : Term, queue : Queue) -> (Term, Queue):
        """
        % forward composition
        composeOrNot(R,(A -> B),c1(R),(A -> C),Queue0,Queue) :- select((B -> C), Queue0, Queue),
        """
        A, B = AtB.exp, AtB.output_exp

        # look for (B => C) in the queue
        BtC = deepcopy(self.select(B, queue, left=True))
        if BtC is None:
            return None, queue

        queue.remove(BtC)
        C = BtC.output_exp

        # add (A => C)
        AtC = Term(A, C)
        return AtC, queue

    def c3(self, BtC : Term, queue : Queue) -> (Term, Queue):
        """
        % forward and backward composition
        composeOrNot(R,(B -> C),c3(R),(A -> D),Queue0,Queue) :-
            select((A -> B), Queue0, Queue1),
            select((C -> D), Queue1, Queue),
        """
        B, C = BtC.exp, BtC.output_exp

        # ! general note: deepcopy is necessary, so we don't match original features in the queue !

        # look for (A => B') in the queue
        AtBPrime = deepcopy(self.select(B, queue, left=False))
        if AtBPrime is None:
            return None, queue
        queue.remove(AtBPrime)
        A, BPrime = AtBPrime.exp, AtBPrime.output_exp
        B.match(BPrime)
        A.match(B)

        # look for (C' => D) in the queue
        CPrimetD = deepcopy(self.select(C, queue, left=True))
        if CPrimetD is None:
            return None, queue
        queue.remove(CPrimetD)
        CPrime, D = CPrimetD.exp, CPrimetD.output_exp
        C.match(B)
        C.match(CPrime)
        D.match(C)

        # add (A => D)
        AtD = Term(A, D)
        return AtD, queue


    def oracle_ok(self, new_queue, result):
        return True

    # def print_config(self, count, rule, config):
    #    print(f"{count}. {rule}")
    #    print(config)


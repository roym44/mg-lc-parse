"""
Defines the left-corner parser object
"""
from lc_rule import LCRule
from mg import MG

class Configuration:
    def __init__(self, position, input_data, queue):
        self.position = position
        self.input_data = input_data
        self.queue = queue

    def __str__(self):
        return f"Position:{self.position}\nInput: {self.input_data}\nQueue:{self.queue}"

class LCParser:
    def __init__(self, grammar : MG):
        self.grammar = grammar

    def generate_parsing_rules(self, rules):
        """
        Generate the appropriate rules for the parsing process.
        1. If no rules are provided, use the grammar's rules.
        2. Based on the lexicon, add the relevant empty-shift rules (e.g., shift([], [=v,c])).
        :param rules: Optional rules; if not provided, use the grammar's rules.
        :return:
        """
        parsing_rules = rules or self.grammar.rules
        empty_string_features = self.grammar.lexicon[""]
        # Add the empty-shift rule for each feature
        for f in empty_string_features:
            parsing_rules.append(LCRule(f"shift([], [{f}])"))
        return parsing_rules


    def parse(self, input_str : list[str], rules : list[LCRule] =None):
        """
        Parse the input string using the provided rules.
        This is of course different from the Prolog version, we do not define parse_steps()
        which calls itself recursively, but instead we use a stack to keep track of the configurations.
        That is why we don't keep track of the count per successful derivation, but we can add it if needed.
        :param input_str: The input string to parse.
        :param rules: Optional rules to use for parsing; if not provided, use the grammar's rules.
        :return: A list of successful configurations and the applied rules.
        """
        parsing_rules = self.generate_parsing_rules(rules)
        print(f"Parsing the sentence: {input_str}, Using the rules: {parsing_rules}")

        initial_config = Configuration(0, input_str, [])
        stack = [(initial_config, [])]
        results = []

        while stack:
            config, applied_rules = stack.pop()
            if self.is_success(config):
                results.append((config, applied_rules))
                continue

            # Explore applying each rule to the current configuration; functions as step()
            for rule in parsing_rules:
                new_config = self.apply_rule(rule, config)
                if new_config and self.oracle_ok(new_config):
                    stack.append((new_config, applied_rules + [rule]))

        return results


    def is_success(self, config : Configuration):
        return True

    def apply_rule(self, rule : LCRule, config : Configuration):
        """
        Applies a parsing rule to the current configuration.
        :param rule: The rule to apply (e.g., shift, lc1, lc2).
        :param config: The current state of the parser as (position, input, queue).
        :return: Updated configuration after applying the rule.
        """
        position, input_data, queue = config

        # Check for shift or LC rule
        if rule == "shift":
            result, new_position, new_input = self.shift(input_data, position)
            updated_queue = queue
        else:
            # Apply the LC rule to the queue's focus element
            focus, *remaining_queue = queue # unpack the queue
            result = self.apply_lc_rule(rule, focus)
            new_position = position
            new_input = input_data
            updated_queue = remaining_queue

        # Compose or not based on the result
        final_result = self.compose_or_not(rule, result, updated_queue)

        # Update queue with the result if oracle check passes
        if self.oracle_ok(updated_queue, final_result):
            return new_position, new_input, [final_result] + updated_queue
        else:
            # If the oracle fails, return the configuration unchanged for now
            return config

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

    def oracle_ok(self, queue, result):
        """
        Oracle check for the result to ensure it's valid.
        :param queue: Current queue after applying a rule.
        :param result: Resulting element to check with the oracle.
        :return: True if the oracle check passes, False otherwise.
        """
        return True  # Modify with actual oracle conditions

    # def print_config(self, count, rule, config):
    #    print(f"{count}. {rule}")
    #    print(config)

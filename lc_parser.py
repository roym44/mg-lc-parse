"""
Defines the left-corner parser object
"""
from mg import MG

class LCParser:
    def __init__(self, grammar : MG):
        self.grammar = grammar

    def parse(self, input_str : list[str], rules=None):
        rules = rules or self.grammar.rules
        print(f"Parsing the sentence: {input_str}, Using the rules: {rules}")

        initial_config = (0, input_str, [])
        return self.parse_steps(initial_config, rules)

    def parse_steps(self, initial_config, rules):
        config = initial_config
        remaining_rules = rules[:]
        count = 0

        while remaining_rules:
            if self.success(config) and not remaining_rules:
                print("Parsing successful.")
                return True

            # Apply the next rule in the sequence
            rule = remaining_rules.pop(0)
            config = self.step(rule, config)
            count += 1

            # Print current configuration for debugging
            self.print_config(count, rule, config)

        # If rules are exhausted and success condition not met
        print("Parsing incomplete or unsuccessful.")
        return False

    def success(self, config):
        pass

    def step(self, rule, config):
        return config

    def print_config(self, count, rule, config):
        position, input_data, queue = config
        print(f"{count}. {rule}")
        print(f"Input: {input_data}")
        print(f"Queue: {queue}")

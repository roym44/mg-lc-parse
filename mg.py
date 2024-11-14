"""
Defines the minimalist grammar object
"""
import json

from lc_rule import LCRule


class MG:
    def __init__(self, input_file):
        """
        Initializes the grammar object with the given input file
        :param input_file: The grammar description file in JSON format
        """
        with open(input_file, 'r') as file:
            data = json.load(file)
        self.lexicon = data.get('lexicon', {})
        self.rules : list[LCRule] = []
        self.start_category = data.get('start_category')

        self.parse_rules(data.get('rules', []))

    def parse_rules(self, rules: list[str]):
        """
        Parses the given rules into a list of LCRule objects
        :param rules: The list of rules to parse
        :return: The list of parsed LCRule objects
        """
        for r in rules:
            self.rules.append(LCRule(r))

    def __str__(self):
        return f"Lexicon: {self.lexicon}\nRules: {self.rules}"


if __name__ == '__main__':
    g1 = MG('input/g1.json')
    print(g1)
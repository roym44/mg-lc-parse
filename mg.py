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
        self.lexicon : dict[str, str] = {} # a mapping between an element and its features
        self.rules : list[LCRule] = [] # a list of LC rules
        self.start_category : str = ''
        self.link_relations : dict[str, str] = {}

        # Parse the JSON file
        with open(input_file, 'r') as file:
            data = json.load(file)
        self.parse_json(data)

        # Compute the link relations
        self.compute_link_relations()

    def parse_json(self, data):
        """
        Parses the given JSON data into the grammar object
        :param data: The JSON data to parse
        """
        self.lexicon = data.get('lexicon')

        rules = data.get('rules')
        for r in rules:
            self.rules.append(LCRule(r))

        self.start_category = data.get('start_category')


    def __str__(self):
        return f"Lexicon: {self.lexicon}\nRules: {self.rules}"

    def compute_link_relations(self):
        pass


if __name__ == '__main__':
    g1 = MG('input/g1.json')
    print(g1)
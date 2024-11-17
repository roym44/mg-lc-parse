"""
Defines the minimalist grammar object
"""
import json

from grammar.lexicon import LexItem, Feature
from lc.lc_rule import LCRule

class MG:
    def __init__(self, input_file):
        """
        Initializes the grammar object with the given input file
        :param input_file: The grammar description file in JSON format
        """
        self.lexicon : list[LexItem] = [] # a mapping between an element and its features
        self.rules : list[LCRule] = [] # a list of LC rules
        self.start_category : Feature = None
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
        for k, v in data.get('lexicon').items():
            for f in v: # empty lexical item can have multiple sets of features
                self.lexicon.append(LexItem(k, f))

        for r in data.get('rules'):
            self.rules.append(LCRule(r))

        self.start_category = Feature(data.get('start_category'))

    def get_lexicon_item(self, element):
        """
        Returns the lexical item with the given element
        :param element: The element to search for
        :return: The lexical item with the given element; None if not found
        """
        for lex in self.lexicon:
            if lex.element == element:
                return lex
        return None

    def __str__(self):
        return f"Lexicon: {self.lexicon}\nRules: {self.rules}"

    def compute_link_relations(self):
        pass


if __name__ == '__main__':
    g1 = MG('../input/g1.json')
    print(g1)
"""
Defines the minimalist grammar object
"""
import json
from dataclasses import dataclass

from lc_rule import LCRule



@dataclass
class Feature:
    prefix: str
    feature: str

    def is_selector(self):
        return self.prefix == '='

    def is_licensor(self):
        return self.prefix == '+'

    def is_licensee(self):
        return self.prefix == '-'

    def __str__(self):
        return f"{self.prefix}{self.feature}"

    def __repr__(self):
        return str(self)

def parse_features(features) -> list[Feature]:
    fs_list = []
    for fs in features.split(','):
        # Check if the feature has a prefix
        prefix, feature = (fs[0], fs[1:]) if fs.startswith(('=', '+', '-')) else ('', fs[0])
        fs_list.append(Feature(prefix, feature))
    return fs_list

class LexItem:

    def __init__(self, element : str, features : str):
        """
        Initializes the lexical item with the given element and features.
        :param element: The element  (e.g., 'Aca')
        :param features: The features as a concatenated string (e.g., '=v,+wh,c')
        """
        self.element : str = element
        self.features : list[Feature] = parse_features(features)

    def __str__(self):
        return f"{repr(self.element)} :: {self.features}"

    def __repr__(self):
        return str(self)


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

        self.start_category = Feature('', data.get('start_category'))


    def __str__(self):
        return f"Lexicon: {self.lexicon}\nRules: {self.rules}"

    def compute_link_relations(self):
        pass


if __name__ == '__main__':
    g1 = MG('input/g1.json')
    print(g1)
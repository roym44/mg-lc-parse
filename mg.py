"""
Defines the minimalist grammar object
"""
import json


class MG:
    def __init__(self, input_file):
        """
        Initializes the grammar object with the given input file
        :param input_file: The grammar description file in JSON format
        """
        with open(input_file, 'r') as file:
            data = json.load(file)
        self.lexicon = data.get('lexicon', {})
        self.rules = data.get('rules', [])

    def __str__(self):
        return f"Lexicon: {self.lexicon}\nRules: {self.rules}"
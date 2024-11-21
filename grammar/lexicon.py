from dataclasses import dataclass


@dataclass
class Feature:
    feature: str
    prefix: str = ''

    def is_selector(self):
        return self.prefix == '='

    def is_licensor(self):
        return self.prefix == '+'

    def is_licensee(self):
        return self.prefix == '-'

    def is_variable(self):
        """
        When building new Terms in LC rules, some features are left as variables.
        """
        return self.prefix == '_'

    def __str__(self):
        return f"{self.prefix}{self.feature}"

    def __repr__(self):
        return str(self)


def parse_features(features) -> list[Feature]:
    fs_list = []
    for fs in features.split(','):
        # Check if the feature has a prefix
        prefix, feature = (fs[0], fs[1:]) if fs.startswith(('=', '+', '-')) else ('', fs[0])
        fs_list.append(Feature(feature, prefix=prefix))
    return fs_list


class LexItem:
    def __init__(self, element: str, features: str):
        """
        Initializes the lexical item with the given element and features.
        :param element: The element  (e.g., 'Aca')
        :param features: The features as a concatenated string (e.g., '=v,+wh,c')
        """
        self.element: str = element
        self.features: list[Feature] = parse_features(features)

    def get_last_index(self, f: Feature):
        try:
            return len(self.features) - 1 - self.features[::-1].index(f)
        except ValueError:
            return -1

    def __str__(self):
        return f"{repr(self.element)} :: {self.features}"

    def __repr__(self):
        return str(self)

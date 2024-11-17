from dataclasses import dataclass
from grammar.lexicon import Feature

UNKNOWN_POS = 99 # replaces '_' position from the paper, will be printed as '_'
UNKNOWN_STYPE = '.'
FEATURE_PLACEHOLDER = Feature('_Fs')
CHAIN_PLACEHOLDER = '_M'

@dataclass
class Expression:
    left: int = UNKNOWN_POS # left position
    right: int = UNKNOWN_POS # right position
    stype: str  = UNKNOWN_STYPE # : or ::
    features: list[Feature] = None
    movers: list['Expression'] = None

    def __str__(self):
        if self.stype == '_M':
            return f"{self.stype}"
        left_str = '_' if self.left == UNKNOWN_POS else self.left
        right_str = '_' if self.right == UNKNOWN_POS else self.right
        exp_str = f"({left_str}-{right_str}{self.stype} {self.features}"

        if self.movers:
            for m in self.movers:
                exp_str += f",{m}"
        exp_str += ')'
        return exp_str

    def __repr__(self):
        return str(self)

    def stype_equal(self, other):
        return (self.stype == other.stype) or \
        (self.stype == UNKNOWN_STYPE) or (other.stype == UNKNOWN_STYPE)

    def pos_equal(self, pos1, pos2):
        return (pos1 == pos2) or (pos1 == UNKNOWN_POS) or (pos2 == UNKNOWN_POS)

    def features_equal(self, other):
        return (self.features == other.features) or \
            (self.features[0] == FEATURE_PLACEHOLDER) or (other.features[0] == FEATURE_PLACEHOLDER)


    def is_chain_place(self):
        return self.stype == CHAIN_PLACEHOLDER

    def movers_equal(self, other):
        # TODO: make sure to handle empty movers list?
        return (self.movers == other.movers) or \
            (self.movers[0].is_chain_place()) or (other.movers[0].is_chain_place())

    def __eq__(self, other):
        return self.pos_equal(self.left, other.left) and \
            self.pos_equal(self.right, other.right) and \
            self.stype_equal(other) and \
            self.features_equal(other) and \
            self.movers_equal(other)

    def get_feat_place_index(self):
        for i, f in enumerate(self.features):
            if f == FEATURE_PLACEHOLDER:
                return i
        return -1

    def has_feature_placeholder(self):
        return self.get_feat_place_index() > -1

    def get_mover_place_index(self):
        for i, m in enumerate(self.movers):
            if m.is_chain_place():
                return i
        return -1
    def has_mover_placeholder(self):
        return self.get_mover_place_index() > -1

    def match(self, other, feat=True, mover=True):
        self.left = other.left if self.left == UNKNOWN_POS else self.left
        self.right = other.right if self.right == UNKNOWN_POS else self.right
        if self.has_feature_placeholder() and feat:
            self.features = self.features[:self.get_feat_place_index()] + other.features
        if self.has_mover_placeholder() and mover:
            self.movers = self.movers[:self.get_mover_place_index()] + other.movers



@dataclass
class Term:
    exp: Expression
    output_exp: Expression = None

    def is_single(self) -> bool:
        return self.output_exp is None

    def __str__(self):
        if self.output_exp:
            return f"{self.exp} => {self.output_exp}"
        return f"{self.exp}"

    def __repr__(self):
        return str(self)





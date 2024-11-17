from dataclasses import dataclass
from grammar.lexicon import Feature

UNKNOWN_POS = 99 # replaces '_' position from the paper
UNKNOWN_STYPE = '.'

@dataclass
class Expression:
    left: int = UNKNOWN_POS # left position
    right: int = UNKNOWN_POS # right position
    stype: str  = UNKNOWN_STYPE # : or ::
    features: list[Feature] = None
    movers: list['Expression'] = None # TODO: maybe it's actually a list of Expressions? that's a chain?

    merged_exp: 'Expression' = None

    def __str__(self):
        if self.stype == '_M':
            return f"{self.stype}"
        left_str = '_' if self.left == UNKNOWN_POS else self.left
        right_str = '_' if self.right == UNKNOWN_POS else self.right

        exp_str = f"({left_str}-{right_str}{self.stype} {self.features} {self.movers})"

        if self.merged_exp:
            return f"{exp_str},{self.merged_exp}"
        return exp_str

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.left == other.left and \
            self.right == other.right and \
            (self.stype == other.stype or self.stype == UNKNOWN_STYPE or other.stype == UNKNOWN_STYPE) and \
            self.features == other.features and \
            self.movers == other.movers


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





from dataclasses import dataclass
from grammar.lexicon import Feature

UNKNOWN_STYPE = '.'

@dataclass
class Expression:
    left: int # left position
    right: int # right position
    stype: str # : or ::
    features: list[Feature]
    movers: list[Feature]

    def __str__(self):
        return f"({self.left}-{self.right}{self.stype} {self.features} {self.movers})"

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





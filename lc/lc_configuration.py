from dataclasses import dataclass
from grammar.lexicon import Feature


@dataclass
class Expression:
    left: int # left position
    right: int # right position
    stype: str # : or ::
    features: list[Feature]
    movers: list[Feature]

    def __str__(self):
        return f"({self.left}-{self.right}{self.stype} {self.features} {self.movers})"


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



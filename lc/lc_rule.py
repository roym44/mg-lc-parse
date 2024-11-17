"""
Defines the LCRule class, which is used to represent a rule in the LC grammar.
There are three types of rules:
1. shift (empty/regular)
2. lc1/lc2 that wrap merge/move rules
3. c/c1/c2/c3 that wrap any other rule
"""


class LCRule:
    def __init__(self, rule: str):
        self.raw_rule : str = rule
        self.comp_rule : str = ''
        self.lc_rule : str = ''
        self.inner_part : str = ''
        self.parse_rule()

    def parse_rule(self):
        rule_str = self.raw_rule

        if rule_str == 'shift':
            self.lc_rule = rule_str
            return

        # check if the rule is a comp rule
        split = rule_str.split('(')
        if rule_str.startswith('c'):
            self.comp_rule, self.lc_rule = split[0], split[1].rstrip(')')
            if len(split) > 2:
                self.inner_part = split[2].rstrip(')')
        else:
            self.lc_rule = split[0]
            self.inner_part = split[1].rstrip(')')

    def is_shift(self) -> bool:
        return self.lc_rule == 'shift'

    def is_empty_shift(self) -> bool:
        """
        An empty-shift rule is a shift rule that operates on the empty string (epsilon), e.g., shift([]),
        this has no dependency on the input string, and can be applied at any time.
        This is opposed to a shift rule that operates on a non-empty lexical item, e.g., shift([Aca]),
        which is taken from the remaining input during parsing.
        """
        return self.is_shift() and self.inner_part.startswith('[]')

    def is_lc(self) -> bool:
        return not self.is_shift()

    def is_comp(self) -> bool:
        return self.comp_rule != ''

    def set_inner_part(self, inner_part):
        """
        Sets the inner part of the rule.
        This is mainly used for SHIFT rules, since we want to store the features of the shift:
        e.g., shift([], [=v,c]) will have the inner part as '[], [=v,c]'
        """
        self.inner_part = inner_part

    def __str__(self):
        return self.raw_rule

    def __repr__(self):
        # return f"{self.raw_rule} § comp={self.comp_rule} lc={self.lc_rule} inner={self.inner_part}"
        return str(self)

if __name__ == '__main__':
    lcr1 = LCRule('shift')
    print(repr(lcr1))
    print(lcr1.is_shift())
    print(lcr1.is_lc())
    print(lcr1.is_comp())

    lcr2 = LCRule('lc1(merge1)')
    print(repr(lcr2))
    print(lcr2.is_shift())
    print(lcr2.is_lc())
    print(lcr2.is_comp())

    lcr3 = LCRule('c1(lc2(merge2))')
    print(repr(lcr3))
    print(lcr3.is_shift())
    print(lcr3.is_lc())
    print(lcr3.is_comp())

    lcr4 = LCRule('c(shift)')
    print(repr(lcr4))
    print(lcr4.is_shift())
    print(lcr4.is_lc())
    print(lcr4.is_comp())

    lcr5 = LCRule('shift([], [=v,c])')
    print(repr(lcr5))
    print(lcr5.is_shift())
    print(lcr5.is_lc())
    print(lcr5.is_comp())

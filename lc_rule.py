"""
Defines the LCRule class, which is used to represent a rule in the LC grammar.
There are three types of rules:
1. shift
2. lc1/lc2 that wrap merge/move
3. c/c1/c2/c3 that wrap the rest of the rules
"""


class LCRule:
    def __init__(self, rule: str):
        self.raw_rule = rule
        self.comp_rule = None
        self.lc_rule = None
        self.inner_part = None
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

    def is_shift(self):
        return self.lc_rule == 'shift'

    def is_lc(self):
        return not self.is_shift()

    def is_comp(self):
        return self.comp_rule is not None

    def __repr__(self):
        return self.__str__()
        # return f"{self.raw_rule} § comp={self.comp_rule} lc={self.lc_rule} inner={self.inner_part}"

    def __str__(self):
        return self.raw_rule

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

from lc.lc_rule import LCRule
from time import sleep

def test_g1_input1_manual(parser, input1):
    rules1 = [
        LCRule('shift([]:[=v,c])'),
        LCRule('lc1(merge1)'),
        LCRule('shift'),
        LCRule('c1(lc2(merge2))'),
        LCRule('shift'),
        LCRule('c1(lc1(merge1))'),
        LCRule('shift'),
        LCRule('lc2(merge3)'),
        LCRule('shift([]:[=v,+wh,c])'),
        LCRule('lc1(merge1)'),
        LCRule('shift'),
        LCRule('c3(lc2(merge2))'),
        LCRule('c(shift)'),
        LCRule('c(lc1(move1))'),
    ]
    test_g1_input(parser, input1, rules=rules1, manual=True)

def test_g1_input2_manual(parser, input2):
    rules2 = [
        LCRule('shift([]:[=v,c])'),
        LCRule('lc1(merge1)'),
        LCRule('shift'),
        LCRule('c1(lc2(merge2))'),
        LCRule('shift'),
        LCRule('c1(lc1(merge1))'),
        LCRule('c(shift)'),
    ]
    test_g1_input(parser, input2, rules=rules2, manual=True)

def test_g1_input3_manual(parser, input3):
    rules3 = [
        LCRule('shift([]:[=v,c])'),
        LCRule('lc1(merge1)'),
        LCRule('shift'),
        LCRule('c1(lc2(merge2))'),
        LCRule('shift'),
        LCRule('c1(lc1(merge1))'),
        LCRule('c(shift)'),
        LCRule('lc2(merge2)'),
        LCRule('shift'),
        LCRule('c1(lc1(merge1))'),
        LCRule('shift([]:[=v,c])'),
        LCRule('c1(lc1(merge1))'),
        LCRule('shift'),
        LCRule('c1(lc2(merge2))'),
        LCRule('shift'),
        LCRule('c1(lc1(merge1))'),
        LCRule('c(shift)')
    ]
    test_g1_input(parser, input3, rules=rules3, manual=True)

def test_g1_input(parser, inp, rules=None, manual=False):
    results = parser.parse(inp, rules=rules, manual=manual)
    sleep(0.1)
    print(f"Results: {results}")
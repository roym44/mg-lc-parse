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
    results = parser.parse(input1, rules=rules1, manual=True)
    sleep(0.1)
    print(f"Results: {results}")


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
    results = parser.parse(input2, rules=rules2, manual=True)
    sleep(0.1)
    print(f"Results: {results}")


def test_g1_input1(parser, input1):
    rules1 = [
        LCRule('shift([]:[=v,c])'),
        LCRule('shift([]:[=v,+wh,c])'),
        LCRule('shift'),
        LCRule('lc1(merge1)'),
        LCRule('c1(lc2(merge2))'),
        LCRule('c1(lc1(merge1))'),
        LCRule('lc2(merge3)'),
        LCRule('c3(lc2(merge2))'),
        LCRule('c(shift)'),
        LCRule('c(lc1(move1))')
    ]
    results = parser.parse(input1, rules=None)
    sleep(0.1)
    print(f"Results: {results}")

def test_g1_input(parser, inp):
    results = parser.parse(inp)
    sleep(0.1)
    print(f"Results: {results}")
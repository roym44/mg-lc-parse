from time import sleep

from grammar.mg import MG
from lc.lc_rule import LCRule
from lc.lc_parser import LCParser


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

def test_g1_input2(parser, input2):
    results = parser.parse(input2, rules=None)
    sleep(0.1)
    print(f"Results: {results}")


def test_g1():
    g1 = MG('input/g1.json')
    parser = LCParser(g1)
    input1 = ['Aca', 'knows', 'what', 'Bibi', 'likes']
    # test_g1_input1(parser, input1)
    # test_g1_input1_manual(parser, input1)

    input2 = ['Bibi', 'likes', 'Aca']
    test_g1_input2(parser, input2)
    # test_g1_input2_manual(parser, input2)


if __name__ == '__main__':
    print('Welcome to the MG Left Corner Parser!')
    test_g1()

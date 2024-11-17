from time import sleep

from grammar.mg import MG
from lc.lc_rule import LCRule
from lc.lc_parser import LCParser

def test_g1():
    g1 = MG('input/g1.json')
    parser = LCParser(g1)
    input1 = ['Aca', 'knows', 'what', 'Bibi', 'likes']
    rules1 = [
        LCRule('shift([]:[=v,c])'),
        LCRule('lc1(merge1)'),
        LCRule('shift'),
        LCRule('c1(lc2(merge2))'),
        LCRule('shift'),
        LCRule('c1(lc1(merge1))'),
        LCRule('shift'),
        LCRule('lc2(merge3)'),
        LCRule('shift([]:[=v,+wh,c])')
    ]

    # shift([]:[=v,c]), lc1(merge1), shift
    # result=(1-99: [=d, v] [_M]) => (0-99: [v] [_M])
    results = parser.parse(input1, rules=rules1, manual=True)
    sleep(0.1)
    print(f"Results: {results}")


if __name__ == '__main__':
    print('Welcome to the MG Left Corner Parser!')
    test_g1()
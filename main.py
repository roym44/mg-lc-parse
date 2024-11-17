from time import sleep

from grammar.mg import MG
from lc.lc_rule import LCRule
from lc.lc_parser import LCParser

def test_g1_manual():
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
        LCRule('shift([]:[=v,+wh,c])'),
        LCRule('lc1(merge1)'),
        LCRule('shift'),
        LCRule('c3(lc2(merge2))'),
        LCRule('c(shift)'),
        LCRule('c(lc1(move1))'),
    ]
    """
    Config: Pos:5,	Input: [],	Queue:§(0-5: [c])§, 
    Rules: [shift([]:[=v,c]), lc1(merge1), shift, c1(lc2(merge2)), shift, c1(lc1(merge1)), shift, 
    lc2(merge3), shift([]:[=v,+wh,c]), lc1(merge1), shift, c3(lc2(merge2)), c(shift), c(lc1(move1))]
    """
    results = parser.parse(input1, rules=rules1, manual=True)
    sleep(0.1)
    print(f"Results: {results}")

def test_g1():
    g1 = MG('input/g1.json')
    parser = LCParser(g1)
    input1 = ['Aca', 'knows', 'what', 'Bibi', 'likes']
    results = parser.parse(input1)
    sleep(0.1)
    print(f"Results: {results}")


if __name__ == '__main__':
    print('Welcome to the MG Left Corner Parser!')
    # test_g1_manual()
    test_g1()
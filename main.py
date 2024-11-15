from time import sleep

from mg import MG
from lc_rule import LCRule
from lc_parser import LCParser

def test_g1():
    g1 = MG('input/g1.json')
    parser = LCParser(g1)
    input1 = ['Aca', 'knows', 'what', 'Bibi', 'likes']
    rules1 = [
        LCRule('shift([]:[=v,c])')
    ]

    results = parser.parse(input1, rules1)
    sleep(0.1)
    print(f"Results: {results}")


if __name__ == '__main__':
    print('Welcome to the MG Left Corner Parser!')
    test_g1()
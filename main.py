from time import sleep

from grammar.mg import MG
from lc.lc_parser import LCParser
from test_g1 import *


def test_g1(manual=False):
    g1 = MG('input/g1.json') # suitable for input1 and input2
    parser = LCParser(g1)
    input1 = ['Aca', 'knows', 'what', 'Bibi', 'likes']
    input2 = ['Bibi', 'likes', 'Aca']
    input3 = ['Aca', 'likes', 'Bibi', 'and', 'Bibi', 'likes', 'Aca']
    if manual:
        test_g1_input1_manual(parser, input1)
        test_g1_input2_manual(parser, input2)
        test_g1_input3_manual(parser, input3)
    else:
        test_g1_input(parser, input1)
        test_g1_input(parser, input2)

if __name__ == '__main__':
    print('Welcome to the MG Left Corner Parser!')
    test_g1(manual=True)

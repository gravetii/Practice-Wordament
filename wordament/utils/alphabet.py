from PyQt4 import QtGui, QtCore
import random
from random import randint
_points = {'': 0,
          'a':1,
          'b':2,
          'c':3,
          'd':3,
          'e':1,
          'f':4,
          'g':4,
          'h':4,
          'i':2,
          'j':4,
          'k':3,
          'l':3,
          'm':4,
          'n':2,
          'o':2,
          'p':2,
          'q':2,
          'r':2,
          's':2,
          't':2,
          'u':4,
          'v':5,
          'w':5,
          'x':6,
          'y':5,
          'z':6,
          'in':6,
          'es':12,
          'pr':6, }

_alphabet = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 't'] * 6 + \
            ['s'] * 12 + \
            ['a', 'e', 'i', 'o'] * 12 + \
            ['u'] * 10 + \
            ['v', 'w', 'x', 'y', 'z'] * 3

class Alphabet(object):
    def __init__(self, letter):
        self.letter = letter
        '''image path wrt to index.py'''
        self.image = 'utils/images/alphabet/' + self.letter + '.png'
        self.points = _points[self.letter]
        self.weight = -1
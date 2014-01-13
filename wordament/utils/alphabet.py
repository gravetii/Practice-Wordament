from PyQt4 import QtGui, QtCore
import random
from random import randint


_points = {'': 0,
          'a':1,
          'b':3,
          'c':3,
          'd':2,
          'e':1,
          'f':4,
          'g':2,
          'h':4,
          'i':1,
          'j':8,
          'k':5,
          'l':1,
          'm':3,
          'n':1,
          'o':1,
          'p':3,
          'q':10,
          'r':1,
          's':1,
          't':1,
          'u':1,
          'v':4,
          'w':4,
          'x':8,
          'y':4,
          'z':10,
          'in':6,
          'es':12,
          'pr':6, }

_alphabet = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'p', 'q', 'r', 't'] * 9 + \
            ['n', 's'] * 15 + \
            ['a', 'e', 'i', 'o', 'u'] * 25 + \
            ['v', 'w', 'x', 'y', 'z'] * 6

class Alphabet(object):
    def __init__(self, letter):
        self.letter = letter
        '''image path wrt to index.py'''
        self.image = 'utils/images/alphabet'  + '/' + self.letter + '.png'
        self.points = _points[self.letter]
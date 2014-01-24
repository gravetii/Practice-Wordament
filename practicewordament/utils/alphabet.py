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
          'z':10,}

_alphabet = ['e'] * 25 + \
            ['t', 'a', 'o', 'i'] * 20 + \
            ['n', 's', 'h', 'r'] * 15 + \
            ['d', 'l', 'c', 'u', 'm'] * 12 + \
            ['w', 'f', 'g', 'y', 'p', 'b'] * 10 + \
            ['v', 'k', 'j', 'x', 'q', 'z'] * 5

class Alphabet(object):
    def __init__(self, letter):
        self.letter = letter
        '''image path wrt to index.py'''
        self.image = 'utils/images/alphabet'  + '/' + self.letter + '.png'
        self.points = _points[self.letter]
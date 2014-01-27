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

alphabet = ['e'] * 25 + \
           ['t', 'a', 'o', 'i'] * 20 + \
           ['n', 's', 'h', 'r'] * 15 + \
           ['d', 'l', 'c', 'u', 'm'] * 12 + \
           ['w', 'f', 'g', 'y', 'p', 'b'] * 10 + \
           ['v', 'k', 'j', 'x', 'q', 'z'] * 5

class Alphabet(object):
    def __init__(self, letter):
        self.letter = letter
        '''image path wrt to practicewordament.py'''
        self.image = 'utils/images/alphabet'  + '/' + self.letter + '.png'
        self.points = _points[self.letter]

class Game:
    def __init__(self, grid, grid_words_list, sum_total_points, total_points):
        self.grid = [[None for _ in range(4)] for _ in range(4)]
        for r in range(4):
            for c in range(4):
                self.grid[r][c] = grid[r][c]
        self.grid_words_list = grid_words_list
        self.sum_total_points = sum_total_points
        self.total_points = total_points
        self.user_words_list = []
        self.sum_user_points = 0
    
class GameQueue:
    def __init__(self):
        self._list = []
        self._len = 0

    def push(self, obj):
        self._list.append(obj)
        self._len += 1
    
    def empty(self):
        return self._len == 0

    @property
    def size(self):
        return self._len

    def pop(self):
        if self.empty(): return None
        obj = self._list.pop(0)
        self._len -= 1
        return obj
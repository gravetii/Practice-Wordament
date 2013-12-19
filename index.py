import time
import sys
from pytrie import StringTrie as trie
import cPickle as pickle
import string
from PyQt4 import QtGui, QtCore

MIN_LENGTH = 3
alphabet = list(string.ascii_lowercase)

'''sample grid'''
grid = [['y', 'g', 'n', 'a'], ['a', 'o', 'n', 't'], ['r', 's', 'i', 'e'], ['a', 'e', 't', 'a']]
T = None

points = {'': 0,
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

class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(300, 300, 500, 350)
        self.setWindowTitle('Wordament')
        self.initUI()
    
    def initUI(self):
        self.textbox = QtGui.QLineEdit(self)
        self.textResult = QtGui.QTextEdit(self)
        self.textResult.setReadOnly(True)
        self.btn = QtGui.QPushButton('Send', self)
        self.btn.clicked.connect(self.onClick)
        self.textbox.move(20, 20)
        self.btn.move(180, 20)
        self.textResult.move(20, 80)
        
    def onClick(self, event):
        text = str(self.textbox.text())
        self.textbox.clear()
        if text in thelist:
            self.textResult.append(text + ': ' + str(total_points[text]))
        
def create_trie():
    global T
    if T is None:
        file_read = open('trie_dump.pkl', 'r+')
        T = pickle.load(file_read)

def is_word(word):
    return T.longest_prefix(word) == word

def is_prefix(prefix):
    a = T.keys(prefix = prefix)
    return len(a) is not 0

def get_neighbors(point):
    (x, y) = (point[0], point[1])
    pre_list = [(x-1,y-1), (x-1,y), (x-1,y+1), (x,y-1), (x,y+1), (x+1,y-1), (x+1,y), (x+1,y+1)]
    post_list = []
    for neighbor in pre_list:
        if neighbor[0] < 0 or neighbor[0] < 0 or neighbor[0] > 3 or neighbor[0] > 3 or \
        neighbor[1] < 0 or neighbor[1] < 0 or neighbor[1] > 3 or neighbor[1] > 3: continue
        else: post_list.append(neighbor)
    return post_list

def find_words(point, prefix, visited, total_points):
    visited[point[0]][point[1]] = True
    word = prefix + grid[point[0]][point[1]]
    if not is_prefix(word):
        return
    if len(word) >= MIN_LENGTH and is_word(word) and word not in thelist:
        thelist.append(word)
    total_points[word] = total_points[prefix] + total_points[grid[point[0]][point[1]]]
    for neighbor in get_neighbors(point):
        if not visited[neighbor[0]][neighbor[1]]:
            _visited = [[False for r in range(4)] for c in range(4)]
            for p in range(4):
                for q in range(4):
                    _visited[p][q] = visited[p][q]
            find_words(neighbor, word, _visited, total_points)

def main():
    create_trie()
    global thelist
    thelist = []
    global total_points
    total_points = points

    for i in range(4):
        for j in range(4):
            visited = [[False for p in range(4)] for q in range(4)]
            find_words((i, j), '', visited, total_points)
    print thelist
    '''create the UI here'''
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__': main()
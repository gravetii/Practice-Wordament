import sys
import cPickle as pickle
import random
from PyQt4 import QtGui, QtCore
from threading import Thread
from utils import alphabet

MIN_LENGTH = 3
T = None
grid = [[None for row in range(4)] for col in range(4)]
 
grid_words_list = None

class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.initUI()
        self.move(300, 150)

    def initUI(self):
        layout = QtGui.QGridLayout(self)
        for row in range(4):
            for col in range(4):
                label = QtGui.QLabel(self)
                letter = grid[row][col]
                pixmap = QtGui.QPixmap(letter.image)
                label.setPixmap(pixmap.scaled(100, 100))
                layout.addWidget(label, row, col)
        self.textbox = QtGui.QLineEdit(self)
        self.resultbox = QtGui.QTextEdit(self)
        self.resultbox.setReadOnly(True)
        self.btn = QtGui.QPushButton('Send', self)
        self.btn.clicked.connect(self.print_result)
        layout.addWidget(self.textbox, 5, 0, 1, 3)
        layout.addWidget(self.resultbox, 6, 0, 3, 3)
        layout.addWidget(self.btn, 5, 3)

    def print_result(self, event):
        text = str(self.textbox.text())
        self.textbox.clear()
        if text in grid_words_list:
            self.resultbox.append(text + ': ' + str(total_points[text]))
            print text
            
    def confirm_exit(self):
        dialog = QtGui.QMessageBox.question(self, 'Really quit?', 'Are you sure you want to quit?',
                                buttons = QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
        if dialog == QtGui.QMessageBox.Yes:
            self.destroy()
        elif dialog == QtGui.QMessageBox.No:
            return
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.confirm_exit()
            return

        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            text = str(self.textbox.text())
            self.textbox.clear()
            if text is None or text not in grid_words_list:
                return
            self.resultbox.append(text + ': ' + str(total_points[text]))
            print text
        
def create_trie():
    global T
    if T is None:
        trie_read = open('utils/trie_dump.pkl', 'r+')
        T = pickle.load(trie_read)

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
        if neighbor[0] < 0 or neighbor[0] > 3 or neighbor[1] < 0 or neighbor[1] > 3: continue
        post_list.append(neighbor)
    return post_list

def find_words(point, prefix, visited, total_points):
    visited[point[0]][point[1]] = True
    word = prefix + grid[point[0]][point[1]].letter
    if not is_prefix(word):
        return
    if len(word) >= MIN_LENGTH and is_word(word) and word not in grid_words_list:
        grid_words_list.append(word)
    total_points[word] = total_points[prefix] + total_points[grid[point[0]][point[1]].letter]
    for neighbor in get_neighbors(point):
        if not visited[neighbor[0]][neighbor[1]]:
            _visited = [[False for r in range(4)] for c in range(4)]
            for p in range(4):
                for q in range(4):
                    _visited[p][q] = visited[p][q]
            find_words(neighbor, word, _visited, total_points)


class InitThread(Thread):
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        create_trie()
        global grid_words_list
        grid_words_list = []
        global total_points
        total_points = alphabet._points

def main():
    global grid
    for r in range(4):
        for c in range(4):
            random_letter = random.choice(alphabet._alphabet)
            letter = alphabet.Alphabet(random_letter)
            grid[r][c] = letter
    '''create the UI here'''
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()

    init_thread = InitThread()
    init_thread.start()
    init_thread.join()
    
    print 'trie created'
    for i in range(4):
        for j in range(4):
            visited = [[False for p in range(4)] for q in range(4)]
            find_words((i, j), '', visited, total_points)
    print grid_words_list
    print len(grid_words_list)
    sys.exit(app.exec_())

if __name__ == '__main__': main()
import sys
import time
import cPickle as pickle
import random
from PyQt4 import QtGui, QtCore
from threading import Thread
from utils import alphabet

MIN_LENGTH = 3
T = None
grid = [[None for row in range(4)] for col in range(4)]
grid_words_list = None
user_words_list = None
total_points = None
trie_thread = None
UNIT_GAME_TIME = 60

'''flag to check if a game is running or not'''
IS_GAME_RUNNING = False


class Window(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.create_menu()
        self.initUI()
        self.move(350, 100)
        self.setFixedSize(425, 575)
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('WORDAMENT!')
        self.setWindowTitle('WORDAMENT')
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
        self.current_timer = None

    def initUI(self):
        layout = QtGui.QBoxLayout(0)
        skin_path = 'utils/images/skins/' + str(random.choice([1, 2, 3])) + '.jpg'
        pixmap = QtGui.QPixmap(skin_path)
        self.label = QtGui.QLabel(self)
        self.label.setPixmap(pixmap.scaled(425, 575))
        layout.addWidget(self.label)
        self.setCentralWidget(self.label)

    def gameUI(self):
        self.statusbar.clearMessage()
        self.main_widget = QtGui.QWidget()
        layout = QtGui.QGridLayout()
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
        self.main_widget.setLayout(layout)
        self.setCentralWidget(self.main_widget)
        self.textbox.setFocus()
        
        '''allow the user to play the game for 1 minute'''
        self.start_timer()
    
    def start_timer(self):
        if self.current_timer:
            self.current_timer.stop()
            self.current_timer.deleteLater()
        self.current_timer = QtCore.QTimer()
        self.current_timer.timeout.connect(self.stop_game)
        self.current_timer.setSingleShot(True) 
        self.current_timer.start(1000 * UNIT_GAME_TIME)

    def stop_game(self):
        self.set_game_running(False)
        print 'TIME UP!'
        self.textbox.setReadOnly(True)
        self.statusbar.showMessage('TIME UP!')
        '''wait for 2 seconds immediately after the game ends before displaying result to user'''
        time.sleep(2)
        self.display_user_result()
    
    def display_user_result(self):
        user_words_score = 0
        global user_words_list
        for word in user_words_list:
            user_words_score += total_points[word]
        user_words_count = str(len(user_words_list))
        grid_result = get_grid_all()
        text_1 = '- Total words: ' + str(user_words_count) + ' out of ' + grid_result[0]
        text_2 = '- Total score: ' + str(user_words_score) + ' out of ' + grid_result[2]
        dialog = QtGui.QMessageBox.information(self, 'Game over!', text_1 + '\n' + text_2 + '\n\nStart new game?',  
                                    buttons = QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
        if dialog == QtGui.QMessageBox.Yes: self.create_new_game()

    def create_menu(self):
        new_game_action = QtGui.QAction('&New Game', self)
        new_game_action.setShortcut('Ctrl+N')
        new_game_action.triggered.connect(self.create_new_game)
        exit_action = QtGui.QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        about_action = QtGui.QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(new_game_action)
        file_menu.addAction(exit_action)
        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(about_action)

    def create_new_game(self):
        if self.is_game_running():
            dialog = QtGui.QMessageBox.question(self, 'Really quit?',
                                                'Quit this game and start a new one?',
                                buttons = QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
            if dialog == QtGui.QMessageBox.No:
                return

        create_random_grid()

        global user_words_list
        user_words_list = []
        global total_points
        total_points = alphabet._points
        global grid_words_list
        grid_words_list = []
        
        if trie_thread.is_alive():
            trie_thread.join()

        '''get the list of meaningful words from this grid'''
        get_all_grid_words()

        result_list = get_grid_all()
        print 'Total number of words: ' + result_list[0]
        print 'Words List: ' + result_list[1]
        print 'Total sum of grid words: ' + result_list[2]
        self.set_game_running(True)
        self.statusbar.showMessage('Starting new game...')
        
        '''wait for 1 seconds before showing the grid to the user'''
        time.sleep(1)
        self.gameUI()
    
    def show_about(self):
        dialog_text = 'Written by Sandeep Dasika in a desperate attempt to do something productive.'
        dialog = QtGui.QMessageBox.information(self, "About", dialog_text, 
                                    buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.Ok)
        if dialog == QtGui.QMessageBox.Ok:
            return

    def print_result(self):
        text = str(self.textbox.text()).strip().lower()
        self.textbox.clear()
        if text == '': return
        
        '''move cursor to the beginning of resultbox'''
        cursor = self.resultbox.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start)
        self.resultbox.setTextCursor(cursor)

        if text in grid_words_list and text not in user_words_list:
            result_string = text + ': ' + str(total_points[text])
            formatted_string = QtCore.QString("<font color='green'>%1</font>").arg(result_string)
            self.resultbox.insertHtml(formatted_string)
            self.resultbox.insertPlainText('\n')
            user_words_list.append(text)
            print text
        elif text in user_words_list:
            self.resultbox.insertHtml(QtCore.QString("<font color='orange'>%1</font>").arg(text))
            self.resultbox.insertPlainText('\n')
        elif text not in grid_words_list:
            self.resultbox.insertHtml(QtCore.QString("<font color='red'>%1</font>").arg(text))
            self.resultbox.insertPlainText('\n')

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return and self.is_game_running():
            self.print_result()

    def set_game_running(self, flag):
        global IS_GAME_RUNNING
        IS_GAME_RUNNING = flag
        
    def is_game_running(self):
        return IS_GAME_RUNNING
    
    def closeEvent(self, event):
        if self.is_game_running():
            dialog_text = 'Really quit?', 'Quit current game?'
        else:
            dialog_text = 'Really exit?', 'Are you sure you want to exit?'
        dialog = QtGui.QMessageBox.question(self, dialog_text[0], dialog_text[1],
                                buttons = QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
        if dialog == QtGui.QMessageBox.Yes:
            event.accept()
        elif dialog == QtGui.QMessageBox.No:
            event.ignore()
            return

class TrieThread(Thread):
    def __init__(self, name):
        Thread.__init__(self, name=name)
    
    def run(self):
        global T
        if T is None:
            trie_read = open('utils/trie_dump.pkl', 'r+')
            T = pickle.load(trie_read)
        print 'trie created'

def is_word(word):
    return T.longest_prefix(word, False) == word

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
    total_points[word] = total_points[prefix] + total_points[grid[point[0]][point[1]].letter]
    if len(word) >= MIN_LENGTH and is_word(word) and word not in grid_words_list:
        grid_words_list.append(word)
    for neighbor in get_neighbors(point):
        if not visited[neighbor[0]][neighbor[1]]:
            _visited = [[False for r in range(4)] for c in range(4)]
            for p in range(4):
                for q in range(4):
                    _visited[p][q] = visited[p][q]
            find_words(neighbor, word, _visited, total_points)

def create_random_grid():
    global grid
    for r in range(4):
        for c in range(4):
            random_letter = random.choice(alphabet._alphabet)
            letter = alphabet.Alphabet(random_letter)
            grid[r][c] = letter

def get_all_grid_words():
    for i in range(4):
        for j in range(4):
            visited = [[False for r in range(4)] for c in range(4)]
            global total_points
            find_words((i, j), '', visited, total_points)

def get_grid_all():
    sum_total_points = 0
    for each_word in grid_words_list:
        sum_total_points += total_points[each_word]
    return (str(len(grid_words_list)), str(grid_words_list), str(sum_total_points))

def main():
    global trie_thread
    trie_thread = TrieThread('trie loading thread')
    trie_thread.start()
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__': main()
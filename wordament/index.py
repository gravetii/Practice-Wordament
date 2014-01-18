import sys
import time
import cPickle as pickle
import random
from PyQt4 import QtGui, QtCore, phonon
from threading import Thread
from utils import alphabet

MIN_LENGTH = 3
T = None
UNIT_GAME_TIME = 10

'''flag to check if a game is running or not'''
IS_GAME_RUNNING = False

class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.create_menu()
        self.initUI()
        self.initPhonon()
        self.initAll()
        self.current_timer = None
        self.timer_display_thread = None

    def initUI(self):
        layout = QtGui.QBoxLayout(0)
        skin_path = 'utils/images/skins/' + str(random.choice([1, 2, 3])) + '.jpg'
        pixmap = QtGui.QPixmap(skin_path)
        self.label = QtGui.QLabel(self)
        self.label.setPixmap(pixmap.scaled(425, 575))
        layout.addWidget(self.label)
        self.setCentralWidget(self.label)
        self.move(350, 100)
        self.setFixedSize(425, 575)
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('WORDAMENT!')
        self.setWindowTitle('WORDAMENT')
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)

    def initPhonon(self):
        self.mediaObject = phonon.Phonon.MediaObject(self)
        self._audioOutput = phonon.Phonon.AudioOutput(phonon.Phonon.MusicCategory)
        phonon.Phonon.createPath(self.mediaObject, self._audioOutput)
        
    def initAll(self):
        self.grid = [[None for row in range(4)] for col in range(4)]
        self.grid_words_list = []
        self.user_words_list = []
        self.sum_total_points = 0
        self.sum_user_points = 0
        self.total_points = {'':0, }
        
    def gameUI(self):
        self.current_grid_words_action.setDisabled(True)
        self.statusbar.clearMessage()
        self.lcd = QtGui.QLCDNumber()
        main_widget = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        for row in range(4):
            for col in range(4):
                label = QtGui.QLabel(self)
                letter = self.grid[row][col]
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
        layout.addWidget(self.lcd, 6, 3, 3, 1)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        self.textbox.setFocus()
        '''allow the user to play the game for UNIT_GAME_TIME seconds'''
        self.start_timer()
    
    def start_timer(self):
        if self.current_timer:
            self.current_timer.stop()
            self.current_timer.deleteLater()
        self.current_timer = QtCore.QTimer()
        self.current_timer.timeout.connect(self.stop_game)
        self.current_timer.setSingleShot(True) 
        self.current_timer.start(1000 * UNIT_GAME_TIME)
        '''display the timer to the user in self.lcd'''
        self.timer_display_thread = TimerDisplayThread(self.lcd)
        self.timer_display_thread.setDaemon(True)
        self.timer_display_thread.start()

    def stop_game(self):
        if self.enable_sound.isChecked():
            self.mediaObject.setCurrentSource(phonon.Phonon.MediaSource('utils/sounds/alarm.wav'))
            self.mediaObject.play()
        self.set_game_running(False)
        print 'TIME UP!'
        self.textbox.setReadOnly(True)
        self.statusbar.showMessage('TIME UP!')
        
        dialog = QtGui.QMessageBox.information(self, 'Game over!', 'TIME UP!', 
                                    buttons = QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel)
        if dialog == QtGui.QMessageBox.Ok or dialog == QtGui.QMessageBox.Cancel:
            self.display_user_result()
        self.current_grid_words_action.setEnabled(True)

    def display_user_result(self):
        text_1 = 'TOTAL WORDS - ' + str(len(self.user_words_list)) + ' out of ' + str(len(self.grid_words_list))
        text_2 = 'TOTAL SCORE - ' + str(self.sum_user_points) + ' out of ' + str(self.sum_total_points)
        self.statusbar.showMessage(text_1 + ' | ' + text_2)

    def create_menu(self):
        new_game_action = QtGui.QAction('&New Game', self)
        new_game_action.setShortcut('Ctrl+N')
        new_game_action.triggered.connect(self.start_new_game)
        exit_action = QtGui.QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        about_action = QtGui.QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        self.current_grid_words_action = QtGui.QAction('&List of words', self)
        self.current_grid_words_action.setDisabled(True)
        self.current_grid_words_action.triggered.connect(self.show_current_grid_words)
        self.enable_sound = QtGui.QAction('&Enable sounds', self, checkable=True)
        self.enable_sound.setChecked(True)
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(new_game_action)
        file_menu.addAction(self.current_grid_words_action)
        file_menu.addAction(exit_action)
        options_menu = menubar.addMenu('&Options')
        options_menu.addAction(self.enable_sound)
        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(about_action)
    
    def show_current_grid_words(self):
        '''this is clickable only after the game is over'''
        self.resultbox.clear()
        for word in self.grid_words_list:
            formatted_word = word + ': ' + str(self.total_points[word])
            if word in self.user_words_list:
                '''print in green'''
                self.print_colored_text(formatted_word, 'green')
            else:
                '''print in black'''
                self.print_colored_text(formatted_word, 'black')
        self.current_grid_words_action.setDisabled(True)
        self.display_user_result()

    def start_new_game(self):
        if self.is_game_running():
            dialog = QtGui.QMessageBox.question(self, 'Really quit?',
                                                'Quit this game and start a new one?',
                                buttons = QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
            if dialog == QtGui.QMessageBox.No:
                return
        self.initAll()
        self.create_random_grid()
        if trie_thread.is_alive():
            trie_thread.join()

        '''get the list of meaningful words from this grid'''
        self.get_all_grid_words()

        print 'Total number of words: ' + str(len(self.grid_words_list))
        print 'Words List: ' + str(self.grid_words_list)
        print 'Total sum of grid words: ' + str(self.sum_total_points)
        self.set_game_running(True)
        self.statusbar.showMessage('Starting new game...')
        
        '''wait for 1 second before showing the grid to the user'''
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

        if text in self.grid_words_list and text not in self.user_words_list:
            result_string = text + ': ' + str(self.total_points[text])
            self.print_colored_text(result_string, 'green')
            self.user_words_list.append(text)
            self.sum_user_points += self.total_points[text]
            print text
        elif text in self.user_words_list:
            self.print_colored_text(text, 'orange')
        elif text not in self.grid_words_list:
            self.print_colored_text(text, 'red')
            
    def print_colored_text(self, text, color):
        color_string = "<font color = '" + color + "'>%1</font>"
        formatted_string = QtCore.QString(color_string).arg(text)
        self.resultbox.insertHtml(formatted_string)
        self.resultbox.insertPlainText('\n')

    def keyPressEvent(self, event):
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
        
    def is_word(self, word):
        global T
        return T.longest_prefix(word, False) == word
    
    def is_prefix(self, prefix):
        a = T.keys(prefix = prefix)
        return len(a) is not 0
    
    def get_neighbors(self, point):
        (x, y) = (point[0], point[1])
        pre_list = [(x-1,y-1), (x-1,y), (x-1,y+1), (x,y-1), (x,y+1), (x+1,y-1), (x+1,y), (x+1,y+1)]
        post_list = []
        for neighbor in pre_list:
            if neighbor[0] < 0 or neighbor[0] > 3 or neighbor[1] < 0 or neighbor[1] > 3: continue
            post_list.append(neighbor)
        return post_list
    
    def find_words(self, point, prefix, visited):
        visited[point[0]][point[1]] = True
        word = prefix + self.grid[point[0]][point[1]].letter
        if not self.is_prefix(word):
            return
        self.total_points[word] = self.total_points[prefix] + self.total_points[self.grid[point[0]][point[1]].letter]
        if len(word) >= MIN_LENGTH and self.is_word(word) and word not in self.grid_words_list:
            self.grid_words_list.append(word)
            self.sum_total_points += self.total_points[word]
        for neighbor in self.get_neighbors(point):
            if not visited[neighbor[0]][neighbor[1]]:
                _visited = [[False for r in range(4)] for c in range(4)]
                for p in range(4):
                    for q in range(4):
                        _visited[p][q] = visited[p][q]
                self.find_words(neighbor, word, _visited)
                
    def create_random_grid(self):
        for r in range(4):
            for c in range(4):
                random_letter = random.choice(alphabet._alphabet)
                letter = alphabet.Alphabet(random_letter)
                self.grid[r][c] = letter
                self.total_points[random_letter] = letter.points

    def get_all_grid_words(self):
        for i in range(4):
            for j in range(4):
                visited = [[False for r in range(4)] for c in range(4)]
                self.find_words((i, j), '', visited)

class TrieThread(Thread):
    def __init__(self, name=None):
        Thread.__init__(self, name=name)

    def run(self):
        global T
        if T is None:
            trie_read = open('utils/trie_dump.pkl', 'r+')
            T = pickle.load(trie_read)
        print 'trie created'
        trie_read.close()

class TimerDisplayThread(Thread):
    def __init__(self, lcd, name=None):
        Thread.__init__(self, name=name)
        self.lcd = lcd

    def run(self):
        self.show_countdown_timer()
        
    def show_countdown_timer(self):
        try:
            for k in range(UNIT_GAME_TIME-1, -1, -1):
                self.lcd.display(k)
                time.sleep(1)
        except RuntimeError:
            return

def main():
    global trie_thread
    trie_thread = TrieThread('trie loading thread')
    trie_thread.setDaemon(True)
    trie_thread.start()
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__': main()
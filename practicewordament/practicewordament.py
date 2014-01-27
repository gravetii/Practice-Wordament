#!/usr/bin/env python

import sys
import time
import cPickle as pickle
import random
from PyQt4 import QtGui, QtCore, phonon
from threading import Thread
from utils.utils import *

MIN_LENGTH = 3
T = None
UNIT_GAME_TIME = 60
MIN_WORDS = 60
IS_APP_RUNNING = False

class GameThread(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.parent = parent
        self.setDaemon(False)
        self.start()

    def run(self):
        if trie_thread.is_alive():
            trie_thread.join()
        global IS_APP_RUNNING
        while True:
            while IS_APP_RUNNING and self.parent.game_queue.size >= 2:
                time.sleep(1)
            if not IS_APP_RUNNING: break
            self.create_random_grid()
            new_game = Game(self.grid, self.grid_words_list, self.sum_total_points, self.total_points)
            self.parent.game_queue.push(new_game)
            self.parent.statusbar.clearMessage()

    def is_word(self, word):
        global T
        return T.longest_prefix(word, False) == word
    
    def is_prefix(self, prefix):
        a = T.keys(prefix = prefix)
        return len(a) != 0
    
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
                _visited = [[False for _ in range(4)] for _ in range(4)]
                for p in range(4):
                    for q in range(4):
                        _visited[p][q] = visited[p][q]
                self.find_words(neighbor, word, _visited)
                
    def initAll(self):
        self.grid = [[None for _ in range(4)] for _ in range(4)]
        self.grid_words_list = []
        self.user_words_list = []
        self.sum_total_points = 0
        self.sum_user_points = 0
        self.total_points = {'':0}

    def create_random_grid(self):
        grid_total_words = 0
        while grid_total_words <= MIN_WORDS:
            self.initAll()
            for r in range(4):
                for c in range(4):
                    random_letter = random.choice(alphabet)
                    letter = Alphabet(random_letter)
                    self.grid[r][c] = letter
                    self.total_points[random_letter] = letter.points
            grid_total_words = self.get_all_grid_words()

    def get_all_grid_words(self):
        for i in range(4):
            for j in range(4):
                visited = [[False for _ in range(4)] for _ in range(4)]
                self.find_words((i, j), '', visited)
        return len(self.grid_words_list)

class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        global IS_APP_RUNNING
        IS_APP_RUNNING = True
        self.game_queue = GameQueue()
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Please wait...initializing...')
        GameThread(self)
        self.UILayout = QtGui.QBoxLayout(0)
        self.gameLayout = QtGui.QGridLayout()
        self.create_menu()
        self.initUI()
        self.initPhonon()
        self.current_timer = None
        self.timer_display_thread = None
        self.current_game = None
        self.game_running = False

    def initUI(self):
        skin_path = 'utils/images/skins/' + str(random.choice([1, 2, 3])) + '.jpg'
        pixmap = QtGui.QPixmap(skin_path)
        self.label = QtGui.QLabel(self)
        self.label.setPixmap(pixmap.scaled(425, 575))
        self.UILayout.addWidget(self.label)
        self.setCentralWidget(self.label)
        self.move(350, 100)
        self.setFixedSize(425, 575)
        self.setWindowTitle('WORDAMENT')
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
        
    def remove_initUI(self):
        for c in reversed(range(self.UILayout.count())):
            widget = self.UILayout.takeAt(c).widget()
            if widget != None: 
                widget.deleteLater()

    def initPhonon(self):
        self.mediaObject = phonon.Phonon.MediaObject(self)
        self._audioOutput = phonon.Phonon.AudioOutput(phonon.Phonon.MusicCategory)
        phonon.Phonon.createPath(self.mediaObject, self._audioOutput)
        
    def gameUI(self):
        self.current_grid_words_action.setDisabled(True)
        self.statusbar.clearMessage()
        self.lcd = QtGui.QLCDNumber()
        main_widget = QtGui.QWidget()
        for row in range(4):
            for col in range(4):
                label = QtGui.QLabel(self)
                letter = self.current_game.grid[row][col]
                pixmap = QtGui.QPixmap(letter.image)
                label.setPixmap(pixmap.scaled(100, 100))
                self.gameLayout.addWidget(label, row, col)
        self.textbox = QtGui.QLineEdit(self)
        self.resultbox = QtGui.QTextEdit(self)
        self.resultbox.setReadOnly(True)
        self.btn = QtGui.QPushButton('Send', self)
        self.btn.clicked.connect(self.print_result)
        self.gameLayout.addWidget(self.textbox, 5, 0, 1, 3)
        self.gameLayout.addWidget(self.resultbox, 6, 0, 3, 3)
        self.gameLayout.addWidget(self.btn, 5, 3)
        self.gameLayout.addWidget(self.lcd, 6, 3, 3, 1)
        main_widget.setLayout(self.gameLayout)
        self.setCentralWidget(main_widget)
        self.textbox.setFocus()
        '''allow the user to play the game for UNIT_GAME_TIME seconds'''
        self.start_timer()
    
    def remove_gameUI(self):
        for c in reversed(range(self.gameLayout.count())):
            widget = self.gameLayout.takeAt(c).widget()
            if widget != None: 
                widget.deleteLater()

    def start_timer(self):
        if self.current_timer:
            self.current_timer.stop()
            self.current_timer.deleteLater()
        self.current_timer = QtCore.QTimer()
        self.current_timer.timeout.connect(self.stop_game)
        self.current_timer.setSingleShot(True) 
        self.current_timer.start(1000 * (UNIT_GAME_TIME))
        '''display the timer to the user in self.lcd'''
        self.timer_display_thread = TimerDisplayThread(self.lcd)

    def stop_game(self):
        if self.enable_sound_action.isChecked():
            self.mediaObject.setCurrentSource(phonon.Phonon.MediaSource('utils/sounds/alarm.wav'))
            self.mediaObject.play()
        self.game_running = False
        self.textbox.setReadOnly(True)
        self.statusbar.showMessage('Game over')
        dialog = QtGui.QMessageBox.information(self, 'Game over!', 'TIME UP!', 
                                    buttons = QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel)
        if dialog == QtGui.QMessageBox.Ok or dialog == QtGui.QMessageBox.Cancel:
            self.display_user_result()
        self.current_grid_words_action.setEnabled(True)
        if self.show_current_grid_words_action.isChecked():
            self.show_current_grid_words()

    def display_user_result(self):
        text_1 = 'TOTAL WORDS - ' + str(len(self.current_game.user_words_list)) + ' out of ' + \
                                                                str(len(self.current_game.grid_words_list))
        text_2 = 'TOTAL SCORE - ' + str(self.current_game.sum_user_points) + ' out of ' + \
                                                                str(self.current_game.sum_total_points)
        self.move_cursor()
        self.print_colored_text(text_1, 'green')
        self.print_colored_text(text_2, 'green')
        self.resultbox.insertPlainText('\n')

    def create_menu(self):
        new_game_action = QtGui.QAction('&New Game', self)
        new_game_action.setShortcut('Ctrl+N')
        new_game_action.triggered.connect(self.start_new_game)
        exit_action = QtGui.QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        about_action = QtGui.QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        self.current_grid_words_action = QtGui.QAction('&List all words', self)
        self.current_grid_words_action.setShortcut('Ctrl+L')
        self.current_grid_words_action.setDisabled(True)
        self.current_grid_words_action.triggered.connect(self.show_current_grid_words)
        self.enable_sound_action = QtGui.QAction('&Enable sounds', self, checkable=True)
        self.enable_sound_action.setChecked(True)
        self.show_current_grid_words_action = QtGui.QAction('&Show all possible words after game', self, checkable=True)
        self.show_current_grid_words_action.setChecked(True)
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(new_game_action)
        file_menu.addAction(self.current_grid_words_action)
        file_menu.addAction(exit_action)
        options_menu = menubar.addMenu('&Options')
        options_menu.addAction(self.enable_sound_action)
        options_menu.addAction(self.show_current_grid_words_action)
        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(about_action)
    
    def show_current_grid_words(self):
        '''this is clickable only after the game is over'''
        self.resultbox.clear()
        for word in self.current_game.grid_words_list:
            formatted_word = word + ': ' + str(self.current_game.total_points[word])
            if word in self.current_game.user_words_list:
                self.print_colored_text(formatted_word, 'green')
            else:
                self.print_colored_text(formatted_word, 'black')
        self.current_grid_words_action.setDisabled(True)
        self.display_user_result()

    def start_new_game(self):
        if self.game_running:
            dialog = QtGui.QMessageBox.question(self, 'Really quit?',
                                                'Quit this game and start a new one?',
                                buttons = QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
            if dialog == QtGui.QMessageBox.No:
                return

        self.game_running = True
        self.statusbar.showMessage('Starting new game...')
        if self.UILayout.count() != 0:
            self.remove_initUI()
        if self.gameLayout.count() != 0:
            self.remove_gameUI()
        self.current_game = None
        while self.current_game == None:
            self.current_game = self.game_queue.pop()
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

        self.move_cursor()

        if text in self.current_game.grid_words_list and text not in self.current_game.user_words_list:
            result_string = text + ': ' + str(self.current_game.total_points[text])
            self.print_colored_text(result_string, 'green')
            self.current_game.user_words_list.append(text)
            self.current_game.sum_user_points += self.current_game.total_points[text]
        elif text in self.current_game.user_words_list:
            self.print_colored_text(text, 'orange')
        elif text not in self.current_game.grid_words_list:
            self.print_colored_text(text, 'red')
            
    def print_colored_text(self, text, color):
        color_string = "<font color = '" + color + "'>%1</font>"
        formatted_string = QtCore.QString(color_string).arg(text)
        self.resultbox.insertHtml(formatted_string)
        self.resultbox.insertPlainText('\n')

    def move_cursor(self, to_start=True):
        cursor = self.resultbox.textCursor()
        if to_start:
            cursor.movePosition(QtGui.QTextCursor.Start)
        else:
            cursor.movePosition(QtGui.QTextCursor.End)
        self.resultbox.setTextCursor(cursor)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return and self.game_running:
            self.print_result()
    
    def closeEvent(self, event):
        if self.game_running:
            dialog_text = 'Really quit?', 'Quit current game?'
        else:
            dialog_text = 'Really exit?', 'Are you sure you want to exit?'
        dialog = QtGui.QMessageBox.question(self, dialog_text[0], dialog_text[1],
                                buttons = QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
        if dialog == QtGui.QMessageBox.Yes:
            global IS_APP_RUNNING
            IS_APP_RUNNING = False
            event.accept()
        elif dialog == QtGui.QMessageBox.No:
            event.ignore()
            return

class TrieThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.setDaemon(False)
        self.start()

    def run(self):
        global T
        if T == None:
            trie_read = open('utils/trie_dump.pkl', 'r+')
            T = pickle.load(trie_read)
        trie_read.close()

class TimerDisplayThread(Thread):
    def __init__(self, lcd):
        Thread.__init__(self)
        self.lcd = lcd
        self.setDaemon(True)
        self.start()

    def run(self):
        self.show_countdown_timer()
        
    def show_countdown_timer(self):
        try:
            for k in range(UNIT_GAME_TIME, -1, -1):
                self.lcd.display(k)
                time.sleep(1)
        except RuntimeError:
            return
    
def main():
    global trie_thread
    trie_thread = TrieThread()
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__': main()
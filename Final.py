import os
import ctypes as ct
import sys
import csv
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class ScrollLabel(QScrollArea):
 
    # constructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
 
        # making widget resizable
        self.setWidgetResizable(True)
 
        # making qwidget object
        content = QWidget(self)
        self.setWidget(content)
 
        # vertical box layout
        lay = QVBoxLayout(content)
 
        # creating label
        self.label = QLabel(content)
        self.label.setObjectName("specialLabel")
        self.label.setMargin(10)

 
        # setting alignment to the text
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
 
        # making label multi-line
        self.label.setWordWrap(True)
 
        # adding label to the layout
        lay.addWidget(self.label)
 
    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)

class LoginScreen(QWidget):
    
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        #Creates a stack of widgets so you can store screens and choose which one to display.
        self.stackedWidget = QStackedWidget()
        
        # Window for login screen
        main_screen = QWidget()

        #Defining buttons and linking them to parent widget
        user_button = QPushButton('User', main_screen)
        admin_button = QPushButton('Admin', main_screen)

        #Adding functionality for what to do once the button is clicked
        user_button.clicked.connect(self.showUserScreen)
        admin_button.clicked.connect(self.passCheck)

        #Layout helps us define the order of the interface. QHBox means all items on the screen would be horizontally placed.
        layout = QHBoxLayout(main_screen)
        label = QLabel('Choose User Type:',main_screen)
        label.adjustSize()
        #Adds all the widgets
        # layout.addWidget(QLabel('Choose User Type:'))
        layout.addWidget(user_button,0)
        layout.addWidget(admin_button,0)
        
        #Adds the screen onto the stack and sets the current screen
        self.stackedWidget.addWidget(main_screen)
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.stackedWidget)

    def passCheck(self):
        self.stacked_widget.setCurrentIndex(1)

    def showUserScreen(self):
        self.stacked_widget.setCurrentIndex(2)

    def showAdminScreen(self):
        self.stacked_widget.setCurrentIndex(3)

class passCheck(QWidget):
    
    def __init__(self,stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.stackedWidget = QStackedWidget()

        main_screen = QWidget()
        passText = QLabel('Enter password:',main_screen)
        passEnter = QLineEdit(main_screen)
        passEnter.setEchoMode(QLineEdit.Password)
        passCheck_button = QPushButton('Log in',main_screen)
        back_button = QPushButton('Back',main_screen)

        passCheck_button.clicked.connect(lambda: self.checkPass(passEnter))
        back_button.clicked.connect(self.goBack)

        main_layout = QHBoxLayout(main_screen)
        main_layout.addWidget(passText)
        main_layout.addWidget(passEnter)
        main_layout.addWidget(passCheck_button)

        self.stackedWidget.addWidget(main_screen)
        # self.stackedWidget.setCurrentWidget(main_screen)
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.stackedWidget)

    def checkPass(self,passEnter):
        passCheck = passEnter.text().strip()
        if passCheck == "hehe":
            passEnter.clear()
            self.stacked_widget.setCurrentIndex(3)
        else:
            QMessageBox.critical(self, 'Error', 'Wrong Password. Try again')

    def goBack(self):
        self.stacked_widget.setCurrentIndex(0)

class UserScreen(QWidget):
    
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.dictionary = self.dictionaryCreate('english.csv')
        self.trie = self.make_trie()
        self.currentWord = ''
        self.initUI()

    def initUI(self):
        self.stackedWidget = QStackedWidget()
        # Main Screen
        main_screen = QWidget()
        get_button = QPushButton('Get Word', main_screen)
        get_letter_button = QPushButton('Get Word Letter-by-letter',main_screen)
        back_button = QPushButton('Back', main_screen)
        
        get_button.clicked.connect(self.showGetScreen)
        get_letter_button.clicked.connect(self.getLetterScreen)
        back_button.clicked.connect(self.goBack)

        main_layout = QVBoxLayout(main_screen)
        main_layout.addWidget(get_button)
        main_layout.addWidget(get_letter_button)

        self.stackedWidget.addWidget(main_screen)

        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.stackedWidget)

    def getLetterScreen(self):
        getLetter_screen = QWidget()
        self.dictionary = self.dictionaryCreate('english.csv')
        self.trie = self.make_trie()
        # Create widgets
        letter_entry = QLineEdit(getLetter_screen)
        getLetter_button = QPushButton('Get words with letter', getLetter_screen)
        getFinalWord_button = QPushButton('Get meaning of the word', getLetter_screen)
        reset_button = QPushButton('Reset sequence',getLetter_screen)
        back_button = QPushButton('Back', getLetter_screen)
        output_display = ScrollLabel(self)
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        # Connect buttons to slots
        getLetter_button.clicked.connect(lambda: self.getLetterWord(letter_entry, output_display))
        getFinalWord_button.clicked.connect(lambda: self.finalWord(output_display))
        back_button.clicked.connect(lambda: self.delete_clicked())
        reset_button.clicked.connect(lambda: self.reset_clicked(output_display))

        # Create layout
        get_letter_layout = QVBoxLayout(getLetter_screen)
        get_letter_layout.addWidget(QLabel('Letter:'))
        get_letter_layout.addWidget(letter_entry)
        get_letter_layout.addWidget(getLetter_button)
        get_letter_layout.addWidget(getFinalWord_button)
        get_letter_layout.addWidget(back_button)
        get_letter_layout.addWidget(reset_button)
        get_letter_layout.addWidget(QLabel('Output'))
        get_letter_layout.addWidget(output_display)  # Add the scroll area to the layout

        # Add screen to stacked widget
        self.stackedWidget.addWidget(getLetter_screen)
        self.stackedWidget.setCurrentWidget(getLetter_screen)    

    def showGetScreen(self):
        self.dictionary = self.dictionaryCreate('english.csv')
        self.trie = self.make_trie()
        get_screen = QWidget()
        word_entry = QLineEdit(get_screen)
        get_button = QPushButton('Get', get_screen)
        back_button = QPushButton('Back', get_screen)

        output_display = ScrollLabel(self)
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        get_button.clicked.connect(lambda: self.getWord(word_entry, output_display))
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        get_layout = QVBoxLayout(get_screen)
        get_layout.addWidget(QLabel('Word:'))
        get_layout.addWidget(word_entry)
        get_layout.addWidget(get_button)
        get_layout.addWidget(back_button)
        get_layout.addWidget(QLabel('Output:'))
        get_layout.addWidget(output_display)
        self.stackedWidget.addWidget(get_screen)
        self.stackedWidget.setCurrentWidget(get_screen)

    def dictionaryCreate(self, filename):
        dictionary = {}
        try:
            data = list()
            with open(filename,"r") as f:
                csv.field_size_limit(int(ct.c_ulong(-1).value // 2))
                reader = csv.reader(f)
                for row in reader:
                    data.append(row)
            
            for i in range(1,len(data)):
                word = data[i].pop(0)
                word = word.upper()
                if word in dictionary:
                    dictionary[word].append(','.join(data[i]))
                else:
                    dictionary[word] = [','.join(data[i])]
        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', f'Could not find {filename}. Please make sure the file exists.')
        return dictionary

    def make_trie(self):
        trie = {}
        for word in self.dictionary:
            current_dict = trie
            for letter in word:
                if letter not in current_dict:
                    current_dict[letter] = {}
                current_dict = current_dict[letter]
            current_dict["_end"] = self.dictionary[word]
        return trie

    def getWord(self, word_entry, output_display):
        word = word_entry.text().strip().upper()
        result = self.in_trie(word)
        output_display.setText(result)

    def in_trie(self, word):
        current_dict = self.trie
        for letter in word:
            if letter not in current_dict:
                return "No such word in dictionary."
            current_dict = current_dict[letter]
        if "_end" in current_dict:
            meanings = ''
            for i in range(len(current_dict["_end"])):
                meanings += str(i+1) + ") " + current_dict["_end"][i] + "\n"
            meanings = meanings[:-1]
            return f"{word}:\n{meanings}"
        else:
            return "No such word in dicitonary."

    def getLetterWord(self,letter_entry,output_display):
        letter_entry = letter_entry.text().strip()
        if len(letter_entry) > 1:
            output_display.setText("Invalid input. Enter one letter at a time.")
        else:
            self.currentWord += letter_entry
            letter_entry = self.currentWord
            result = self.in_trie_by_letter(letter_entry)
            if "No such words" in result:
                self.currentWord = self.currentWord[:-1]
                if "No words with the" not in output_display.text():
                    output_display.setText('No words with the inputted letter. Kindly pick a letter from one of the following combinations\n' + output_display.text())
            else:
                result = ", ".join(result)
                output_display.setText(result)

    def finalWord(self,output_display):
        temp = self.currentWord.upper()
        result = self.in_trie(temp)
        self.currentWord = ''
        output_display.setText(result)

    def in_trie_by_letter(self, currentWord):
        temp = currentWord.upper()
        current_dict = self.trie
        for letter in temp:
            if letter not in current_dict:
                return "No such words in dictionary that contain the following letters."
            current_dict = current_dict[letter]
        lst = list()
        for i in current_dict:
            if i == "_end":
                continue
            lst.append(currentWord+i.lower())
        return lst

    def delete_clicked(self):
        self.stackedWidget.setCurrentIndex(0)
        self.currentWord = ''

    def reset_clicked(self,output_display):
        self.currentWord = ''
        output_display.setText('Sequence resetted!')

    def goBack(self):
        self.stacked_widget.setCurrentIndex(0)

class AdminScreen(QWidget):
    
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.dictionary = self.dictionaryCreate('english.csv')
        self.trie = self.make_trie()
        self.currentWord = ''
        self.initUI()

    def initUI(self):
        self.stackedWidget = QStackedWidget()

        # Main Screen
        main_screen = QWidget()
        insert_button = QPushButton('Insert Word', main_screen)
        get_button = QPushButton('Get Word', main_screen)
        delete_button = QPushButton('Delete Word', main_screen)
        reset_button = QPushButton('Reset Dictionary', main_screen)
        get_letter_button = QPushButton('Get Word Letter-by-letter',main_screen)
        delete_meaning_button = QPushButton('Delete Meaning of Word',main_screen)
        back_button = QPushButton('Back',main_screen)
        
        insert_button.clicked.connect(self.showInsertScreen)
        get_button.clicked.connect(self.showGetScreen)
        delete_button.clicked.connect(self.showDeleteScreen)
        reset_button.clicked.connect(self.resetDictionary)
        get_letter_button.clicked.connect(self.getLetterScreen)
        delete_meaning_button.clicked.connect(self.ShowDeleteMeaningScreen)
        back_button.clicked.connect(self.goBack)

        main_layout = QVBoxLayout(main_screen)
        main_layout.addWidget(reset_button)
        main_layout.addWidget(insert_button)
        main_layout.addWidget(get_button)
        main_layout.addWidget(get_letter_button)
        main_layout.addWidget(delete_button)
        main_layout.addWidget(delete_meaning_button)

        self.stackedWidget.addWidget(main_screen)

        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.stackedWidget)

    def getLetterScreen(self):
        getLetter_screen = QWidget()

        # Create widgets
        letter_entry = QLineEdit(getLetter_screen)
        getLetter_button = QPushButton('Get words with letter', getLetter_screen)
        getFinalWord_button = QPushButton('Get meaning of the word', getLetter_screen)
        reset_button = QPushButton('Reset sequence',getLetter_screen)
        back_button = QPushButton('Back', getLetter_screen)
        output_display = ScrollLabel(self)
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        # Connect buttons to slots
        getLetter_button.clicked.connect(lambda: self.getLetterWord(letter_entry, output_display))
        getFinalWord_button.clicked.connect(lambda: self.finalWord(output_display))
        back_button.clicked.connect(lambda: self.delete_clicked())
        reset_button.clicked.connect(lambda: self.reset_clicked(output_display))

        # Create layout
        get_letter_layout = QVBoxLayout(getLetter_screen)
        get_letter_layout.addWidget(QLabel('Letter:'))
        get_letter_layout.addWidget(letter_entry)
        get_letter_layout.addWidget(getLetter_button)
        get_letter_layout.addWidget(getFinalWord_button)
        get_letter_layout.addWidget(back_button)
        get_letter_layout.addWidget(reset_button)
        get_letter_layout.addWidget(QLabel('Output'))
        get_letter_layout.addWidget(output_display)  # Add the scroll area to the layout

        # Add screen to stacked widget
        self.stackedWidget.addWidget(getLetter_screen)
        self.stackedWidget.setCurrentWidget(getLetter_screen)

    def showInsertScreen(self):
        insert_screen = QWidget()
        word_entry = QLineEdit(insert_screen)
        verb_entry = QLineEdit(insert_screen)
        meaning_entry = QTextEdit(insert_screen)
        insert_button = QPushButton('Insert', insert_screen)
        back_button = QPushButton('Back', insert_screen)
        output_display = ScrollLabel(self)
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)


        insert_button.clicked.connect(lambda: self.insertWord(word_entry, verb_entry, meaning_entry, output_display))
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        insert_layout = QVBoxLayout(insert_screen)
        insert_layout.addWidget(QLabel('Word:'))
        insert_layout.addWidget(word_entry)
        insert_layout.addWidget(QLabel('Verb:'))
        insert_layout.addWidget(verb_entry)
        insert_layout.addWidget(QLabel('Meaning:'))
        insert_layout.addWidget(meaning_entry)
        insert_layout.addWidget(insert_button)
        insert_layout.addWidget(back_button)
        insert_layout.addWidget(QLabel('Output:'))
        insert_layout.addWidget(output_display)

        self.stackedWidget.addWidget(insert_screen)
        self.stackedWidget.setCurrentWidget(insert_screen)

    def showGetScreen(self):
        get_screen = QWidget()
        word_entry = QLineEdit(get_screen)
        get_button = QPushButton('Get', get_screen)
        back_button = QPushButton('Back', get_screen)
        output_display = ScrollLabel(self)
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)


        get_button.clicked.connect(lambda: self.getWord(word_entry, output_display))
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        get_layout = QVBoxLayout(get_screen)
        get_layout.addWidget(QLabel('Word:'))
        get_layout.addWidget(word_entry)
        get_layout.addWidget(get_button)
        get_layout.addWidget(back_button)
        get_layout.addWidget(QLabel('Output:'))
        get_layout.addWidget(output_display)

        self.stackedWidget.addWidget(get_screen)
        self.stackedWidget.setCurrentWidget(get_screen)

    def showDeleteScreen(self):
        delete_screen = QWidget()
        word_entry = QLineEdit(delete_screen)
        delete_button = QPushButton('Delete', delete_screen)
        back_button = QPushButton('Back', delete_screen)
        output_display = ScrollLabel(self)
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        delete_button.clicked.connect(lambda: self.deleteWord(word_entry, output_display))
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        delete_layout = QVBoxLayout(delete_screen)
        delete_layout.addWidget(QLabel('Word:'))
        delete_layout.addWidget(word_entry)
        delete_layout.addWidget(delete_button)
        delete_layout.addWidget(back_button)
        delete_layout.addWidget(QLabel('Output:'))
        delete_layout.addWidget(output_display)

        self.stackedWidget.addWidget(delete_screen)
        self.stackedWidget.setCurrentWidget(delete_screen)
    
    def ShowDeleteMeaningScreen(self):
        delete_meaning_screen = QWidget()
        word_entry = QLineEdit(delete_meaning_screen)
        meaning_entry = QLineEdit(delete_meaning_screen)
        verb_entry = QLineEdit(delete_meaning_screen)
        delete_button = QPushButton('Find Meanings', delete_meaning_screen)
        back_button = QPushButton('Back', delete_meaning_screen)
        output_display = ScrollLabel(self)
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)


        delete_button.clicked.connect(lambda: self.deleteMeaning(word_entry, verb_entry, meaning_entry , output_display))
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        delete_layout = QVBoxLayout(delete_meaning_screen)
        delete_layout.addWidget(QLabel('Word:'))
        delete_layout.addWidget(word_entry)
        delete_layout.addWidget(QLabel('Verb:'))
        delete_layout.addWidget(verb_entry)
        delete_layout.addWidget(QLabel('Meaning:'))
        delete_layout.addWidget(meaning_entry)
        delete_layout.addWidget(delete_button)
        delete_layout.addWidget(back_button)
        delete_layout.addWidget(QLabel('Output:'))
        delete_layout.addWidget(output_display)

        self.stackedWidget.addWidget(delete_meaning_screen)
        self.stackedWidget.setCurrentWidget(delete_meaning_screen)

    def deleteMeaning(self, word_entry, verb_entry, meaning_entry, output_display):
        word = word_entry.text().strip().upper()
        verb = verb_entry.text().strip()
        meaning = meaning_entry.text().strip()
        result = self.delete_trie_meaning(word, verb, meaning)
        output_display.setText(result) 

    def delete_trie_meaning(self, word, verb, meaning ):
        current_dict = self.trie
        for letter in word:
            if letter not in current_dict:
                return "No such word in dictionary."
            current_dict = current_dict[letter]
        if "_end" not in current_dict:
            return "No such word in dictionary."
        else:
            lst = []
            for i in range(len(current_dict["_end"])):
                if len(verb) == 0:
                    if current_dict["_end"][i][0] == "," and meaning in current_dict["_end"][i][1:]:
                        lst.append(current_dict["_end"][i][1:])
                else:
                    if verb == current_dict["_end"][i][:len(verb)] and meaning in current_dict["_end"][i][len(verb):]:
                        lst.append(current_dict["_end"][i][len(verb)+1:])
            if len(lst) == 0:
                return "No such meaning exists."
            else:
                self.show_delete_meaning_list(word, verb, lst)

    def show_delete_meaning_list(self, word, verb, lst):
        delete_meaning_list_screen = QWidget()
        
        back_button = QPushButton('Back', delete_meaning_list_screen)
        select_meaning = QPushButton('Delete Selected Meaning',delete_meaning_list_screen)
        list_widget = QListWidget(self)
        for meaning in lst:
            list_widget.addItem(meaning)
        list_widget.setWordWrap(True)

        output_display = ScrollLabel(self)
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        select_meaning.clicked.connect(lambda: self.deleteList(word,verb,list_widget.currentItem().text(),output_display, list_widget, list_widget.currentRow()))

        delete_meaning_layout = QVBoxLayout(delete_meaning_list_screen)
        delete_meaning_layout.addWidget(QLabel('Select a meaning from the list'))
        delete_meaning_layout.addWidget(list_widget)
        delete_meaning_layout.addWidget(back_button)
        delete_meaning_layout.addWidget(select_meaning)
        delete_meaning_layout.addWidget(output_display)

        self.stackedWidget.addWidget(delete_meaning_list_screen)
        self.stackedWidget.setCurrentWidget(delete_meaning_list_screen)

    def removeListItem(self,list_widget,row):
        list_widget.takeItem(row)

    def deleteList(self, word, verb, item, output_display, list_widget, row):
        self.removeListItem(list_widget,row)
        meaning = item
        result = self.delete_meaning_list_(word, verb, meaning)
        output_display.setText(result) 

    def delete_meaning_list_(self, word, verb, meaning):
        current_dict = self.trie
        for letter in word:
            if letter not in current_dict:
                return "No such word in dictionary."
            current_dict = current_dict[letter]
        check = f"{verb},{meaning}"
        if len(current_dict["_end"]) == 1:
            del current_dict["_end"]
            self.delete_meaning_from_CSV(word,verb,meaning)
            return "Meaning and word successfully deleted as there is only one meaning."
        else:
            for i in range(len(current_dict["_end"])):
                if check == current_dict["_end"][i]:
                    del current_dict["_end"][i]
                    self.delete_meaning_from_CSV(word,verb,meaning)
                    return "Meaning successfully deleted."
    
    def delete_meaning_from_CSV(self, word, verb, meaning):
        try:
            meaning = meaning.strip('"')
            with open("english.csv", "r", newline='', encoding='utf-8') as copyf, open("transfer.csv", "w", newline='', encoding='utf-8') as f:
                csv.field_size_limit(int(ct.c_ulong(-1).value // 2))
                reader = csv.reader(copyf)
                writer = csv.writer(f)
                for row in reader:
                    if word != row[0].strip().upper() or verb != row[1] or meaning != row[2]:
                        writer.writerow(row)
            os.replace("transfer.csv", "english.csv")
        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', 'CSV file not found.')

    def dictionaryCreate(self, filename):
        dictionary = {}
        try:
            data = list()
            with open(filename,"r") as f:
                csv.field_size_limit(int(ct.c_ulong(-1).value // 2))
                reader = csv.reader(f)
                for row in reader:
                    data.append(row)
            
            for i in range(1,len(data)):
                word = data[i].pop(0)
                word = word.upper()
                if word in dictionary:
                    dictionary[word].append(','.join(data[i]))
                else:
                    dictionary[word] = [','.join(data[i])]
        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', f'Could not find {filename}. Please make sure the file exists.')
        return dictionary

    def make_trie(self):
        trie = {}
        for word in self.dictionary:
            current_dict = trie
            for letter in word:
                if letter not in current_dict:
                    current_dict[letter] = {}
                current_dict = current_dict[letter]
            current_dict["_end"] = self.dictionary[word]
        return trie

    def insertWord(self, word_entry, verb_entry, meaning_entry, output_display):
        word = word_entry.text().strip()
        verb = verb_entry.text().strip()
        meaning = meaning_entry.toPlainText().strip()
        
        if word == '' or meaning == '':
            output_display.setText('Word and meaning cannot be empty.')
            return
        
        result = self.insert_trie(word, meaning, verb)
        output_display.setText(result)

    def insert_trie(self, word, meaning, verb):
        temp = word.upper()
        current_dict = self.trie
        for letter in temp:
            if letter not in current_dict:
                current_dict[letter] = {}
            current_dict = current_dict[letter]
        toBeAppended = verb + "," + meaning
        if "_end" in current_dict:
            if toBeAppended not in current_dict["_end"]:
                current_dict["_end"].append(toBeAppended)
                self.writeToCSV(word, verb, meaning)
                return "Meaning added successfully"
            else:
                return "Meaning already in dictionary!"
        else:
            current_dict["_end"] = [toBeAppended]
            self.writeToCSV(word, verb, meaning)
            return "Word entered successfully"

    def writeToCSV(self, word, verb, meaning):
        try:
            with open("english.csv", "a", newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([word, verb, meaning])
        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', 'CSV file not found.')

    def getWord(self, word_entry, output_display):
        word = word_entry.text().strip().upper()
        result = self.in_trie(word)
        output_display.setText(result)

    def in_trie(self, word):
        current_dict = self.trie
        for letter in word:
            if letter not in current_dict:
                return "No such word in dictionary."
            current_dict = current_dict[letter]
        if "_end" in current_dict:
            meanings = ''
            for i in range(len(current_dict["_end"])):
                meanings += str(i+1) + ") " + current_dict["_end"][i] + "\n"
            meanings = meanings[:-1]
            return f"{word}:\n{meanings}"
        else:
            return "No such word in dictionary."
        
    def in_trie_by_letter(self, currentWord):
        temp = currentWord.upper()
        current_dict = self.trie
        for letter in temp:
            if letter not in current_dict:
                return "No such words in dictionary that contain the following letters."
            current_dict = current_dict[letter]
        lst = list()
        for i in current_dict:
            if i == "_end":
                continue
            lst.append(currentWord+i.lower())
        return lst

    def deleteWord(self, word_entry, output_display):
        word = word_entry.text().strip().upper()
        result = self.delete_trie_word(word)
        output_display.setText(result)

    def delete_trie_word(self, word):
        current_dict = self.trie
        for letter in word:
            if letter not in current_dict:
                return "No such word in dictionary."
            current_dict = current_dict[letter]
        if "_end" not in current_dict:
            return "No such word in dictionary."
        else:
            del current_dict["_end"]
            self.delete_word_from_CS(word)
            return "Word removed successfully."

    def delete_word_from_CS(self, word):
        try:
            with open("english.csv", "r", newline='', encoding='utf-8') as copyf, open("transfer.csv", "w", newline='', encoding='utf-8') as f:
                csv.field_size_limit(int(ct.c_ulong(-1).value // 2))
                reader = csv.reader(copyf)
                writer = csv.writer(f)
                for row in reader:
                    if row[0].strip().upper() != word:
                        writer.writerow(row)
            os.replace("transfer.csv", "english.csv")
            print(UserScreen.dictionary)
        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', 'CSV file not found.')
    
    def resetDictionary(self):
            try:
                with open("english.csv","w",newline='') as f:
                    writer = csv.writer(f)
                    with open("original.csv","r") as copyf:
                        csv.field_size_limit(int(ct.c_ulong(-1).value // 2))
                        reader = csv.reader(copyf)
                        for i, rows in enumerate(reader):
                            writer.writerow([rows[0],rows[1],rows[2]])
                self.dictionary = self.dictionaryCreate("english.csv")
                self.trie = self.make_trie()
                QMessageBox.information(self, 'Success', 'Dictionary reset successfully.')
            except FileNotFoundError:
                QMessageBox.critical(self, 'Error', 'Original CSV file not found.')
    
    def delete_clicked(self):
        self.stackedWidget.setCurrentIndex(0)
        self.currentWord = ''

    def getLetterWord(self,letter_entry,output_display):
        letter_entry = letter_entry.text().strip()
        if len(letter_entry) > 1:
            output_display.setText("Invalid input. Enter one letter at a time.")
        else:
            self.currentWord += letter_entry
            letter_entry = self.currentWord
            result = self.in_trie_by_letter(letter_entry)
            if "No such words" in result:
                self.currentWord = self.currentWord[:-1]
                if "No words with the" not in output_display.text():
                    output_display.setText('No words with the inputted letter. Kindly pick a letter from one of the following combinations\n' + output_display.text())
            else:
                result = ", ".join(result)
                output_display.setText(result)
    
    def reset_clicked(self,output_display):
        self.currentWord = ''
        output_display.setText('Sequence resetted')

    def finalWord(self,output_display):
        temp = self.currentWord.upper()
        result = self.in_trie(temp)
        self.currentWord = ''
        output_display.setText(result)

    def goBack(self):
        self.stacked_widget.setCurrentIndex(0)

def main():
    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()

    stacked_widget.setStyleSheet(open('Style.css').read())

    login_screen = LoginScreen(stacked_widget)
    pass_check = passCheck(stacked_widget)
    user_screen = UserScreen(stacked_widget)
    admin_screen = AdminScreen(stacked_widget)

    stacked_widget.addWidget(login_screen)
    stacked_widget.addWidget(pass_check)
    stacked_widget.addWidget(user_screen)
    stacked_widget.addWidget(admin_screen)

    stacked_widget.setWindowTitle('Dictionary Application')
    stacked_widget.setFixedHeight(stacked_widget.sizeHint().height() + 200)
    stacked_widget.setFixedWidth(stacked_widget.sizeHint().width() + 100)
    stacked_widget.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

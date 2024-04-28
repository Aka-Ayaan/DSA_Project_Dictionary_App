import os
import ctypes as ct
import sys
import csv
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class SharedResources: # Singleton class to store all the methods used by the UserScreen and AdminScreen classes
    _instance = None

    # Centralized resources for the application
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SharedResources, cls).__new__(cls)
            cls._instance.load_resources()
        return cls._instance

    def load_resources(self):
        self.dictionary = self.dictionaryCreate('english.csv')
        self.trie = self.make_trie(self.dictionary)
        self.suggestingDictionary = self.dictionaryCreate('suggest.csv')
        self.suggestingTrie = self.make_trie(self.suggestingDictionary)
        self.rejectedDictionary = self.dictionaryCreate('rejectedWords.csv')
        self.rejectedTrie = self.make_trie(self.rejectedDictionary)
        self.currentWord = ''
    
    # Create a dictionary from the CSV file
    def dictionaryCreate(self, filename):
        dictionary = {}
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
        return dictionary

    # Create a trie from the dictionary
    def make_trie(self,dictionary):
        trie = {}
        for word in dictionary:
            current_dict = trie
            for letter in word:
                if letter not in current_dict:
                    current_dict[letter] = {}
                current_dict = current_dict[letter]
            current_dict["_end"] = dictionary[word]
        return trie
    
    # Overwrite the dictionary with the original CSV file
    def resetDictionary(self):
        with open("english.csv","w",newline='') as f:
            writer = csv.writer(f)
            with open("original.csv","r") as copyf:
                csv.field_size_limit(int(ct.c_ulong(-1).value // 2))
                reader = csv.reader(copyf)
                for i, rows in enumerate(reader):
                    writer.writerow([rows[0],rows[1],rows[2]])
        self.load_resources()
    
    # Insert a word into the trie and CSV file
    def insert_trie(self, word, meaning, verb, trieStr='main', filename='english.csv', dictionaryStr='main'):
        if trieStr == "main":
            current_dict = self.trie
        elif trieStr == "suggest":
            current_dict = self.suggestingTrie
        elif trieStr == "reject":
            current_dict = self.rejectedTrie
        temp = word.upper()
        for letter in temp:
            if letter not in current_dict:
                current_dict[letter] = {}
            current_dict = current_dict[letter]
        toBeAppended = verb + "," + meaning
        if "_end" in current_dict:
            if toBeAppended not in current_dict["_end"]:
                current_dict["_end"].append(toBeAppended)
                self.writeToCSV(word, verb, meaning, filename, dictionaryStr)
                return "Meaning added successfully"
            else:
                return "Meaning already in dictionary!"
        else:
            current_dict["_end"] = [toBeAppended]
            self.writeToCSV(word, verb, meaning, filename, dictionaryStr)
            return "Word entered successfully"

    # Write any changes to the CSV file
    def writeToCSV(self, word, verb, meaning, filename='english.csv', dictionaryStr='main'):
        with open(filename, "a", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([word, verb, meaning])
        if dictionaryStr == "main":    
            self.dictionary = self.dictionaryCreate(filename)
        elif dictionaryStr == "suggest":
            self.suggestingDictionary = self.dictionaryCreate(filename)
        elif dictionaryStr == "reject":
            self.rejectedDictionary = self.dictionaryCreate(filename)

    # Check if a word is in the trie and gets its meanings
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

    # Prefix search for words in the trie    
    def in_trie_by_letter(self):
        temp = self.currentWord.upper()
        current_dict = self.trie
        for letter in temp:
            if letter not in current_dict:
                return "No such words in dictionary that contain the following letters."
            current_dict = current_dict[letter]
        lst = list()
        for i in current_dict:
            if i == "_end":
                continue
            lst.append(self.currentWord+i.lower())
        return lst
    
    # Delete a word from the trie and CSV file
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
            self.delete_word_from_CSV(word)
            return "Word removed successfully."

    # Deletion from the CSV file
    # transfer.csv is temporarily created to store the changes
    def delete_word_from_CSV(self, word):
        with open("english.csv", "r", newline='', encoding='utf-8') as copyf, open("transfer.csv", "w", newline='', encoding='utf-8') as f:
            csv.field_size_limit(int(ct.c_ulong(-1).value // 2))
            reader = csv.reader(copyf)
            writer = csv.writer(f)
            for row in reader:
                if row[0].strip().upper() != word:
                    writer.writerow(row)
        os.replace("transfer.csv", "english.csv")
        self.dictionary = self.dictionaryCreate('english.csv')

    # Delete a meaning of a word in the trie and CSV file   
    def returnList_delete_meaning(self, word, verb, meaning,trieStr='main'):
        if trieStr == "main":
            current_dict = self.trie
        elif trieStr == "suggest":
            current_dict = self.suggestingTrie
        elif trieStr == "reject":
            current_dict = self.rejectedTrie
        temp = word.upper()
        for letter in temp:
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
                return lst

    # The list of meanings shown to the user for deletion
    def delete_meaning_list(self, word, verb, meaning,trieStr="main",filename="english.csv",dictionaryStr="main"):
        if trieStr == "main":
            current_dict = self.trie
        elif trieStr == "suggest":
            current_dict = self.suggestingTrie
        for letter in word:
            if letter not in current_dict:
                return "No such word in dictionary."
            current_dict = current_dict[letter]
        check = f"{verb},{meaning}"
        if len(current_dict["_end"]) == 1:
            if check == current_dict["_end"][0]:
                del current_dict["_end"]
                self.delete_meaning_from_CSV(word,verb,meaning,dictionaryStr,filename)
                return "Meaning and word successfully deleted as there is only one meaning."
        else:
            for i in range(len(current_dict["_end"])):
                if check == current_dict["_end"][i]:
                    del current_dict["_end"][i]
                    self.delete_meaning_from_CSV(word,verb,meaning,dictionaryStr,filename)
                    return "Meaning successfully deleted."
    
    # Deletion of the selected meaning from the CSV file
    def delete_meaning_from_CSV(self, word, verb, meaning,dictionaryStr='main',filename='english.csv'):
        meaning = meaning.strip('"')
        with open(filename, "r", newline='', encoding='utf-8') as copyf, open("transfer.csv", "w", newline='', encoding='utf-8') as f:
            csv.field_size_limit(int(ct.c_ulong(-1).value // 2))
            reader = csv.reader(copyf)
            writer = csv.writer(f)
            for row in reader:
                if word != row[0].strip().upper() or verb != row[1] or meaning != row[2]:
                    writer.writerow(row)
        os.replace("transfer.csv", filename)
        if dictionaryStr == "main":
            self.dictionary = self.dictionaryCreate(filename)
        elif dictionaryStr == "suggest":
            self.suggestingDictionary = self.dictionaryCreate(filename)               

    def itemsOfList(self):
        lst = list()
        for i in self.suggestingDictionary:
            for j in range(len(self.suggestingDictionary[i])):
                temp = self.suggestingDictionary[i][j].split(',')
                verb = temp[0]
                meaning = " ".join(temp[1:])
                toAppend = "Word: " + i + "\n" + "Type of speech: " + verb + "\n" + "Meaning: " + meaning
                lst.append(toAppend)
        return lst

class ScrollLabel(QScrollArea): # A class to create a scrollable label used in the UserScreen and AdminScreen classes
 
    # constructor
    def __init__(self):
        QScrollArea.__init__(self)
 
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

class LoginScreen(QWidget): # A class to create the login screen
    
    # Constructor
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        # Creates a stack of widgets so you can store screens and choose which one to display.
        self.stackedWidget = QStackedWidget()
        
        # Window for login screen
        main_screen = QWidget()

        # Defining buttons and linking them to parent widget
        user_button = QPushButton('User', main_screen)
        admin_button = QPushButton('Admin', main_screen)

        # Adding functionality for what to do once the button is clicked
        user_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        admin_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        # Layout helps us define the order of the interface. QHBox means all items on the screen would be horizontally placed.
        layout = QHBoxLayout(main_screen)
        label = QLabel('Choose User Type:',main_screen)
        label.adjustSize()
        # Adds all the widgets to the layout
        layout.addWidget(user_button)
        layout.addWidget(admin_button)
        
        # Adds the screen onto the stack and sets the current screen
        self.stackedWidget.addWidget(main_screen)
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.stackedWidget)

class passCheck(QWidget): # A class to create the password check screen if Admin is selected
    
    # Constructor
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
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        main_layout = QHBoxLayout(main_screen)
        main_layout.addWidget(passText)
        main_layout.addWidget(passEnter)
        main_layout.addWidget(passCheck_button)

        self.stackedWidget.addWidget(main_screen)
        # self.stackedWidget.setCurrentWidget(main_screen)
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.stackedWidget)

    # Checking the password entered
    def checkPass(self,passEnter):
        passCheck = passEnter.text().strip()
        if passCheck == "hehe":
            passEnter.clear()
            self.stacked_widget.setCurrentIndex(3)
        else:
            QMessageBox.critical(self, 'Error', 'Wrong Password. Try again')

    # Function to go back to the previous screen if the back button is clicked

class UserScreen(QWidget):
    
    # Constructor
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.resources = SharedResources()
        self.initUI()

    def initUI(self):

        self.stackedWidget = QStackedWidget() # Creating a stack of widgets 
        
        # Main Screen for the User
        main_screen = QWidget()

        # Defining buttons and linking them to parent widget
        get_button = QPushButton('Get Word', main_screen)
        get_letter_button = QPushButton('Get Word Letter-by-letter',main_screen)
        suggest_new = QPushButton('Suggest-a-word',main_screen)
        back_button = QPushButton('Back', main_screen)
        
        get_button.clicked.connect(self.showGetScreen)
        get_letter_button.clicked.connect(self.getLetterScreen)
        suggest_new.clicked.connect(self.getNewWordScreen)
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        # Adding the elements to the layout
        main_layout = QVBoxLayout(main_screen)
        main_layout.addWidget(get_button)
        main_layout.addWidget(get_letter_button)
        main_layout.addWidget(suggest_new)

        # Add screen to stacked widget
        self.stackedWidget.addWidget(main_screen)

        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.stackedWidget)

    def getLetterScreen(self):
        
        getLetter_screen = QWidget() # Create widget
    
        # Initialize elements of the widget
        letter_entry = QLineEdit(getLetter_screen)
        getLetter_button = QPushButton('Get words with letter', getLetter_screen)
        getFinalWord_button = QPushButton('Get meaning of the word', getLetter_screen)
        reset_button = QPushButton('Reset sequence',getLetter_screen)
        back_button = QPushButton('Back', getLetter_screen)
        output_display = ScrollLabel()
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        # Connect buttons to slots
        getLetter_button.clicked.connect(lambda: self.getLetterWord(letter_entry, output_display))
        getFinalWord_button.clicked.connect(lambda: self.finalWord(output_display))
        back_button.clicked.connect(lambda: self.goBack())
        reset_button.clicked.connect(lambda: self.reset_clicked(output_display))

        # Create layout and add elements to it
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

        get_screen = QWidget() # Create widget

        # Initialize elements of the widget
        word_entry = QLineEdit(get_screen)
        get_button = QPushButton('Get', get_screen)
        back_button = QPushButton('Back', get_screen)
        output_display = ScrollLabel()
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        # Connect buttons to slots
        get_button.clicked.connect(lambda: self.getWord(word_entry, output_display))
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        # Create layout and add elements to it
        get_layout = QVBoxLayout(get_screen)
        get_layout.addWidget(QLabel('Word:'))
        get_layout.addWidget(word_entry)
        get_layout.addWidget(get_button)
        get_layout.addWidget(back_button)
        get_layout.addWidget(QLabel('Output:'))
        get_layout.addWidget(output_display)

        # Add screen to stacked widget
        self.stackedWidget.addWidget(get_screen)
        self.stackedWidget.setCurrentWidget(get_screen)

    def getWord(self, word_entry, output_display): # Function to link the GUI to the trie functionality
        word = word_entry.text().strip().upper()
        if word == '':
            QMessageBox.critical(self, 'Error', 'Enter a word to continue!')
        else:
            result = self.resources.in_trie(word)
            output_display.setText(result)

    def getLetterWord(self,letter_entry,output_display): # Function to link the GUI to the trie functionality
        letter_text = letter_entry.text().strip()
        letter_entry.clear()
        if len(letter_text) > 1:
            QMessageBox.critical(self, 'Error', 'Enter one letter at a time!')
        elif len(letter_text) == 0:
            QMessageBox.critical(self, 'Error', 'Enter a letter to continue!')
        else:
            self.resources.currentWord += letter_text
            result = self.resources.in_trie_by_letter()
            if "No such words" in result:
                self.resources.currentWord = self.resources.currentWord[:-1]
                QMessageBox.critical(self, 'Error', 'No words for the following letter. Kindly pick a letter from the combinations given')
            else:
                result = ", ".join(result)
                output_display.setText(result)

    def finalWord(self,output_display): # Helper function to get the final word
        temp = self.resources.currentWord.upper()
        result = self.resources.in_trie(temp)
        self.resources.currentWord = ''
        output_display.setText(result)

    def getNewWordScreen(self):
        getNewWord_screen = QWidget() #Create Widget

       #Initialize elements of wthe widget        
        word_entry = QLineEdit(getNewWord_screen)
        verb_entry = QLineEdit(getNewWord_screen)
        meaning_entry = QLineEdit(getNewWord_screen)
        entry_button = QPushButton('Suggest Word',getNewWord_screen)
        back_button = QPushButton('Back',getNewWord_screen)
        output_display = ScrollLabel()
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        #Connect buttons to slots
        entry_button.clicked.connect(lambda: self.processSuggestion(word_entry,verb_entry,meaning_entry,output_display))
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        #Create layout and add elements to it
        getNewWord_layout = QVBoxLayout(getNewWord_screen)
        getNewWord_layout.addWidget(QLabel('Word:'))
        getNewWord_layout.addWidget(word_entry)
        getNewWord_layout.addWidget(QLabel('Type of speech (verb, noun, adjectives):'))
        getNewWord_layout.addWidget(verb_entry)
        getNewWord_layout.addWidget(QLabel('Meaning:'))
        getNewWord_layout.addWidget(meaning_entry)
        getNewWord_layout.addWidget(back_button)
        getNewWord_layout.addWidget(entry_button)
        getNewWord_layout.addWidget(QLabel('Output:'))
        getNewWord_layout.addWidget(output_display)

        #Add screen to stacked widget
        self.stackedWidget.addWidget(getNewWord_screen)
        self.stackedWidget.setCurrentWidget(getNewWord_screen)

    def processSuggestion(self,word_entry,verb_entry,meaning_entry,output_display):
        word = word_entry.text().strip()
        verb = verb_entry.text().strip()
        meaning = meaning_entry.text().strip()
        if word == '':
            QMessageBox.critical(self, 'Error', 'Word field is empty. Kindly enter a word')
        elif meaning == '':
            QMessageBox.critical(self,'Error','Meaning field is empty. Kindly enter a word')
        else:
            result = self.resources.returnList_delete_meaning(word,verb,meaning)      
            if type(result) == list:
                for i in result:
                    if i == meaning:
                        output_display.setText('Meaning already exists in dictionary!')
                        return
            else:
                forbidden = self.resources.returnList_delete_meaning(word,verb,meaning,'reject')
                if type(forbidden) == list:
                    for i in forbidden:
                        if i == meaning:
                            output_display.setText('The following meaning has already been rejected and can\'t be added into the dictionary.')
                            return
            output = self.resources.insert_trie(word,meaning,verb,"suggest",'suggest.csv','suggest')
            if output == "Meaning already in dictionary!":
                output_display.setText('This meaning is already under review!')
            else:
                output_display.setText('Suggestion received! Thanks for contributing. We will review your input and insert it into the dictionary if applicable!')

    def reset_clicked(self,output_display): # Function to reset the sequence
        self.resources.currentWord = ''
        output_display.setText('Sequence resetted!')

    def goBack(self):
        self.resources.currentWord = ''
        self.stackedWidget.setCurrentIndex(0)

class AdminScreen(QWidget):

    # Constructor
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.resources = SharedResources()
        self.initUI()

    def initUI(self):
        
        self.stackedWidget = QStackedWidget() # Creating a stack of widgets

        # Main Screen for the Admin
        main_screen = QWidget()

        # Defining buttons and linking them to parent widget
        insert_button = QPushButton('Insert Word', main_screen)
        get_button = QPushButton('Get Word', main_screen)
        delete_button = QPushButton('Delete Word', main_screen)
        reset_button = QPushButton('Reset Dictionary', main_screen)
        get_letter_button = QPushButton('Get Word Letter-by-letter',main_screen)
        delete_meaning_button = QPushButton('Delete Meaning of Word',main_screen)
        review_user_suggestion_button = QPushButton('Review user suggestions',main_screen)
        back_button = QPushButton('Back',main_screen)
        
        # Functionality for the buttons when clicked
        insert_button.clicked.connect(self.showInsertScreen)
        get_button.clicked.connect(self.showGetScreen)
        delete_button.clicked.connect(self.showDeleteScreen)
        reset_button.clicked.connect(self.resetDict)
        get_letter_button.clicked.connect(self.getLetterScreen)
        delete_meaning_button.clicked.connect(self.ShowDeleteMeaningScreen)
        review_user_suggestion_button.clicked.connect(self.showUserSuggestions)
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        # Adding the elements to the layout
        main_layout = QVBoxLayout(main_screen)
        main_layout.addWidget(reset_button)
        main_layout.addWidget(insert_button)
        main_layout.addWidget(get_button)
        main_layout.addWidget(get_letter_button)
        main_layout.addWidget(delete_button)
        main_layout.addWidget(delete_meaning_button)
        main_layout.addWidget(review_user_suggestion_button)

        # Add screen to stacked widget
        self.stackedWidget.addWidget(main_screen)
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.stackedWidget)

    def resetDict(self):
        self.resources.resetDictionary()
        QMessageBox.information(self, 'Success', 'Dictionary resetted')

    def getLetterScreen(self):

        getLetter_screen = QWidget() # Creating widget

        # Initialize elements of the widget
        letter_entry = QLineEdit(getLetter_screen)
        getLetter_button = QPushButton('Get words with letter', getLetter_screen)
        getFinalWord_button = QPushButton('Get meaning of the word', getLetter_screen)
        reset_button = QPushButton('Reset sequence',getLetter_screen)
        back_button = QPushButton('Back', getLetter_screen)
        output_display = ScrollLabel()
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        # Connect buttons to slots
        getLetter_button.clicked.connect(lambda: self.getLetterWord(letter_entry, output_display))
        getFinalWord_button.clicked.connect(lambda: self.finalWord(output_display))
        back_button.clicked.connect(lambda: self.goBack())
        reset_button.clicked.connect(lambda: self.reset_clicked(output_display))

        # Create layout and add elements to it
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

        insert_screen = QWidget() # Creating widget
        
        # Initialize elements of the widget
        word_entry = QLineEdit(insert_screen)
        verb_entry = QLineEdit(insert_screen)
        meaning_entry = QTextEdit(insert_screen)
        insert_button = QPushButton('Insert', insert_screen)
        back_button = QPushButton('Back', insert_screen)
        output_display = ScrollLabel()
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        # Connect buttons to slots
        insert_button.clicked.connect(lambda: self.insertWord(word_entry, verb_entry, meaning_entry, output_display))
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        # Create layout and add elements to it
        insert_layout = QVBoxLayout(insert_screen)
        insert_layout.addWidget(QLabel('Word:'))
        insert_layout.addWidget(word_entry)
        insert_layout.addWidget(QLabel('Type of speech (verb, noun, adjectives):'))
        insert_layout.addWidget(verb_entry)
        insert_layout.addWidget(QLabel('Meaning:'))
        insert_layout.addWidget(meaning_entry)
        insert_layout.addWidget(insert_button)
        insert_layout.addWidget(back_button)
        insert_layout.addWidget(QLabel('Output:'))
        insert_layout.addWidget(output_display)

        # Add screen to stacked widget
        self.stackedWidget.addWidget(insert_screen)
        self.stackedWidget.setCurrentWidget(insert_screen)

    def showGetScreen(self):

        get_screen = QWidget() # Creating widget
        
        # Initialize elements of the widget
        word_entry = QLineEdit(get_screen)
        get_button = QPushButton('Get', get_screen)
        back_button = QPushButton('Back', get_screen)
        output_display = ScrollLabel()
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        # Connect buttons to slots
        get_button.clicked.connect(lambda: self.getWord(word_entry, output_display))
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        # Create layout and add elements to it
        get_layout = QVBoxLayout(get_screen)
        get_layout.addWidget(QLabel('Word:'))
        get_layout.addWidget(word_entry)
        get_layout.addWidget(get_button)
        get_layout.addWidget(back_button)
        get_layout.addWidget(QLabel('Output:'))
        get_layout.addWidget(output_display)

        # Add screen to stacked widget
        self.stackedWidget.addWidget(get_screen)
        self.stackedWidget.setCurrentWidget(get_screen)

    def showDeleteScreen(self):

        delete_screen = QWidget() # Creating widget

        # Initialize elements of the widget
        word_entry = QLineEdit(delete_screen)
        delete_button = QPushButton('Delete', delete_screen)
        back_button = QPushButton('Back', delete_screen)
        output_display = ScrollLabel()
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        # Connect buttons to slots
        delete_button.clicked.connect(lambda: self.deleteWord(word_entry, output_display))
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        # Create layout and add elements to it
        delete_layout = QVBoxLayout(delete_screen)
        delete_layout.addWidget(QLabel('Word:'))
        delete_layout.addWidget(word_entry)
        delete_layout.addWidget(delete_button)
        delete_layout.addWidget(back_button)
        delete_layout.addWidget(QLabel('Output:'))
        delete_layout.addWidget(output_display)

        # Add screen to stacked widget
        self.stackedWidget.addWidget(delete_screen)
        self.stackedWidget.setCurrentWidget(delete_screen)
    
    def ShowDeleteMeaningScreen(self):

        delete_meaning_screen = QWidget() # Creating widget

        # Initialize elements of the widget
        word_entry = QLineEdit(delete_meaning_screen)
        meaning_entry = QLineEdit(delete_meaning_screen)
        verb_entry = QLineEdit(delete_meaning_screen)
        delete_button = QPushButton('Find Meanings', delete_meaning_screen)
        back_button = QPushButton('Back', delete_meaning_screen)
        output_display = ScrollLabel()
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        # Connect buttons to slots
        delete_button.clicked.connect(lambda: self.deleteMeaning(word_entry, verb_entry, meaning_entry , output_display))
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        # Create layout and add elements to it
        delete_layout = QVBoxLayout(delete_meaning_screen)
        delete_layout.addWidget(QLabel('Word:'))
        delete_layout.addWidget(word_entry)
        delete_layout.addWidget(QLabel('Type of speech (verb, noun, adjectives):'))
        delete_layout.addWidget(verb_entry)
        delete_layout.addWidget(QLabel('Enter a meaning or part of a meaning:'))
        delete_layout.addWidget(meaning_entry)
        delete_layout.addWidget(delete_button)
        delete_layout.addWidget(back_button)
        delete_layout.addWidget(QLabel('Output:'))
        delete_layout.addWidget(output_display)

        # Add screen to stacked widget
        self.stackedWidget.addWidget(delete_meaning_screen)
        self.stackedWidget.setCurrentWidget(delete_meaning_screen)

    def deleteMeaning(self, word_entry, verb_entry, meaning_entry, output_display): # Function to link the GUI to the trie functionality
        word = word_entry.text().strip().upper()
        verb = verb_entry.text().strip()
        meaning = meaning_entry.text().strip()
        if word == '':
            QMessageBox.critical(self, 'Error', 'Enter a word to continue!')
        else:
            result = self.resources.returnList_delete_meaning(word, verb, meaning)
            if type(result) == list:
                result = self.show_delete_meaning_list(word,verb,result)
            else:
                output_display.setText(result) 


    def show_delete_meaning_list(self, word, verb, lst): # Function to show the list of meanings to the user for deletion
        
        delete_meaning_list_screen = QWidget() # Creating widget

        # Initialize elements of the widget
        back_button = QPushButton('Back', delete_meaning_list_screen)
        select_meaning = QPushButton('Delete Selected Meaning',delete_meaning_list_screen)
        list_widget = QListWidget(self)
        for meaning in lst:
            list_widget.addItem(meaning)
        list_widget.setWordWrap(True)
        output_display = ScrollLabel()
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        # Connect buttons to slots
        back_button.clicked.connect(lambda: self.ShowDeleteMeaningScreen())
        select_meaning.clicked.connect(lambda: self.deleteList(word,verb,list_widget.currentItem(),output_display, list_widget, list_widget.currentRow()))

        # Create layout and add elements to it
        delete_meaning_layout = QVBoxLayout(delete_meaning_list_screen)
        delete_meaning_layout.addWidget(QLabel('Select a meaning from the list'))
        delete_meaning_layout.addWidget(list_widget)
        delete_meaning_layout.addWidget(back_button)
        delete_meaning_layout.addWidget(select_meaning)
        delete_meaning_layout.addWidget(QLabel('Output:'))
        delete_meaning_layout.addWidget(output_display)

        # Add screen to stacked widget
        self.stackedWidget.addWidget(delete_meaning_list_screen)
        self.stackedWidget.setCurrentWidget(delete_meaning_list_screen)

    def removeListItem(self,list_widget,row): # Function to remove the selected item from the list
        list_widget.takeItem(row)

    def deleteList(self, word, verb, item, output_display, list_widget, row): # Function to link the GUI to the trie functionality
        if item == None:
            QMessageBox.critical(self, 'Error', 'Select a meaning to continue!')
        else:
            text = item.text()
            self.removeListItem(list_widget,row)
            meaning = text
            result = self.resources.delete_meaning_list(word, verb, meaning)
            output_display.setText(result) 

    def insertWord(self, word_entry, verb_entry, meaning_entry, output_display): # Function to link the GUI to the trie functionality
        word = word_entry.text().strip()
        verb = verb_entry.text().strip()
        meaning = meaning_entry.toPlainText().strip()
        if word == '':
            QMessageBox.critical(self, 'Error', 'No word input!')
        elif meaning == '':
            QMessageBox.critical(self, 'Error', 'No meaning input!')
        else:
            result = self.resources.insert_trie(word, meaning, verb)
            output_display.setText(result)

    def getWord(self, word_entry, output_display): # Function to link the GUI to the trie functionality
        word = word_entry.text().strip().upper()
        if word == '':
            QMessageBox.critical(self, 'Error', 'Enter a word to continue!')
        else:
            result = self.resources.in_trie(word)
            output_display.setText(result)

    def deleteWord(self, word_entry, output_display): # Function to link the GUI to the trie functionality
        word = word_entry.text().strip().upper()
        if word == '':
            QMessageBox.critical(self, 'Error', 'Enter a word to continue!')
        else:
            result = self.resources.delete_trie_word(word)
            output_display.setText(result)

    def getLetterWord(self,letter_entry,output_display): # Function to link the GUI to the trie functionality
        letter_text = letter_entry.text().strip()
        letter_entry.clear()
        if len(letter_text) > 1:
            QMessageBox.critical(self, 'Error', 'Can\'t enter more than one letter at a time!')
        elif len(letter_text) == 0:
            QMessageBox.critical(self, 'Error', 'Enter a letter to continue!')
        else:
            self.resources.currentWord += letter_text
            result = self.resources.in_trie_by_letter()
            if "No such words" in result:
                self.resources.currentWord = self.resources.currentWord[:-1]
                QMessageBox.critical(self, 'Error', 'No words for the following letter. Kindly pick a letter from the combinations given')
            else:
                result = ", ".join(result)
                output_display.setText(result)
    
    def reset_clicked(self,output_display): # Function to reset the sequence
        self.resources.currentWord = ''
        output_display.setText('Sequence resetted')

    def finalWord(self,output_display): # Helper function to get the final word
        temp = self.resources.currentWord.upper()
        result = self.resources.in_trie(temp)
        self.resources.currentWord = ''
        output_display.setText(result)

    def showUserSuggestions(self):
        showSuggestion_screen = QWidget() #Creating Widget

        #Initialize elements of the widget
        back_button = QPushButton('Back',showSuggestion_screen)
        addSuggestion_button = QPushButton('Add Suggestion To Dictionary',showSuggestion_screen)
        rejectSuggestion_button = QPushButton('Reject Suggestion',showSuggestion_screen)
        output_display = ScrollLabel()
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)
        Suggestion = QListWidget(self)
        itemList = self.resources.itemsOfList()
        for i in itemList:
            Suggestion.addItem(i)
        Suggestion.setWordWrap(True)
        
        #Connect button to slots
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        addSuggestion_button.clicked.connect(lambda: self.AddSuggestion(Suggestion.currentItem(),output_display,Suggestion,Suggestion.currentRow()))
        rejectSuggestion_button.clicked.connect(lambda: self.RejectSuggestion(Suggestion.currentItem(),Suggestion,Suggestion.currentRow(),output_display))
        
        #Create layout and add elements to it
        showSuggestion_layout = QVBoxLayout(showSuggestion_screen)
        showSuggestion_layout.addWidget(QLabel('List of suggestions:'))
        showSuggestion_layout.addWidget(Suggestion)
        showSuggestion_layout.addWidget(back_button)
        showSuggestion_layout.addWidget(addSuggestion_button)
        showSuggestion_layout.addWidget(rejectSuggestion_button)
        showSuggestion_layout.addWidget(QLabel('Output:'))
        showSuggestion_layout.addWidget(output_display)

        #Add screen to stacked widget
        self.stackedWidget.addWidget(showSuggestion_screen)
        self.stackedWidget.setCurrentWidget(showSuggestion_screen)

    def RejectSuggestion(self,item,Suggestion,row,output_display):
        if item == None:
            output_display.setText('No word selected to be disapproved.')
        else:
            text = item.text()
            self.removeListItem(Suggestion,row)
            temp = text.split('\n')
            for i in range(len(temp)):
                temp[i] = temp[i].split(' ')
            word = " ".join(temp[0][1:])
            verb = " ".join(temp[1][3:])
            meaning = " ".join(temp[2][1:])
            self.resources.delete_meaning_list(word,verb,meaning,"suggest","suggest.csv","suggest")
            self.resources.insert_trie(word,meaning,verb,"reject","rejectedWords.csv","reject")
            output_display.setText("Word successfully disapproved")


    def AddSuggestion(self, item, output_display, Suggestion, row):
        if item == None:
            output_display.setText('No word selected to be added to dictionary')
        else:
            self.removeListItem(Suggestion,row)
            text = item.text()
            temp = text.split('\n')
            for i in range(len(temp)):
                temp[i] = temp[i].split(' ')
            word = " ".join(temp[0][1:])
            verb = " ".join(temp[1][3:])
            meaning = " ".join(temp[2][1:])
            self.resources.delete_meaning_list(word,verb,meaning,"suggest","suggest.csv","suggest")
            result = self.resources.insert_trie(word,meaning,verb)
            output_display.setText(result)

    def goBack(self):
        self.resources.currentWord = ''
        self.stackedWidget.setCurrentIndex(0)


def main(): # Main function to run the application

    dictionary = SharedResources.dictionaryCreate(SharedResources,'english.csv')
    trie = SharedResources.make_trie(SharedResources,dictionary)
    # Initialize the application
    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()

    # Set the style of the application
    stacked_widget.setStyleSheet(open('Style.css').read())

    # Create the screens
    login_screen = LoginScreen(stacked_widget)
    pass_check = passCheck(stacked_widget)
    user_screen = UserScreen(stacked_widget)
    admin_screen = AdminScreen(stacked_widget)

    # Add the screens to the stacked widget
    stacked_widget.addWidget(login_screen)
    stacked_widget.addWidget(pass_check)
    stacked_widget.addWidget(user_screen)
    stacked_widget.addWidget(admin_screen)

    # Initialize the stacked widget
    stacked_widget.setWindowIcon(QIcon('just_a_girl.png'))
    stacked_widget.setWindowTitle('Dictionary Application')
    stacked_widget.setMinimumHeight(stacked_widget.sizeHint().height() + 200)
    stacked_widget.setMinimumWidth(stacked_widget.sizeHint().width() + 100)
    stacked_widget.show()

    # Run the application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

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
    def insert_trie(self, word, meaning, verb, trie, filename, dictionary):
        if trie == "main":
            current_dict = self.trie
        elif trie == "suggest":
            current_dict = self.suggestingTrie
        elif trie == "reject":
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
                self.writeToCSV(word, verb, meaning, filename, dictionary)
                return "Meaning added successfully"
            else:
                return "Meaning already in dictionary!"
        else:
            current_dict["_end"] = [toBeAppended]
            self.writeToCSV(word, verb, meaning, filename, dictionary)
            return "Word entered successfully"

    # Write any changes to the CSV file
    def writeToCSV(self, word, verb, meaning, filename, dictionary):
        with open(filename, "a", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([word, verb, meaning])
        if dictionary == "main":    
            self.dictionary = self.dictionaryCreate(filename)
        elif dictionary == "suggest":
            self.suggestingDictionary = self.dictionaryCreate(filename)
        elif dictionary == "reject":
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
            self.delete_word_from_CS(word)
            return "Word removed successfully."

    # Deletion from the CSV file
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
            # print(UserScreen.dictionary)
            self.dictionary = self.dictionaryCreate('english.csv')
        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', 'CSV file not found.')

    # Delete a meaning of a word in the trie and CSV file   
    def delete_trie_meaning(self, word, verb, meaning,trie='main'):
        if trie == "main":
            current_dict = self.trie
        elif trie == "suggest":
            current_dict = self.suggestingTrie
        elif trie == "reject":
            current_dict = self.rejectedTrie
        temp = word.upper()
        for letter in temp:
            if letter not in current_dict:
                return "No such word in dictionary."
            current_dict = current_dict[letter]
        if "_end" not in current_dict:
            return "No such word in dictionary."
        else:
            print(current_dict)
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
    def delete_meaning_list_(self, word, verb, meaning,trie="main",filename="english.csv",dictionary="main"):
        if trie == "main":
            current_dict = self.trie
        else:
            current_dict = self.suggestingTrie
        for letter in word:
            if letter not in current_dict:
                return "No such word in dictionary."
            current_dict = current_dict[letter]
        check = f"{verb},{meaning}"
        if len(current_dict["_end"]) == 1:
            if check == current_dict["_end"][0]:
                del current_dict["_end"]
                print(word,verb,meaning)
                self.delete_meaning_from_CSV(word,verb,meaning,dictionary,filename)
                return "Meaning and word successfully deleted as there is only one meaning."
            else:
                return "No such word in dictionary"
        else:
            for i in range(len(current_dict["_end"])):
                if check == current_dict["_end"][i]:
                    del current_dict["_end"][i]
                    self.delete_meaning_from_CSV(word,verb,meaning,dictionary,filename)
                    return "Meaning successfully deleted."
    
    # Deletion of the selected meaning from the CSV file
    def delete_meaning_from_CSV(self, word, verb, meaning,dictionary,filename):
        try:
            meaning = meaning.strip('"')
            with open(filename, "r", newline='', encoding='utf-8') as copyf, open("transfer.csv", "w", newline='', encoding='utf-8') as f:
                csv.field_size_limit(int(ct.c_ulong(-1).value // 2))
                reader = csv.reader(copyf)
                writer = csv.writer(f)
                for row in reader:
                    if word != row[0].strip().upper() or verb != row[1] or meaning != row[2]:
                        writer.writerow(row)
            os.replace("transfer.csv", filename)
            if dictionary == "main":
                self.dictionary = self.dictionaryCreate(filename)
            elif dictionary == "suggest":
                self.suggestingDictionary = self.dictionaryCreate(filename)
        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', 'CSV file not found.')                

class ScrollLabel(QScrollArea): # A class to create a scrollable label used in the UserScreen and AdminScreen classes
 
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
        user_button.clicked.connect(self.showUserScreen)
        admin_button.clicked.connect(self.passCheck)

        # Layout helps us define the order of the interface. QHBox means all items on the screen would be horizontally placed.
        layout = QHBoxLayout(main_screen)
        label = QLabel('Choose User Type:',main_screen)
        label.adjustSize()
        # Adds all the widgets to the layout
        layout.addWidget(user_button,0)
        layout.addWidget(admin_button,0)
        
        # Adds the screen onto the stack and sets the current screen
        self.stackedWidget.addWidget(main_screen)
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.stackedWidget)

    # Defining the series of the screens in the stacked widget
    def passCheck(self):
        self.stacked_widget.setCurrentIndex(1)

    def showUserScreen(self):
        self.stacked_widget.setCurrentIndex(2)

    def showAdminScreen(self):
        self.stacked_widget.setCurrentIndex(3)

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
        back_button.clicked.connect(self.goBack)

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
    def goBack(self):
        self.stacked_widget.setCurrentIndex(0)

class UserScreen(QWidget):
    
    # Constructor
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.resources = SharedResources()
        self.dictionary = self.resources.dictionary
        self.trie = self.resources.trie
        self.suggestingDictionary = self.resources.suggestingDictionary
        self.suggestingTrie = self.resources.suggestingTrie
        self.rejectedDictionary = self.resources.rejectedDictionary
        self.rejectedTrie = self.resources.rejectedTrie
        self.currentWord = ''
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
        back_button.clicked.connect(self.goBack)

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
        output_display = ScrollLabel(self)
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        # Connect buttons to slots
        getLetter_button.clicked.connect(lambda: self.getLetterWord(letter_entry, output_display))
        getFinalWord_button.clicked.connect(lambda: self.finalWord(output_display))
        back_button.clicked.connect(lambda: self.delete_clicked())
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
        output_display = ScrollLabel(self)
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
        result = self.resources.in_trie(word)
        output_display.setText(result)

    def getLetterWord(self,letter_entry,output_display): # Function to link the GUI to the trie functionality
        letter_entry = letter_entry.text().strip()
        if len(letter_entry) > 1:
            output_display.setText("Invalid input. Enter one letter at a time.")
        else:
            self.currentWord += letter_entry
            letter_entry = self.currentWord
            result = self.resources.in_trie_by_letter(letter_entry)
            if "No such words" in result:
                self.currentWord = self.currentWord[:-1]
                if "No words with the" not in output_display.text():
                    output_display.setText('No words with the inputted letter. Kindly pick a letter from one of the following combinations\n' + output_display.text())
            else:
                result = ", ".join(result)
                output_display.setText(result)

    def finalWord(self,output_display): # Helper function to get the final word
        temp = self.currentWord.upper()
        result = self.resources.in_trie(temp)
        self.currentWord = ''
        output_display.setText(result)

    def getNewWordScreen(self):
        getNewWord_screen = QWidget() #Create Widget

       #Initialize elements of wthe widget        
        word_entry = QLineEdit(getNewWord_screen)
        verb_entry = QLineEdit(getNewWord_screen)
        meaning_entry = QLineEdit(getNewWord_screen)
        entry_button = QPushButton('Suggest Word',getNewWord_screen)
        back_button = QPushButton('Back',getNewWord_screen)
        output_display = ScrollLabel(self)
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        #Connect buttons to slots
        entry_button.clicked.connect(lambda: self.processSuggestion(word_entry,verb_entry,meaning_entry,output_display))
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        #Create layout and add elements to it
        getNewWord_layout = QVBoxLayout(getNewWord_screen)
        getNewWord_layout.addWidget(QLabel('Word:'))
        getNewWord_layout.addWidget(word_entry)
        getNewWord_layout.addWidget(QLabel('Verb:'))
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
        result = self.resources.delete_trie_meaning(word,verb,meaning)      
        if type(result) == list:
            for i in result:
                if i == meaning:
                    output_display.setText('Word already exists in dictionary!')
                    return
        else:
            forbidden = self.resources.delete_trie_meaning(word,verb,meaning,'reject')
            if type(forbidden) == list:
                for i in forbidden:
                    if i == meaning:
                        output_display.setText('The following word has already been rejected and can\'t be added into the dictionary.')
                        return
            else:
                output = self.resources.insert_trie(word,meaning,verb,"suggest",'suggest.csv','suggest')
                if output == "Meaning already in dictionary!":
                    output_display.setText('This word is already under review!')
                else:
                    output_display.setText('Suggestion received! Thanks for contributing. We will review your input and insert it into the dictionary if applicable!')


    def delete_clicked(self): # Function to delete the meaning selected
        self.stackedWidget.setCurrentIndex(0)
        self.currentWord = ''

    def reset_clicked(self,output_display): # Function to reset the sequence
        self.currentWord = ''
        output_display.setText('Sequence resetted!')

    def goBack(self): # Function to go back to the previous screen
        self.stacked_widget.setCurrentIndex(0)

class AdminScreen(QWidget):

    # Constructor
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.resources = SharedResources()
        self.dictionary = self.resources.dictionary
        self.trie = self.resources.trie
        self.suggestingDictionary = self.resources.suggestingDictionary
        self.suggestingTrie = self.resources.suggestingTrie
        self.rejectedDictionary = self.resources.rejectedDictionary
        self.rejectedTrie = self.resources.rejectedTrie
        self.currentWord = ''
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
        back_button.clicked.connect(self.goBack)

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
        self.dictionary = self.resources.dictionary
        self.trie = self.resources.trie
        QMessageBox.information(self, 'Success', 'Dictionary resetted')

    def getLetterScreen(self):

        getLetter_screen = QWidget() # Creating widget

        # Initialize elements of the widget
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
        output_display = ScrollLabel(self)
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        # Connect buttons to slots
        insert_button.clicked.connect(lambda: self.insertWord(word_entry, verb_entry, meaning_entry, output_display))
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        # Create layout and add elements to it
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

        # Add screen to stacked widget
        self.stackedWidget.addWidget(insert_screen)
        self.stackedWidget.setCurrentWidget(insert_screen)

    def showGetScreen(self):

        get_screen = QWidget() # Creating widget
        
        # Initialize elements of the widget
        word_entry = QLineEdit(get_screen)
        get_button = QPushButton('Get', get_screen)
        back_button = QPushButton('Back', get_screen)
        output_display = ScrollLabel(self)
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
        output_display = ScrollLabel(self)
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
        output_display = ScrollLabel(self)
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        # Connect buttons to slots
        delete_button.clicked.connect(lambda: self.deleteMeaning(word_entry, verb_entry, meaning_entry , output_display))
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        # Create layout and add elements to it
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

        # Add screen to stacked widget
        self.stackedWidget.addWidget(delete_meaning_screen)
        self.stackedWidget.setCurrentWidget(delete_meaning_screen)

    def deleteMeaning(self, word_entry, verb_entry, meaning_entry, output_display): # Function to link the GUI to the trie functionality
        word = word_entry.text().strip().upper()
        verb = verb_entry.text().strip()
        meaning = meaning_entry.text().strip()
        result = self.resources.delete_trie_meaning(word, verb, meaning)
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
        output_display = ScrollLabel(self)
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)

        # Connect buttons to slots
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        select_meaning.clicked.connect(lambda: self.deleteList(word,verb,list_widget.currentItem().text(),output_display, list_widget, list_widget.currentRow()))

        # Create layout and add elements to it
        delete_meaning_layout = QVBoxLayout(delete_meaning_list_screen)
        delete_meaning_layout.addWidget(QLabel('Select a meaning from the list'))
        delete_meaning_layout.addWidget(list_widget)
        delete_meaning_layout.addWidget(back_button)
        delete_meaning_layout.addWidget(select_meaning)
        delete_meaning_layout.addWidget(output_display)

        # Add screen to stacked widget
        self.stackedWidget.addWidget(delete_meaning_list_screen)
        self.stackedWidget.setCurrentWidget(delete_meaning_list_screen)

    def removeListItem(self,list_widget,row): # Function to remove the selected item from the list
        list_widget.takeItem(row)

    def deleteList(self, word, verb, item, output_display, list_widget, row): # Function to link the GUI to the trie functionality
        self.removeListItem(list_widget,row)
        meaning = item
        result = self.resources.delete_meaning_list_(word, verb, meaning)
        output_display.setText(result) 

    def insertWord(self, word_entry, verb_entry, meaning_entry, output_display): # Function to link the GUI to the trie functionality
        word = word_entry.text().strip()
        verb = verb_entry.text().strip()
        meaning = meaning_entry.toPlainText().strip()
        
        if word == '' or meaning == '':
            output_display.setText('Word and meaning cannot be empty.')
            return
        
        result = self.resources.insert_trie(word, meaning, verb,'main','english.csv','main')
        
        output_display.setText(result)

    def getWord(self, word_entry, output_display): # Function to link the GUI to the trie functionality
        word = word_entry.text().strip().upper()
        result = self.resources.in_trie(word)
        output_display.setText(result)

    def deleteWord(self, word_entry, output_display): # Function to link the GUI to the trie functionality
        word = word_entry.text().strip().upper()
        result = self.resources.delete_trie_word(word)
        output_display.setText(result)

    def delete_clicked(self): # Function to delete the meaning selected
        self.stackedWidget.setCurrentIndex(0)
        self.currentWord = ''

    def getLetterWord(self,letter_entry,output_display): # Function to link the GUI to the trie functionality
        letter_entry = letter_entry.text().strip()
        if len(letter_entry) > 1:
            output_display.setText("Invalid input. Enter one letter at a time.")
        else:
            self.currentWord += letter_entry
            letter_entry = self.currentWord
            result = self.resources.in_trie_by_letter(letter_entry)
            if "No such words" in result:
                self.currentWord = self.currentWord[:-1]
                if "No words with the" not in output_display.text():
                    output_display.setText('No words with the inputted letter. Kindly pick a letter from one of the following combinations\n' + output_display.text())
            else:
                result = ", ".join(result)
                output_display.setText(result)
    
    def reset_clicked(self,output_display): # Function to reset the sequence
        self.currentWord = ''
        output_display.setText('Sequence resetted')

    def finalWord(self,output_display): # Helper function to get the final word
        temp = self.currentWord.upper()
        result = self.resources.in_trie(temp)
        self.currentWord = ''
        output_display.setText(result)

    def showUserSuggestions(self):
        showSuggestion_screen = QWidget() #Creating Widget

        #Initialize elements of the widget
        back_button = QPushButton('Back',showSuggestion_screen)
        addSuggestion_button = QPushButton('Add Suggestion To Dictionary',showSuggestion_screen)
        rejectSuggestion_button = QPushButton('Reject Suggestion',showSuggestion_screen)
        output_display = ScrollLabel(self)
        output_display.setFrameStyle(QFrame.Box)
        output_display.setLineWidth(0)
        Suggestion = QListWidget(self)
        self.suggestingDictionary = self.resources.suggestingDictionary
        print(self.suggestingDictionary)
        for i in self.suggestingDictionary:
            for j in range(len(self.suggestingDictionary[i])):
                temp = self.suggestingDictionary[i][j].split(',')
                verb = temp[0]
                meaning = " ".join(temp[1:])
                toAppend = "Word: " + i + "\n" + "Verb: " + verb + "\n" + "Meaning: " + meaning
                Suggestion.addItem(toAppend)
                break
        Suggestion.setWordWrap(True)

        #Connect button to slots
        back_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        addSuggestion_button.clicked.connect(lambda: self.AddSuggestion(Suggestion.currentItem().text(),output_display,Suggestion,Suggestion.currentRow()))
        rejectSuggestion_button.clicked.connect(lambda: self.RejectSuggestion(Suggestion.currentItem().text(),Suggestion,Suggestion.currentRow(),output_display))
        #Creat layout and add elements to it
        showSuggestion_layout = QVBoxLayout(showSuggestion_screen)
        showSuggestion_layout.addWidget(QLabel('List of suggestions:'))
        showSuggestion_layout.addWidget(Suggestion)
        showSuggestion_layout.addWidget(back_button)
        showSuggestion_layout.addWidget(addSuggestion_button)
        showSuggestion_layout.addWidget(rejectSuggestion_button)
        showSuggestion_layout.addWidget(output_display)

        #Add screen to stacked widget
        self.stackedWidget.addWidget(showSuggestion_screen)
        self.stackedWidget.setCurrentWidget(showSuggestion_screen)

    def RejectSuggestion(self,item,Suggestion,row,output_display):
        self.removeListItem(Suggestion,row)

        temp = item.split('\n')
        for i in range(len(temp)):
            temp[i] = temp[i].split(' ')
        word = " ".join(temp[0][1:])
        verb = " ".join(temp[1][1:])
        meaning = " ".join(temp[2][1:])
        self.resources.delete_meaning_list_(word,verb,meaning,"suggest","suggest.csv","suggest")
        self.resources.insert_trie(word,meaning,verb,"reject","rejectedWords.csv","reject")
        output_display.setText("Word successfully disapproved")


    def AddSuggestion(self, item, output_display, Suggestion, row):
        self.removeListItem(Suggestion,row)
        temp = item.split('\n')
        for i in range(len(temp)):
            temp[i] = temp[i].split(' ')
        word = " ".join(temp[0][1:])
        verb = " ".join(temp[1][1:])
        meaning = " ".join(temp[2][1:])
        self.resources.delete_meaning_list_(word,verb,meaning,"suggest","suggest.csv","suggest")
        # self.resources.insert_trie()
        result = self.resources.insert_trie(word,meaning,verb,'main','english.csv','main')
        output_display.setText(result)

    def goBack(self): # Function to go back to the previous screen
        self.stacked_widget.setCurrentIndex(0)

def main(): # Main function to run the application

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
    stacked_widget.setWindowTitle('Dictionary Application')
    stacked_widget.setFixedHeight(stacked_widget.sizeHint().height() + 200)
    stacked_widget.setFixedWidth(stacked_widget.sizeHint().width() + 100)
    stacked_widget.show()

    # Run the application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

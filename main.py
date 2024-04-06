import csv
import ctypes as ct
#CSV to dictionary word and meaning
def dictionaryCreate(filename):
    countX = 127338
    countY = 139824
    with open(filename) as f:
        data = f.readlines()
    for i in range(len(data)):
        if i >= countX and i <= countY:
            data[i] = data[i].strip().split(' ')
        else:
            #User-defined words from 188510
            data[i] = data[i].strip().split(',')
    dict = {}
    for i in range(1,len(data)):
        word = data[i].pop(0)
        word = word.upper()
        if word in dict:
            dict[word].append(','.join(data[i]))
        else:
            dict[word] = [','.join(data[i])]
    return dict


#Conversion from dictionary to trie
def make_trie(dictionary):
    words = []
    for i in dictionary:
        words.append(i)
    root = {}
    for word in words:
        current_dict = root
        for letter in word:
            if letter not in current_dict:
                current_dict[letter] = {}
            current_dict = current_dict[letter]
        current_dict["_end"] = dictionary[word]
    return root



#get function
def in_trie(trie, word, dictionary, returnAfterInsert = False):
    temp = word.upper()
    current_dict = trie
    for letter in temp:
        if letter not in current_dict:
            takeChoice = input("No such word in dictionary. Want to insert a new word?")
            if takeChoice.upper() == "YES":
                verb = input("What part of speech is it? (Verb,Noun,adjective,preposition,etc) Can skip if don't know: ")
                meaning = input("Enter your meaning: ")
                trie = insert_trie(trie,word,meaning,verb,dictionary)
                return in_trie(trie,word,dictionary,True)
            else:
                return "Exiting..."
        current_dict = current_dict[letter]
    if "_end" in current_dict:
        for i in range(len(current_dict["_end"])):
            if current_dict["_end"][i][0] == ",":
                current_dict["_end"][i] = current_dict["_end"][i][1:]
        str1 = word + ": " + str(current_dict["_end"])
        if returnAfterInsert:
            return str1
        else:
            print(str1)
            flag = False
            while not flag:
                choice = input("Is this the meaning you are lookin for?: ")
                if choice.upper() == "YES":
                    return "Great! Exiting program.."
                elif choice.upper() == "NO":
                    print("Add your own meaning to this word:")
                    verb = input("What part of speech is it? (Verb,Noun,adjective,preposition,etc) Can skip if don't know: ")
                    meaning = input("Enter your meaning: ")
                    trie = insert_trie(trie,word,meaning,verb,dictionary)
                    str1 = word + ": " + str(current_dict["_end"])
                    return str1
                else:
                    print("Invalid Input: Enter \"yes\" or \"no\" to continue.")

    else:
        takeChoice = input("No such word in dictionary. Want to insert a new word?")
        if takeChoice.upper() == "YES":
            verb = input("What part of speech is it? (Verb,Noun,adjective,preposition,etc) Can skip if don't know: ")
            meaning = input("Enter your meaning: ")
            trie = insert_trie(trie,word,meaning,verb,dictionary)
            str1 = in_trie(trie,word,dictionary,True)
            return str1
        else:
            return "Exiting..."

#Adds the words user has entered into the csv file in order to save them permenatnely (even for the next time the program runs)
def writeToCSV(word,verb,meaning,trie,dictionary):
    with open("english.csv","a",newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([word,verb,meaning])
    dictionary = dictionaryCreate("english.csv")
    trie = make_trie(dictionary)
    return (trie,dictionary)

#Insert function
def insert_trie(trie,word,meaning,verb,dictionary):
    temp = word.upper()
    current_dict = trie
    flag = True
    for letter in temp:
        if letter not in current_dict:
            flag = False
            break
        current_dict = current_dict[letter]
    toBeAppended = verb + "," + meaning
    if flag:
        if "_end" in current_dict:
            print("Word already exists")
            if toBeAppended not in current_dict["_end"]:
                current_dict["_end"].append(toBeAppended)
                temp = writeToCSV(word,verb,meaning,trie,dictionary)
                trie , dictionary = temp[0], temp[1]
                print("Meaning added succesfully")
                return trie
            else:
                return "Meaning already in dictionary!"
        else:
            current_dict["_end"] = [toBeAppended]
            temp = writeToCSV(word,verb,meaning,trie,dictionary)
            trie , dictionary = temp[0], temp[1]
            print("Word entered succesfully")
            return trie
    else:
        current_dict = trie
        for letter in temp:
            if letter not in current_dict:
                current_dict[letter] = {}
            current_dict = current_dict[letter]
        current_dict["_end"] = [toBeAppended]
        temp = writeToCSV(word,verb,meaning,trie,dictionary)
        trie , dictionary = temp[0], temp[1]
        print("Word entered succesfully")
        return trie
    
def delete_word_from_CS(word,trie,dictionary):
    with open("english.csv","r") as copyf, open("transfer.csv","w",newline='') as f:
        reader = csv.reader(copyf)
        commacsvwriter = csv.writer(f)
        csv.field_size_limit(int(ct.c_ulong(-1).value // 2))
        for i, rows in enumerate(reader):
            if word == rows[0]:
                continue
            else:
                commacsvwriter.writerow([rows[0],rows[1],rows[2]])
    with open("transfer.csv","r") as copyf, open("english.csv","w",newline='') as f:
        reader = csv.reader(copyf)
        commacsvwriter = csv.writer(f)
        csv.field_size_limit(int(ct.c_ulong(-1).value // 2))
        for i, rows in enumerate(reader):
            commacsvwriter.writerow([rows[0],rows[1],rows[2]])
    dictionary = dictionaryCreate("english.csv")
    trie = make_trie(dictionary)
    return (trie,dictionary)

def delete_trie_word(trie,word,dicitionary):
    temp = word.upper()
    current_dict = trie
    for letter in temp:
        if letter not in current_dict:
            takeChoice = input("No such word in dictionary. Want to insert a new word?")
            if takeChoice.upper() == "YES":
                meaning = input("Enter your meaning: ")
                trie = insert_trie(trie,word,meaning,dictionary)
                return in_trie(trie,word,dictionary,True)
            else:
                return "Exiting..."
        current_dict = current_dict[letter]
    if "_end" not in current_dict:
        takeChoice = input("No such word in dictionary. Want to insert a new word?")
        if takeChoice.upper() == "YES":
            meaning = input("Enter your meaning: ")
            trie = insert_trie(trie,word,meaning,dictionary)
            str1 = in_trie(trie,word,dictionary,True)
            return str1
        else:
            return "Exiting..."
    else:
        del current_dict["_end"]
        delete_word_from_CS(word,trie,dictionary)
        return "Word removed succesfully"

def reset(dictionary,trie):
    with open("english.csv","w",newline='') as f:
        commacsvwriter = csv.writer(f)
        with open("original.csv","r") as copyf:
            csv.field_size_limit(int(ct.c_ulong(-1).value // 2))
            reader = csv.reader(copyf)
            for i, rows in enumerate(reader):
                if i == 1 or i == 128450:
                    print(rows)
                commacsvwriter.writerow([rows[0],rows[1],rows[2]])
    dictionary = dictionaryCreate("english.csv")
    trie = make_trie(dictionary)
    return (trie,dictionary)
    
def delete_meaning_from_CSV(word,verb,meaning,dictionary,trie):
    with open("english.csv","r") as copyf, open("transfer.csv","w",newline='') as f:
        reader = csv.reader(copyf)
        commacsvwriter = csv.writer(f)
        csv.field_size_limit(int(ct.c_ulong(-1).value // 2))
        meaning = meaning.strip('"')
        for i, rows in enumerate(reader):
            if word == rows[0] and verb == rows[1] and meaning == rows[2]:
                continue
            else:
                commacsvwriter.writerow([rows[0],rows[1],rows[2]])
    with open("transfer.csv","r") as copyf, open("english.csv","w",newline='') as f:
        reader = csv.reader(copyf)
        commacsvwriter = csv.writer(f)
        csv.field_size_limit(int(ct.c_ulong(-1).value // 2))
        for i, rows in enumerate(reader):
            commacsvwriter.writerow([rows[0],rows[1],rows[2]])
    trie = make_trie(dictionary)
    return (trie,dictionary)

def delete_trie_word_meaning(trie,word,meaning,verb,dictionary):
    temp = word.upper()
    current_dict = trie
    for letter in temp:
        if letter not in current_dict:
            takeChoice = input("No such word in dictionary. Want to insert a new word?")
            if takeChoice.upper() == "YES":
                meaning = input("Enter your meaning: ")
                trie = insert_trie(trie,word,meaning,dictionary)
                return in_trie(trie,word,dictionary,True)
            else:
                return "Exiting..."
        current_dict = current_dict[letter]
    if "_end" not in current_dict:
        takeChoice = input("No such word in dictionary. Want to insert a new word?")
        if takeChoice.upper() == "YES":
            meaning = input("Enter your meaning: ")
            trie = insert_trie(trie,word,meaning,dictionary)
            str1 = in_trie(trie,word,dictionary,True)
            return str1
        else:
            return "Exiting..."
    else:
        if len(current_dict["_end"]) == 1:
            flagInput = False
            while not flagInput:
                print(word,"only contains the one meaning. Deleting this meaning would also delete the word as there are no other meanings!. Continue?")
                userInput = input()
                if userInput.upper() == "YES":
                    if verb + "," + meaning == current_dict["_end"][0]:
                        del current_dict["_end"]
                        temp = delete_meaning_from_CSV(word,verb,meaning,dictionary,trie)
                        trie, dictionary = temp[0], temp[1]
                        return "Meaning and word successfully deleted."
                    else:
                        return "No such meaning exists."
                elif userInput.upper() == "NO":
                    return "Exiting program.."
                else:
                    print("Invalid input. Answer with either yes or no")
        else:
            for i in range(len(current_dict["_end"])):
                check = verb + "," + meaning
                if check == current_dict["_end"][i]:
                    del current_dict["_end"][i]
                    temp = delete_meaning_from_CSV(word,verb,meaning,dictionary,trie)
                    trie, dictionary = temp[0], temp[1]
                    # print(word + ": " + str(current_dict["_end"]))
                    return "Meaning successfully deleted."
            return "No such meaning exists."


dictionary = dictionaryCreate('english.csv')
trie = make_trie(dictionary)
flag = True
while flag:
    logInFlag = False
    while not logInFlag:
        initalInput = int(input("Select interface:\n1)Admin\n2)User\n"))
        if initalInput == 1:
            passFlag = False
            while not passFlag:
                userInput = input("Enter password: ")
                passStore = "hehe"
                if userInput == passStore:
                    passFlag = True
                    operationFlag = False
                    while not operationFlag:
                        userSelect = int(input("Select operation:\n1)Reset dictionary\n"))
                        if userSelect == 1:
                            temp = reset(dictionary,trie)
                            trie, dictionary = temp[0], temp[1]
                            operationFlag = True
                            print("Dictionary resetted!")
                        else:
                            print("Invalid input. Enter 1 to continue")
                else:
                    print("Wrong password")
                    choice = int(input("Select 1 or 2:\n1)Try again\n2)Main meanu\n3)Exit program\n")) 
                    if choice == 2:
                        passFlag = True
                    elif choice == 3:
                        print("Exiting...")
                        passFlag = True
                        logInFlag = True
                        flag = False
            flagInput = False
            while not flagInput and initalInput != 1:
                choice = input("Exit the program?: ")
                if choice.upper() == "YES":
                    logInFlag = True
                    flagInput = True
                    flag = False
                elif choice.upper() == "NO":
                    flagInput = True
                else:
                    print("Invalid input. Answer with either yes or no")
        elif initalInput == 2:   
            mainFlag = False
            while not mainFlag:
                userInput = int(input("Select your operation by entering the number:\n1)Insert\n2)Get\n3)Delete\n4)Main Menu\n5)Exit\n"))
                if userInput == 1:
                    word = input("Enter your word: ")
                    verb = input("What part of speech is it? (Verb,Noun,adjective,preposition,etc). Can skip if don't know: ")
                    meaning = input("Enter your meaning: ")
                    temp = insert_trie(trie,word,meaning,verb,dictionary)
                    if type(temp) != str:
                        trie = temp
                        print(in_trie(trie,word,dictionary,True))
                    else:
                        print(temp)
                elif userInput == 2:
                    word = input("Enter your word: ")
                    print(in_trie(trie,word,dictionary))
                elif userInput == 3:
                    select = int(input("Choose your operation:\n1)Delete the word\n2)Delete a meaning of the word\n"))
                    flagCheck = False
                    while not flagCheck:
                        if select == 1:
                            word = input("Enter your word: ")
                            print(delete_trie_word(trie,word,dictionary))
                            flagCheck = True
                        elif select == 2:
                            word = input("Enter your word: ")
                            verb = input("What part of speech is it? (Verb,Noun,adjective,preposition,etc). Can skip if don't know: ")
                            meaning = input("Enter your meaning: ")
                            print(delete_trie_word_meaning(trie,word,meaning,verb,dictionary))
                            flagCheck = True
                        else:
                            print("Invalid input. Answer with 1 or 2")
                elif userInput == 4:
                    mainFlag = True
                elif userInput == 5:
                    print("Exiting..")
                    mainFlag = True
                    logInFlag = True
                    flag = False
                else:
                    print("Invalid input. Enter a number between 1 and 3.")
                    continue
        else:
            print("Invalid input. Enter 1 or 2 to continue")

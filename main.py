#CSV to dictionary word and meaning
def dictionary(filename):
    with open(filename) as f:
        data = f.readlines()
    for i in range(len(data)):
        if i >= 127357 and i <= 139844:
            data[i] = data[i].strip().split(' ')
        else:
            data[i] = data[i].strip().split(',')
    dict = {}
    for i in range(1,len(data)):
        word = data[i].pop(0)
        word = word.upper()
        if word in dict:
            dict[word].append(','.join(data[i]))
        else:
            dict[word] = [','.join(data[i])]
    lst = list()
    for i in dict:
        if "-" == i[0] or "'" in i or "/" in i or "." in i or "1" in i or "(" in i or ")" in i:
            lst.append(i)
    for i in range(len(lst)):
        del dict[lst[i]]
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
def in_trie(trie, word, returnAfterInsert = False):
    temp = word.upper()
    current_dict = trie
    for letter in temp:
        if letter not in current_dict:
            takeChoice = input("No such word in dictionary. Want to insert a new word?")
            if takeChoice.upper() == "YES":
                meaning = input("Enter your meaning: ")
                trie = insert_trie(trie,word,meaning)
                return in_trie(trie,word,True)
            else:
                return "Exiting..."
        current_dict = current_dict[letter]
    if "_end" in current_dict:
        if current_dict["_end"][0][0] == ",":
            str1 = word + ": " + current_dict["_end"][0][1:]
        else:
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
                    meaning = input("Enter your meaning: ")
                    trie = insert_trie(trie,word,meaning)
                    str1 = word + ": " + str(current_dict["_end"])
                    return str1
                else:
                    print("Invalid Input: Enter \"yes\" or \"no\" to continue.")

    else:
        takeChoice = input("No such word in dictionary. Want to insert a new word?")
        if takeChoice.upper() == "YES":
            meaning = input("Enter your meaning: ")
            trie = insert_trie(trie,word,meaning)
            str1 = in_trie(trie,word,True)
            return str1
        else:
            return "Exiting..."

#Insert function
def insert_trie(trie,word,meaning):
    temp = word.upper()
    current_dict = trie
    flag = True
    for letter in temp:
        if letter not in current_dict:
            flag = False
            break
        current_dict = current_dict[letter]
    if flag:
        if "_end" in current_dict:
            print("Word already exists")
            current_dict["_end"].append(meaning)
            print("Meaning added succesfully")
            return trie
        else:
            current_dict["_end"] = [meaning]
            print("Word entered succesfully")
            return trie
    else:
        current_dict = trie
        for letter in temp:
            if letter not in current_dict:
                current_dict[letter] = {}
            current_dict = current_dict[letter]
        current_dict["_end"] = [meaning]
        print("Word entered succesfully")
        return trie
    
def delete_trie_word(trie,word):
    temp = word.upper()
    current_dict = trie
    for letter in temp:
        if letter not in current_dict:
            takeChoice = input("No such word in dictionary. Want to insert a new word?")
            if takeChoice.upper() == "YES":
                meaning = input("Enter your meaning: ")
                trie = insert_trie(trie,word,meaning)
                return in_trie(trie,word,True)
            else:
                return "Exiting..."
        current_dict = current_dict[letter]
    if "_end" not in current_dict:
        takeChoice = input("No such word in dictionary. Want to insert a new word?")
        if takeChoice.upper() == "YES":
            meaning = input("Enter your meaning: ")
            trie = insert_trie(trie,word,meaning)
            str1 = in_trie(trie,word,True)
            return str1
        else:
            return "Exiting..."
    else:
        del current_dict["_end"]
        return "Word removed succesfully"

def delete_trie_word_meaning(trie,word,meaning):
    temp = word.upper()
    current_dict = trie
    for letter in temp:
        if letter not in current_dict:
            takeChoice = input("No such word in dictionary. Want to insert a new word?")
            if takeChoice.upper() == "YES":
                meaning = input("Enter your meaning: ")
                trie = insert_trie(trie,word,meaning)
                return in_trie(trie,word,True)
            else:
                return "Exiting..."
        current_dict = current_dict[letter]
    if "_end" not in current_dict:
        takeChoice = input("No such word in dictionary. Want to insert a new word?")
        if takeChoice.upper() == "YES":
            meaning = input("Enter your meaning: ")
            trie = insert_trie(trie,word,meaning)
            str1 = in_trie(trie,word,True)
            return str1
        else:
            return "Exiting..."
    else:
        if len(current_dict["_end"]) == 1:
            flagInput = False
            while not flagInput:
                print(word,"only contains the meaning you have asked to delete. Deleting this meaning would also delete the word as there are no other meanings!. Continue?")
                userInput = input()
                if userInput.upper() == "YES":
                    del current_dict["_end"]
                    return "Meaning and word successfully deleted."
                elif userInput.upper() == "NO":
                    return "Exiting program.."
                else:
                    print("Invalid input. Answer with either yes or no")
        else:
            for i in range(len(current_dict["_end"])):
                if current_dict["_end"][i] == meaning:
                    del current_dict["_end"][i]
                    print(word + ": " + str(current_dict["_end"]))
                    return "Meaning successfully deleted."
            return "No such meaning exists."


dictionary = dictionary('english.csv')
trie = make_trie(dictionary)
flag = True
while flag:
    mainFlag = False
    while not mainFlag:
        userInput = int(input("Select your operation by entering the number:\n1)Insert\n2)Get\n3)Delete\n"))
        if userInput == 1:
            word = input("Enter your word: ")
            meaning = input("Enter your meaning: ")
            trie = insert_trie(trie,word,meaning)
            print(in_trie(trie,word, True))
            mainFlag = True
        elif userInput == 2:
            word = input("Enter your word: ")
            print(in_trie(trie,word))
            mainFlag = True
        elif userInput == 3:
            select = int(input("Choose your operation:\n1)Delete the word\n2)Delete a meaning of the word\n"))
            flagCheck = False
            while not flagCheck:
                if select == 1:
                    word = input("Enter your word: ")
                    print(delete_trie_word(trie,word))
                    flagCheck = True
                    mainFlag = True
                elif select == 2:
                    word = input("Enter your word: ")
                    meaning = input("Enter your meaning: ")
                    print(delete_trie_word_meaning(trie,word,meaning))
                    flagCheck = True
                    mainFlag = True
                else:
                    print("Invalid input. Answer with 1 or 2")
        else:
            print("Invalid input. Enter a number between 1 and 3.")
    flagInput = False
    while not flagInput:
        choice = input("Exit the program?: ")
        if choice.upper() == "YES":
            flagInput = True
            flag = False
        elif choice.upper() == "NO":
            flagInput = True
        else:
            print("Invalid input. Answer with either yes or no")

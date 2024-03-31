def dictionary(filename):
    with open(filename) as f:
        data = f.readlines()
    for i in range(len(data)):
        if i >= 127358 and i <= 139845:
            data[i] = data[i].strip().split(' ')
        else:
            data[i] = data[i].strip().split(',')
        

    dict = {}
    for i in range(len(data)):
        word = data[i].pop(0)
        if word in dict:
            dict[word].append(','.join(data[i]))
        else:
            dict[word] = [','.join(data[i])]
    print(dict['Rytina'])

dictionary('english.csv')
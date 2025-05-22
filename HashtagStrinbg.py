def Hashtag_String(string):
    """
    This function takes a string and returns a new string with the first letter of each word capitalized and prefixed with a hashtag.
    """
    for char in string:
        if char.isalnum() or char.isspace():
            continue
        else:
            string = string.replace(char, '')
    
    string = string.strip()
    l = string.split(" ")
    hashList = []
    for i in l:
        hashList.append(i.capitalize())

    hashtag_string = '#'
    for i in hashList:
        hashtag_string += i
    
    return hashtag_string

s=input("Enter a string: ")
print(Hashtag_String(s))
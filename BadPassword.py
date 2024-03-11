import requests
import pandas as pd
import numpy as np
import re
from string import punctuation
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud

#exporting the files
url = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-no-swears.txt"
response = requests.get(url)

with open("google-10000-english-no-swears.txt", "wb") as file:
    file.write(response.content)


url = "https://gist.githubusercontent.com/kingabzpro/d22c3e672083a4fa59c33faf132d116f/raw/377dd517f2dd33e2ea03dda3ba3db03321ac54db/synthetic_username_password.csv"
response = requests.get(url)

with open("synthetic_username_password.csv", "wb") as file:
    file.write(response.content)

url = "https://gitlab.com/kalilinux/packages/seclists/-/raw/kali/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt"
response = requests.get(url)

with open("10-million-password-list-top-1000000.txt", "wb") as file:
    file.write(response.content)



users = pd.read_csv("/Users/flavianirere/Desktop/workspace/KeyLogger.PythonTraining/synthetic_username_password.csv")
print("Number of samples = "+str(users.size))
# Taking a look at the 6 first users
users.head(6)

print("Number of missing values : \n\n"+str(users.isna().sum()))


users['length'] = users['password'].str.len()
# Checking for short length passwords
users['too_short'] = users['length']<8
print("Counting and printing the number of users with too short passwords :" +\
 str(users['too_short'].sum()))
# The  first 6 rows
users.head(6)

# loading top 1000000 most used words on internet.
common_passwords = pd.read_csv("10-million-password-list-top-1000000.txt",
                              header=None)


# Checking most commonly used passwords
users['common_password'] = users['password'].str.lower().isin( common_passwords)


print("Number of users using common passwords :"+str(sum(users['common_password'])))


# Reading in a list of the 10000 most common words
words = pd.read_csv("google-10000-english-no-swears.txt",
                              header=None)

users['common_word'] = users['password'].str.lower().isin(words)


print("The number of users using common words as passwords :"+str(sum(users['common_word'])))


# Saperating firstname and last name from your username
users['first_name'] = users['user_name'].str.extract(r'(^\w+)', expand=False)
users['last_name'] = users['user_name'].str.extract(r'(\w+$)', expand=False)

# Checking Username in your password
users['uses_name'] = (users['password'] == users['first_name'])|\
                     (users['password'] == users['last_name'])

print("The number of users using names as passwords :"+str(sum(users['uses_name'])))

### Flagging the users with passwords with >= 4 repeats
users['too_many_repeats'] = users['password'].str.contains(r'(.)\1\1\1\1\1');

# Taking a look at the users with too many repeats
print("Number of passwords with > 4 repeat character :"+str(users['too_many_repeats'].sum()));


#Password should have at least one numerical
#Password should have at least one uppercase letter
#Password should have at least one lowercase letter
#Password should have at least one of the special characters


def digital(data):  
    val = True
    if not any(char.isdigit() for char in data["password"]):
        val = False
    else:
        val = True
    return val
def upper(data):  
    val = True
    if not any(char.isupper() for char in data["password"]):
        val = False
    else:
        val = True
    return val

def lower(data):  
    val = True
    if not any(char.islower() for char in data["password"]):
        val = False
    else:
        val = True
    return val

def special(data): 
    SpecialSym = set(punctuation) 
    val = True
    if not any(char in SpecialSym for char in data["password"]):
        val = False
    else:
        val = True
    return val



users["Have_digit"] = users.apply(digital,axis=1) ## Checking if password have numerical char
users["Have_capital"] = users.apply(upper,axis=1) ## Checking if password have upper character
users["Have_lower"] = users.apply(lower,axis=1) ## Checking if password have lower character
users["Have_special_char"] = users.apply(special,axis=1) ## Checking if password have special char

def strength(data):
    power = 0
    
    # Check if the password is not too short
    if not data["too_short"]:
        power += 1
    
    # Check if the password is not a common password
    if not data["common_password"]:
        power += 1
    
    # Check if the password does not have too many repeats
    if not data["too_many_repeats"]:
        power += 1
    
    # Check if the password does not use the user's name
    if not data["uses_name"]:
        power += 1
    
    # Check if the password does not contain common words
    if not data["common_word"]:
        power += 1
    
    # Check if the password has at least one digit
    if data["Have_digit"]:
        power += 1
    
    # Check if the password has at least one uppercase letter
    if data["Have_capital"]:
        power += 1
    
    # Check if the password has at least one lowercase letter
    if data["Have_lower"]:
        power += 1
    
    # Check if the password has at least one special character
    if data["Have_special_char"]:
        power += 1
    
    # Return the calculated power or strength score
    return power


users["strength"] = users.apply(strength,axis=1)

# Checking password validity 
users['bad_password'] = users['too_short']|\
                        users['common_password']|\
                        users['common_word']|\
                        users['uses_name']|\
                        users["too_many_repeats"]|\
                        ~users['Have_digit']|\
                        ~users['Have_capital']|\
                        ~users['Have_lower']|\
                        ~users['Have_special_char']


print("The number of bad passwords :"+str(users['bad_password'].sum())+"/"+str(len(users["password"])))

# Checking password validity 
users['bad_password'] = users['strength']>6


print("The number of bad passwords :"+str(users['bad_password'].sum())+"/"+str(len(users["password"])))

def bad_pass(username,password):
    too_short = True
    common_password = True
    common_word = True
    uses_name = True
    too_many_repeats = True
    digit = False
    lower = False
    upper = False
    special = False
    SpecialSym = set(punctuation) 

    firstname = ""
    lastname = ""

    if len(password) < 8:
        print('Password length should be greater then 8')
        too_short = True
    else:
        too_short = False

    if password.lower() in ( common_passwords.values):
        print('Password should not have pawned passwords')
        common_password = True
    else:
        common_password = False

    if password.lower() in (words.values):
        print('Password should not have Google most common word')
        common_word = True
    else:
        common_word = False
    firstname = re.findall(r'(^\w+)', username)
    lastname = re.findall(r'(\w+$)', username)

    if (password == firstname)|(password == lastname):
        print('Password should not have username')
        uses_name = True
    else:
        uses_name = False

    if np.size(re.findall(r'(.)\1\1\1\1\1', password) ) == 0:
        
        too_many_repeats = False
    else:
        print('Password should not have repeatative character')
        too_many_repeats = True

    if not any(char.isdigit() for char in password):
        print('Password should have at least one numerical')
        digit = True
            
    if not any(char.isupper() for char in password):
        print('Password should have at least one uppercase letter')
        upper = True
            
    if not any(char.islower() for char in password):
        print('Password should have at least one lowercase letter')
        lower = True
            
    if not any(char in SpecialSym for char in password):
        print('Password should have at least one of the special characters')
        special = True

    if too_short|common_password|common_word|uses_name|too_many_repeats|\
        digit|upper|lower|special:
        print('\n\033[1m'+"Bad Password"+'\033[0m')
    else:
        print('\n\033[1m'+"Good Password"+'\033[0m')

username = "Abid.Ali"
new_password = "Gf4Cx4b%Fqfc#Z"
bad_pass(username,new_password)


# -*- coding: utf-8 -*-
"""
Determine the shift of the Caesar Cypher

Created on Sat Feb  2 23:03:02 2019

@author: shakes
"""
from collections import Counter
import string

message = "Zyp cpxpxmpc ez wzzv fa le esp delcd lyo yze ozhy le jzfc qppe Ehz ypgpc rtgp fa hzcv Hzcv rtgpd jzf xplytyr lyo afcazdp lyo wtqp td pxaej hteszfe te Escpp tq jzf lcp wfnvj pyzfrs ez qtyo wzgp cpxpxmpc te td espcp lyo ozye esczh te lhlj Depaspy Slhvtyr" 

#frequency of each letter
letter_counts = Counter(message)
#print(letter_counts)

#find max letter
maxFreq = -1
maxLetter = None
for letter, freq in letter_counts.items(): 
    print(letter, ":", freq) 
    if letter != ' ' and freq > maxFreq:
        maxLetter = letter
        maxFreq = freq
print("Max Ocurring Letter:", maxLetter)

#predict shift
#assume max letter is 'e'
letters = string.ascii_letters #contains 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

shift = ord(maxLetter) - ord('e')
print("Predicted Shift:", shift)

#attempt decipher
upperLetters = string.ascii_uppercase
lowerLetters = string.ascii_lowercase
decrypt = []
for letter in message:
    letters = [];
    if letter in upperLetters:
        letters = upperLetters
    elif letter in lowerLetters:
        letters = lowerLetters
    else:
        decrypt.append(letter)
        continue

    index = letters.index(letter)
    decrypt.append(letters[(index - shift + len(letters))%len(letters)])

print("Message:", "".join(decrypt));

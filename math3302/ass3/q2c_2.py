# Convert Vigenere cipher to a Caesar cipher problem
# l is the length of the key
def vigenere_key(msg,l):
    # split the cipher text into buckets
    buckets = []
    for i in range(l):
        buckets.append(msg[i::l])
    # perform caesar cipher analysis on each bucket
    # bigGuess is the full key
    bigGuess = []
    for bucket in buckets:
        # count the number of letters
        counter = dict.fromkeys(string.ascii_lowercase, 0)
        for c in bucket:
            counter[c] += 1
        # find most frequent letter and guess it's 'e'
        frequent = max(counter.items(), key=operator.itemgetter(1))[0]
        guess = (ord(frequent) - ord('e'))%26
        print(chr(guess + ord('a')))
        # add our guessed character to our bigGuess
        bigGuess.append(guess)
    return bigGuess

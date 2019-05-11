# Kasiski's test on msg
def kasiski(msg):
    # Find all n-grams
    # in this case it will be segments of length 3
    n = 3
    counter = {}
    for i in range(len(msg)):
        substr = msg[i:i+n]
        if substr in counter.keys():
            counter[substr] += 1
        else:
            counter[substr] = 1

    # find the n-grams that appear more than once, these are the interesting ones
    # we will find the distances between these n-grams
    interest = []
    for k,v in counter.items():
        if v > 1:
            interest.append(k)

    # Find distances between n-grams
    distances = []
    for w in interest:
        occurs = [m.start() for m in re.finditer(w, msg)]
        for o in range(1,len(occurs)):
            for i in range(o+1,len(occurs)):
                distances.append(occurs[o] - occurs[i])

    # gcd algorithm as determined by Euler's algorithm
    def gcd(a,b):
        if b == 0:
            return a
        return gcd(b, a%b)

    # how many distances share 3,4 or 5 as common factors
    frequency = {3:0, 4:0, 5:0}
    for factor in frequency.keys():
        for d in distances:
            frequency[factor] += 1 if gcd(d,factor) == factor else 0

    print("Factor:Frequency")
    for k,v in frequency.items():
        print(k,":",v)
    return frequency

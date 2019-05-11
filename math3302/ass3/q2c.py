#!/usr/bin/env python3
import re
import string
import operator
import itertools

msg = "laoginxbvrythrmyahglakhlipjivwamsycvksfwwwoahoxoem" \
"fzoyejzsoylmcalgesbjhtfzenbcyillrbvatbtvsrknwmlvrv" \
"wwwaxgeoqcftfosjhitlkwfnaaguesgfplfgpwakkxfiefmgum" \
"kyceizxoqaslhuvgupvrypwgletrqifxraijosfefwvrjwehjm" \
"dwzlipvwgivuiglalanrfxfnwzxprrlhjrvzbguskmsfwkaoah" \
"otgnwwtglefwueeuxthpslsiijiselsigbrwgsiijlsrqklczy" \
"uaogsfxgrekxofazxbbrwaofxgizncsioexuxfgeagzlrghbrp" \
"ghyvrythqsjboakjtmglsmbvkzmqbydwvnzwusymwosqxzthui" \
"ztrceklsqxzkchkztheeyxrlekacevauzrektblxjturhqhtby" \
"jturxzhgrjagsyckaocivywakwkgpsmerainxfuenxqyylvvrh" \
"sdbvjwycewagbbvlacfikfwymfzzvtkaoiiukwrhgnhbryhrnr" \
"vzcbhfxgflwawzwwetpsmeraslasytohbqijbbtelmvrgseabj" \
"zbgqiexoasmkoahxhfnqgfsaxxxzgowxbyclasgijkwopwizre" \
"knfrsxtrbytesymxxwgaslofqsezcejmmtslndeelasemftvhv" \
"jrplpswmaejucesmzvjlgpofenxflgdxjrvohanrobhuazthys" \
"jwvrrjrifivmcqikvfvfwtgglwkszeaggbjjxoypqkszejdoop" \
"wnuymfxgfwzxvnhhkciivtbrbuxzyifmkvjwmcbrwhtbyjfcfx" \
"lxrvsmlozfslgnhgkgnrvaoimfzphvaxruijaiffsgrcvgisep" \
"qbbnqskpyietifsdxizazbquwzxvnhzxffidyrrwazbrhsgrze" \
"jkwrhgytuijwohkzmsewlhgbqwkwpljthuijxzqijemziflvrh" \
"wocgivasewwetasomcglwizreknfrwgyteifvvsmumwbrxksag" \
"zvcbowkm"

# Find all n-grams
n = 3
counter = {}
for i in range(len(msg)):
  substr = msg[i:i+n]
  if substr in counter.keys():
    counter[substr] += 1
  else:
    counter[substr] = 1

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

# gcd algorithm is determined by Euler
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

# assume key length is the most common factor
l = max(frequency.items(), key=operator.itemgetter(1))[0]
buckets = []
for i in range(l):
  buckets.append(msg[i::l])
# perform caesar cipher analysis on each bucket
bigGuess = []
for bucket in buckets:
  counter = dict.fromkeys(string.ascii_lowercase, 0)
  for c in bucket:
    counter[c] += 1
  # find most frequent (guess it's 'e')
  frequent = max(counter.items(), key=operator.itemgetter(1))[0]
  guess = (ord(frequent) - ord('e'))%26
  bigGuess.append(guess)

# used to decode a single character (c) with a given shift (s)
def decode(c,s):
  # (i) is the actual index of the letter
  # a=0, b=1, c=2 ... etc.
  i = ord(c) - ord('a')

  # (i_d) is the index of the decoded letter
  # it is shifted back by (i)
  # the modulo operator used here is not the usual mathematical modulo
  # it is not guaranteed to give a positive answer (hence the +26)
  i_d = (i - s) % 26

  # (c_d) is the decoded letter
  c_d = chr(i_d + ord('a'))
  return c_d

# forced to proper key since the initial key was ftone
bigGuess = [ord(c) - ord('a') for c in "stone"]
msgd = ""
for c,s in zip(msg,itertools.cycle(bigGuess)):
  msgd += decode(c,s)
print(msgd)

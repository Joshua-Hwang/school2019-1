#!/usr/bin/env python3
import re

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

# Find all trigraphs
counter = {}
for i in range(len(msg)):
  substr = msg[i:i+5]
  if substr in counter.keys():
    counter[substr] += 1
  else:
    counter[substr] = 1

interest = []
for k,v in counter.items():
  if v > 1:
    interest.append(k)

# Find distances between trigraphs
distances = []
for w in interest:
  occurs = [m.start() for m in re.finditer(w, msg)]
  for i in range(1,len(occurs)):
    distances.append(occurs[i] - occurs[i-1])

print(distances)

# gcd algorithm is determined by Euler
def gcd(a,b):
  if b == 0:
    return a
  return gcd(b, a%b)

ans = distances[0]
for a in distances[1:]:
  ans = gcd(ans, a)

print(ans)

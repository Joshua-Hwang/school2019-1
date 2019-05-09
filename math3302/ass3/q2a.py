#!/usr/bin/env python3

msg = "ujgcxijgt"

# used to decode a single character (c) with a given shift (s)
def decode(c,s):
  # (i) is the actual index of the letter
  # a=0, b=1, c=2 ... etc.
  i = ord(c) - ord('a')

  # (i_d) is the index of the decoded letter
  # it is shifted back by (i)
  # the modulo operator used here is not the usual mathematical modulo
  # it is not guaranteed to give a positive answer (hence the +26)
  i_d = (i - s + 26) % 26

  # (c_d) is the decoded letter
  c_d = chr(i_d + ord('a'))
  return c_d

# Begin the exhaustive search
# iterate over all possible shifts (s)
for s in range(26):
  # create a variable (ans) to store our temporary answer
  ans = ""
  # iterate over each character in message and decode
  for c in msg:
    # append the decoded letter to our temporary (ans)
    ans += decode(c,s)

  # Notify the user what shift was used and the answer for it
  print("Shift:", s)
  print(ans)
  # The shift is likely found halfway through.
  # A request to continue searching is placed after each shift is tested
  cont = input("Continue?(y/n) ")
  if cont == 'n':
    break

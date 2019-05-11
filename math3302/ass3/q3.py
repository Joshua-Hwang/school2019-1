#!/usr/bin/env python3
import math

test = True
# a^-1 mod b
def mult_inv(a,b):
    print("\\text{Finding inverse of", a, "and", b,"}")
    ans = egcd(a, b)
    if ans[0] != 1:
        return None
    else:
        print("\\text{Found inverse", ans[1], "}")
        return ans[1]

def egcd(a,b):
    if a == 0:
        return (b, 0, 1)
    else:
        gcd, x, y = egcd(b % a, a)
        newx, newy = y - math.floor(b/a) * x, x
        print(f"{gcd} &= {a} \\times {newx} + {b} \\times {newy}")
        return (gcd, newx, newy)

# Chinese remainder theorem
n1 = 43807
n2 = 48721
n3 = 44767

a1 = 42710
a2 = 15083
a3 = 40156

M1 = n2*n3
print("m_1 &=",M1)
M2 = n1*n3
print("m_2 &=",M2)
M3 = n1*n2
print("m_3 &=",M3)
M = n1*n2*n3
print("m &=",M)

y1 = mult_inv(M1, n1)
print("y_1 &=", y1)
y2 = mult_inv(M2, n2)
print("y_2 &=", y2)
y3 = mult_inv(M3, n3)
print("y_3 &=", y3)

ans = (a1*M1*y1 + a2*M2*y2 + a3*M3*y3)%M
print(ans)
print(ans**(1/3))

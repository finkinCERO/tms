#!/usr/bin/python3.8

import base64

a = '0xff6f0140006f01'
#b = base64.b64decode(a)

n = int(a, 16)
bStr = ''
while n > 0:
    bStr = str(n % 2) + bStr
    n = n >> 1
res = bStr

l = 64 - len(res)
print(l)
correction = ""
while 0 < l:
    correction = correction + "0"
    l = l - 1


# Print the resultant string
print("Resultant string", correction + str(res))

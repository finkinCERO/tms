#!/usr/bin/python3.8
def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val    


def int_to_bits(_value, bits):
    _bytes = '{0:08b}'.format(_value)
    return _bytes.encode()


def with_bit_overflow(number):
    _bits = int_to_bits(number, 8).decode("ascii").replace("-","")
    print("bits: "+str(_bits))
    print("first "+ _bits[0])
    
    return int(_bits[0])


def two_complment_substract(a, b):
    return a + (twos_comp(b, 8)+1)


def is_seqence_number_newer(incoming, current):
    result = with_bit_overflow(two_complment_substract(incoming,current))
    print(result)
    return  result > 0


#a = 120
#b = 130
#c = 2
#print(is_seqence_number_newer(a,b))
#print(twos_comp(130,8))
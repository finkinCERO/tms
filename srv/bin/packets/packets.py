#!/usr/bin/python3.8
import base64
TYPE_RREQ_HEADER = b'0000'
TYPE_RREP_HEADER = b'0001'
TYPE_REER_HEADER = b'0010'
TYPE_MSG_HEADER = b'0011'
TYPE_ACK_HEADER = b'0100'


class Packets:

    def get_generic_packet_header(type=None, flags=None, hop_address=None, prev_hop_address=None):

        byte = type + flags + hop_address + prev_hop_address
        # if(type==b"0000" and flags==b"0000"):
        #    byte = hop_address + prev_hop_address
        #    print("* rreq matched")

        return byte

    def get_request_packet_header(self, hop_address, prev_hop_address):
        hAddr = hop_address
        prevAddr = prev_hop_address
        if isinstance(hAddr, int):
            hAddr = self.int_to_bits(hAddr, 8)

        if isinstance(prevAddr, int):
            prevAddr = self.int_to_bits(prevAddr, 8)
        byte = self.get_generic_packet_header(
            TYPE_RREQ_HEADER, b'0000', hAddr, prevAddr)

        #TYPE_RREQ_HEADER + b'0000' + hop_address + prev_hop_address
        return byte

    

    def get_reply_packet_header(self, hop_address, prev_hop_address):
        hAddr = hop_address
        prevAddr = prev_hop_address
        if isinstance(hAddr, int):
            hAddr = self.int_to_bits(hAddr, 8)
        if isinstance(prevAddr, int):
            prevAddr = self.int_to_bits(prevAddr, 8)
        byte = self.get_generic_packet_header(
            TYPE_RREP_HEADER, b'0000', hAddr, prevAddr)
        return byte

    def get_error_packet_header(self, hop_address, prev_hop_address):

        byte = self.get_generic_packet_header(
            TYPE_REER_HEADER, b'0000', hop_address, prev_hop_address)
        return byte

    def get_msg_packet_header(self, hop_address, prev_hop_address):

        byte = self.get_generic_packet_header(
            TYPE_MSG_HEADER, b'0000', hop_address, prev_hop_address)
        return byte

    def get_ack_packet_header(self, hop_address, prev_hop_address):

        byte = self.get_generic_packet_header(
            TYPE_ACK_HEADER, b'0000', hop_address, prev_hop_address)
        return byte

    def get_rreq_packets(self, prev_hop_addr, request_id, dest_addr, dest_seq, hop_count, origin_addr, origin_seq):
        byte = self.get_request_packet_header(b'11111111', prev_hop_addr) + \
            request_id + dest_addr + dest_seq + hop_count + origin_addr + origin_seq
        return byte

    def get_rrep_packets(self, hop_addr, prev_hop_addr, request_id, dest_addr, dest_seq, hop_count, origin_addr, origin_seq):
        byte = self.get_request_packet_header(hop_addr, prev_hop_addr) + \
            request_id + dest_addr + dest_seq + hop_count + origin_addr + origin_seq
        return byte

    def int_to_bits(_value, bits):
        _bytes = '{0:08b}'.format(_value)
        return _bytes.encode()

    def get_hex(bits):
        hex_value = hex(int(bits, base=2))[2:]
        i = 0
        for bit in str(bits.decode("ascii")):
            if(bit == "0"):
                i = i + 1
            else:
                break
        c = int(i / 4)
        #print("c, i:\t", c, i)
        for j in range(0, c):
            if(4 <= i):
                hex_value = "0" + hex_value
        return hex_value

    def count_zeros_from_start(hex_value):
        l = len(hex_value)
        print("# count 0 value:\t"+hex_value)
        count = 0
        for i in range(0, l):
            if hex_value[i] == "0":
                count += 1
            else:
                break
        print("# zeros:\t"+str(count))
        return count

    def add_zeros(binary, i):
        n = i
        for j in range(0, n):
            binary = '0'+binary

        return binary

    def hex_to_binary_bits(self, value):
        # print("# zeros:\t\t", zeros)
        n = int(value, 16)
        zeros = self.count_zeros_from_start(str(bin(n))[2:])
        hex_zeros = self.count_zeros_from_start(value)
        _bin = str(bin(n))[2:]
        l = 4 - len(_bin) % 4
        if l == 4:
            l = 0
        print("len:\t"+str(len(_bin))+"\tl:\t"+str(l))
        _bin = self.add_zeros(_bin, l + hex_zeros*4)
        return _bin

    def base64_to_hex(value):
        res = base64.b64decode(value).hex()
        return res
    def decodeBase64(b64_string):
        _bytes = base64.b64decode(b64_string)
        int_arr = [x for x in _bytes]
        return int_arr
    def encodeBase64(int_arr):
        byte_arr = b''
        for value in int_arr:
            byte_arr += int(value).to_bytes(1, 'big')
        result = base64.b64encode(byte_arr)
        print(result)
        return result


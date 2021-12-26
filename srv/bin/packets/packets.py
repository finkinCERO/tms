#!/usr/bin/python3.8
TYPE_RREQ_HEADER = b'0000'
TYPE_RREP_HEADER = b'0001'
TYPE_REER_HEADER = b'0010'
TYPE_MSG_HEADER = b'0011'
TYPE_ACK_HEADER = b'0100'


class Packets:

    def get_generic_packet_header(type=None, flags=None, hop_address=None, prev_hop_address=None):

        byte = type + flags + hop_address + prev_hop_address
  
        return byte

    def get_request_packet_header(self, hop_address, prev_hop_address):

        byte = self.get_generic_packet_header(
            TYPE_RREQ_HEADER, b'0000', hop_address, prev_hop_address)
        TYPE_RREQ_HEADER + b'0000' + hop_address + prev_hop_address
        return byte

    def get_reply_packet_header(self, hop_address, prev_hop_address):

        byte = self.get_generic_packet_header(
            TYPE_RREQ_HEADER, b'0000', hop_address, prev_hop_address)
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


#Packets.get_generic_packet_header(TYPE_RREQ_HEADER, b'0000', b'1111', b'0001')

from common.packet import Packet
import logging

class Batch:
    def __init__(self, packets):
        self.packets = packets

    @classmethod
    def deserialize(cls, bytes):
        packets = []
        payload_length = int.from_bytes(bytes[0:2], byteorder='big', signed=False)

        byte_data = bytes[2:]

        failed_packets = 0
        current_byte = 0

        while current_byte < payload_length:
            packet_length = int.from_bytes(byte_data[0:2], byteorder='big', signed=False)
            packet_bytes = byte_data[0:2 + packet_length]
            try:
                packet = Packet.deserialize(packet_bytes)
                packets.append(packet)
            except Exception as e:
                logging.info(f"Failed to deserialize packet: {e}")
                failed_packets += 1
            
            current_byte += 2 + packet_length
            byte_data = byte_data[2 + packet_length:]
        return cls(packets), failed_packets
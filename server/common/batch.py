from common.packet import Packet

class Batch:
    def __init__(self, packets):
        self.packets = packets

    @classmethod
    def deserialize(cls, bytes):
        packets = []
        byte_data = bytes
        while len(byte_data) > 0:
            packet_length = int.from_bytes(byte_data[0:2], byteorder='big', signed=False)
            packet_bytes = byte_data[2:2 + packet_length]
            packet = Packet.deserialize(packet_bytes)
            packets.append(packet)
            byte_data = byte_data[2 + packet_length:]
        return cls(packets)
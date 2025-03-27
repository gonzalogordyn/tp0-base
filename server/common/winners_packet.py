class WinnersPacket:
    WINNERS_CODE = 9001
    def __init__(self, winners):
        self.winners = winners

    def serialize(self):
        code = self.WINNERS_CODE.to_bytes(2, byteorder='big', signed=False)
        payload = b''
        for winner in self.winners:
            document_int = int(winner)
            document_bytes = document_int.to_bytes(4, byteorder='big', signed=False)
            payload += document_bytes
        payload_length = len(payload).to_bytes(2, byteorder='big', signed=False)
        
        return code + payload_length + payload

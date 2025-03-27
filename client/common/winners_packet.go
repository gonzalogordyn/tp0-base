package common

import (
	"encoding/binary"
	"errors"
)

type WinnersPacket struct {
	Winners []int
}

const WinnersCode = 9001

func DeserializeWinnersPacket(data []byte) (*WinnersPacket, error) {

	payloadLength := binary.BigEndian.Uint16(data[2:4])
	if len(data) < int(4+payloadLength) {
		return nil, errors.New("invalid packet")
	}

	// Lectura de ganadores
	payload := data[4 : 4+payloadLength]
	winners := []int{}

	for i := 0; i < len(payload); i += 4 {
		if i+4 > len(payload) {
			return nil, errors.New("invalid packet")
		}

		document := binary.BigEndian.Uint32(payload[i : i+4])
		winners = append(winners, int(document))
	}

	return &WinnersPacket{Winners: winners}, nil
}

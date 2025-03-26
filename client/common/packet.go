package common

import (
	"bytes"
	"encoding/binary"
	"errors"
)

type Packet struct {
	Nombre     string
	Apellido   string
	Nacimiento string
	Documento  uint32
	Numero     uint32
}

func NewPacket(nombre, apellido, nacimiento string, documento, numero uint32) (*Packet, error) {
	if len(nombre) > 30 || len(apellido) > 30 {
		return nil, errors.New("no debe superar los 30 caracteres")
	}
	if len(nacimiento) != 10 {
		return nil, errors.New("formato de fecha incorrecto")
	}
	return &Packet{nombre, apellido, nacimiento, documento, numero}, nil
}

func (packet *Packet) Serialize() ([]byte, error) {
	var buf bytes.Buffer

	nombreBytes := []byte(packet.Nombre)
	apellidoBytes := []byte(packet.Apellido)
	nacimientoBytes := []byte(packet.Nacimiento)

	log.Infof("nombreBytes: %v", nombreBytes)
	log.Infof("apellidoBytes: %v", apellidoBytes)
	log.Infof("nacimientoBytes: %v", nacimientoBytes)
	buf.WriteByte(byte(len(nombreBytes)))
	buf.Write(nombreBytes)

	buf.WriteByte(byte(len(apellidoBytes)))
	buf.Write(apellidoBytes)

	buf.Write(nacimientoBytes)

	if err := binary.Write(&buf, binary.BigEndian, packet.Documento); err != nil {
		return nil, err
	}
	if err := binary.Write(&buf, binary.BigEndian, packet.Numero); err != nil {
		return nil, err
	}

	payload := buf.Bytes()
	payloadLength := make([]byte, 2)
	binary.BigEndian.PutUint16(payloadLength, uint16(len(payload)))

	return append(payloadLength, payload...), nil
}

func Deserialize(data_bytes []byte) (*Packet, error) {
	if len(data_bytes) < 2 {
		return nil, errors.New("formato invalido de paquete")
	}

	data := data_bytes[2:]

	// Lectura de nombre
	nombreLength := int(data[0])
	nombre := string(data[1 : 1+nombreLength])

	// Lectura de apellido
	apellidoLengthField := 1 + nombreLength
	apellidoLength := int(data[apellidoLengthField])
	apellidoStart := apellidoLengthField + 1
	apellido := string(data[apellidoStart : apellidoStart+apellidoLength])

	// Lectura de nacimiento
	nacimientoStart := apellidoStart + apellidoLength
	nacimiento := string(data[nacimientoStart : nacimientoStart+10])

	// Lectura de documento
	documentoStart := nacimientoStart + 10
	documento := binary.BigEndian.Uint32(data[documentoStart : documentoStart+4])

	// Lectura de numero
	numeroStart := documentoStart + 4
	numero := binary.BigEndian.Uint32(data[numeroStart : numeroStart+4])

	return &Packet{nombre, apellido, nacimiento, documento, numero}, nil
}

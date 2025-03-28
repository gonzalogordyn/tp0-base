package common

import (
	"encoding/csv"
	"io"
	"os"
	"strconv"
)

func ReadBets(filePath string, startLine, maxAmount int) ([]Packet, int, error) {
	// Reservo 2 bytes para el header
	maxSize := 8190

	file, err := os.Open(filePath)
	if err != nil {
		return nil, 0, err
	}
	defer file.Close()

	reader := csv.NewReader(file)

	for i := 0; i < startLine; i++ {
		_, err := reader.Read()
		if err != nil {
			return nil, 0, err
		}
	}

	var bets []Packet
	linesRead := 0
	tamanioTotal := 0

	for linesRead < maxAmount {
		record, err := reader.Read()
		if err != nil {
			if err == io.EOF {
				break
			}
			return nil, 0, err
		}

		documento, _ := strconv.ParseUint(record[2], 10, 32)
		numero, _ := strconv.ParseUint(record[4], 10, 32)
		bet := Packet{
			Nombre:     record[0],
			Apellido:   record[1],
			Nacimiento: record[3],
			Documento:  uint32(documento),
			Numero:     uint32(numero),
		}
		if tamanioTotal+bet.Size() > maxSize {
			break
		}
		bets = append(bets, bet)
		linesRead++
		tamanioTotal += bet.Size()
	}

	return bets, startLine + linesRead, nil
}

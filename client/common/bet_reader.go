package common

import (
	"encoding/csv"
	"os"
	"strconv"
)

func ReadBets(filePath string) ([]Packet, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	// Mateo,Agüero,29380265,1981-09-07,3347

	var bets []Packet

	for _, record := range records {
		documento, _ := strconv.ParseUint(record[2], 10, 32)
		numero, _ := strconv.ParseUint(record[4], 10, 32)
		bet := Packet{
			Nombre:     record[0],
			Apellido:   record[1],
			Nacimiento: record[3],
			Documento:  uint32(documento),
			Numero:     uint32(numero),
		}
		bets = append(bets, bet)
	}
	return bets, nil
}

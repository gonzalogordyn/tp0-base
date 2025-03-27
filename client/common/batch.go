package common

import "encoding/binary"

func CreateBatches(bets []Packet, maxAmount int) ([][]byte, error) {
	log.Infof("Creando batches")
	const maxBatchSize = 8192
	const headerSize = 2

	var batches [][]byte
	var currentBatch []byte

	packetsInCurrentBatch := 0
	currentBatchSize := headerSize

	for _, bet := range bets {
		log.Infof("Apuesta: %v", bet)
		// Chequeo si se excede el tamaño máximo de batch o cantidad de paquetes
		if currentBatchSize+bet.Size() > maxBatchSize || packetsInCurrentBatch >= maxAmount {
			log.Infof("Creando nuevo batch.")
			// Serializo la longitud del batch (sin el header)
			batchLength := make([]byte, headerSize)
			binary.BigEndian.PutUint16(batchLength, uint16(currentBatchSize-headerSize))

			// Agrego el header al batch y appendeo
			currentBatch = append(batchLength, currentBatch...)
			batches = append(batches, currentBatch)

			// Nuevo batch
			currentBatch = []byte{}
			currentBatchSize = headerSize
		}

		serializedBet, err := bet.Serialize()
		if err != nil {
			return nil, err
		}

		currentBatch = append(currentBatch, serializedBet...)
		currentBatchSize += len(serializedBet)
	}
	if len(currentBatch) > 0 {
		// Serializo la longitud del batch (sin el header)
		batchLength := make([]byte, headerSize)
		binary.BigEndian.PutUint16(batchLength, uint16(currentBatchSize-headerSize))

		// Agrego el header al batch y appendeo
		currentBatch = append(batchLength, currentBatch...)
		batches = append(batches, currentBatch)
	}

	return batches, nil
}

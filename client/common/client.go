package common

import (
	"encoding/binary"
	"fmt"
	"io"
	"net"
	"strconv"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

const NOTIFICATION = 9000

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID             string
	ServerAddress  string
	LoopAmount     int
	LoopPeriod     time.Duration
	BatchMaxAmount int
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn

	// Envio id del cliente
	idInt, err := strconv.Atoi(c.config.ID)
	if err != nil {
		log.Errorf("error convirtiendo id de cliente a int")
		c.conn.Close()
	}
	idByte := byte(idInt)
	err = c.WriteAllBytes([]byte{idByte})
	if err != nil {
		log.Errorf("error enviando id de cliente")
		c.conn.Close()
		return err
	}

	return nil
}

func (c *Client) GracefulShutdown() {
	log.Infof("Cerrando cliente...")
	if c.conn != nil {
		log.Infof("Cerrando conexión con el servidor...")
		c.conn.Close()
	}
}

func (c *Client) WriteAllBytes(data []byte) error {
	totalSent := 0
	// log.Infof("Bytes enviados: %x", data)
	for totalSent < len(data) {
		sent, err := c.conn.Write(data[totalSent:])
		if err != nil {
			return err
		}
		if sent == 0 {
			return io.ErrUnexpectedEOF
		}
		totalSent += sent
	}
	return nil
}

func (c *Client) ReadAllBytes(n int) ([]byte, error) {
	data := make([]byte, n)
	totalRead := 0
	for totalRead < n {
		read, err := c.conn.Read(data[totalRead:])
		if err != nil {
			return nil, err
		}
		if read == 0 {
			return nil, io.ErrUnexpectedEOF
		}
		totalRead += read
	}
	return data, nil
}

func (c *Client) WaitForWinners() {
	// Lectura del header
	header, err := c.ReadAllBytes(4)
	if err != nil {
		log.Errorf("error recibiendo header del paquete")
		return
	}

	// Primeros 2 bytes son el codigo (9001)
	code := binary.BigEndian.Uint16(header[:2])
	if code != WinnersCode {
		log.Errorf("error: código inesperado %d, esperado %d", code, WinnersCode)
		return
	}

	// Proximos 2 bytes son el tamaño del payload en bytes
	payloadLength := binary.BigEndian.Uint16(header[2:4])

	// Lectura del payload
	payload, err := c.ReadAllBytes(int(payloadLength))
	if err != nil {
		log.Errorf("error recibiendo payload del paquete")
		return
	}

	// Deserializacion del paquete de ganadores
	winnersPacket, err := DeserializeWinnersPacket(append(header, payload...))
	if err != nil {
		log.Errorf("error deserializando paquete de ganadores")
		return
	}

	// Log the winners
	log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %d", len(winnersPacket.Winners))
}

func (c *Client) SendNotification() {
	notificationBytes := make([]byte, 2)
	binary.BigEndian.PutUint16(notificationBytes, NOTIFICATION)
	err := c.WriteAllBytes(notificationBytes)
	if err != nil {
		log.Errorf("error enviando notificación al servidor: %v", err)
		return
	}

	log.Infof("action: notificacion_enviada | result: success")
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	log.Infof("Lectura de csv")
	bets, err := ReadBets(fmt.Sprintf("/.data/agency-%s.csv", c.config.ID))
	if err != nil {
		log.Errorf("error leyendo apuestas")
	}
	log.Infof("Apuestas leídas: %v", bets)

	batches, err := CreateBatches(bets, c.config.BatchMaxAmount)
	if err != nil {
		log.Errorf("error creando batches")
	}
	log.Debugf("Batches creados: %v", batches)

	c.createClientSocket()

	for _, batch := range batches {
		// Escribo con funcion auxiliar para evitar short write
		err = c.WriteAllBytes(batch)
		if err != nil {
			log.Errorf("error enviando paquete")
			return
		}

		// Lectura de la response con funcion auxiliar para evitar short read
		msg, err := c.ReadAllBytes(3)
		if err != nil {
			log.Errorf("error recibiendo respuesta")
			return
		}

		if len(msg) != 3 || string(msg[:3]) != "ACK" {
			log.Errorf("error recibiendo respuesta")
			return
		}

		log.Infof("action: batch_enviado | result: success | batch_size: %d", len(batch))
	}
	c.SendNotification()
	c.WaitForWinners()
	c.conn.Close()
}

package common

import (
	"fmt"
	"io"
	"net"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

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
	log.Infof("Bytes enviados: %x", data)
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

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {

	bets, err := ReadBets(fmt.Sprintf("/.data/agency-%s.csv", c.config.ID))
	if err != nil {
		log.Errorf("error leyendo apuestas")
	}

	batches, err := CreateBatches(bets, c.config.BatchMaxAmount)
	if err != nil {
		log.Errorf("error creando batches")
	}

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

	c.conn.Close()

	log.Infof("action: apuestas_enviadas | result: success")
}

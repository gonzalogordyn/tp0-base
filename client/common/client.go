package common

import (
	"encoding/binary"
	"io"
	"net"
	"os"
	"strconv"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
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
	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	// Create the connection the server in every loop iteration. Send an
	c.createClientSocket()
	nombre := os.Getenv("NOMBRE")
	apellido := os.Getenv("APELLIDO")
	nacimiento := os.Getenv("NACIMIENTO")
	documentoStr := os.Getenv("DOCUMENTO")
	numeroStr := os.Getenv("NUMERO")

	documento, err := strconv.ParseUint(documentoStr, 10, 32)
	if err != nil {
		log.Errorf("error parseando documento")
	}
	numero, err := strconv.ParseUint(numeroStr, 10, 32)
	if err != nil {
		log.Errorf("error parseando numero")
	}

	// Creo el paquete
	packet, err := NewPacket(nombre, apellido, nacimiento, uint32(documento), uint32(numero))
	if err != nil {
		log.Errorf("error creando paquete")
	}

	// Lo serializo a bytes
	packetBytes, err := packet.Serialize()
	if err != nil {
		log.Errorf("error serializando paquete")
	}

	// Escribo con funcion auxiliar para evitar short write
	err = c.WriteAllBytes(packetBytes)
	if err != nil {
		log.Errorf("error enviando paquete")
	}

	// Lectura de la response con funcion auxiliar para evitar short read
	msg, err := c.ReadAllBytes(7)
	if err != nil {
		log.Errorf("error recibiendo respuesta")
	}

	if len(msg) != 7 || string(msg[:3]) != "ACK" {
		log.Errorf("error recibiendo respuesta")
		return
	}

	receivedNumero := binary.BigEndian.Uint32(msg[3:])
	if receivedNumero != packet.Numero {
		log.Errorf("numero incorrecto, esperado: %d, recibido: %d", packet.Numero, receivedNumero)
		return
	}

	c.conn.Close()

	log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
		packet.Documento,
		packet.Numero,
	)
}

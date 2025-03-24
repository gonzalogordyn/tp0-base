#!/bin/bash

SERVER_CONTAINER="server"
PORT=12345
MSG="hola mundo 1234"

SERVER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $SERVER_CONTAINER)

RESPONSE=$(docker run --rm --network container:$SERVER_CONTAINER alpine sh -c "echo "$MSG" | nc -w 5 $SERVER_IP $PORT")

if [ "$RESPONSE" = "$MSG" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi
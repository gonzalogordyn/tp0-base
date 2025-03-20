#!/bin/bash

SERVER_CONTAINER="server"
PORT=12345
MSG="hola mundo 1234\n"

RESPONSE=$(docker run --rm --network container:$SERVER_CONTAINER alpine sh -c "echo '$MSG' | nc -w 1 localhost '$PORT'")

if [ "$RESPONSE" == "$MSG" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi
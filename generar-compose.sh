#!/bin/bash
if [ "$#" -lt 2 ]; then
    echo "Uso: $0 <nombre_archivo> <cantidad_clientes>"
    exit 1
fi

echo "Nombre del archivo de salida: $1"
echo "Cantidad de clientes: $2"
python3 mi-generador.py $1 $2
# TP0: Docker + Comunicaciones + Concurrencia

### Ejercicio N°3:
Crear un script de bash `validar-echo-server.sh` que permita verificar el correcto funcionamiento del servidor utilizando el comando `netcat` para interactuar con el mismo. Dado que el servidor es un echo server, se debe enviar un mensaje al servidor y esperar recibir el mismo mensaje enviado.

En caso de que la validación sea exitosa imprimir: `action: test_echo_server | result: success`, de lo contrario imprimir:`action: test_echo_server | result: fail`.

El script deberá ubicarse en la raíz del proyecto. Netcat no debe ser instalado en la máquina _host_ y no se pueden exponer puertos del servidor para realizar la comunicación (hint: `docker network`). `

## Resolución

Creé un script que levanta un contenedor de una imagen de Alpine para poder utilizar netcat, y se conecta a la red del servidor. Así se le envía un mensaje, y al ser un echo server, verifico que la respuesta sea igual a lo que envié.

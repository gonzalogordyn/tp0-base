# TP0: Docker + Comunicaciones + Concurrencia

## Parte 2: Repaso de Comunicaciones

Las secciones de repaso del trabajo práctico plantean un caso de uso denominado **Lotería Nacional**. Para la resolución de las mismas deberá utilizarse como base el código fuente provisto en la primera parte, con las modificaciones agregadas en el ejercicio 4.

### Ejercicio N°5:
Modificar la lógica de negocio tanto de los clientes como del servidor para nuestro nuevo caso de uso.

#### Cliente
Emulará a una _agencia de quiniela_ que participa del proyecto. Existen 5 agencias. Deberán recibir como variables de entorno los campos que representan la apuesta de una persona: nombre, apellido, DNI, nacimiento, numero apostado (en adelante 'número'). Ej.: `NOMBRE=Santiago Lionel`, `APELLIDO=Lorca`, `DOCUMENTO=30904465`, `NACIMIENTO=1999-03-17` y `NUMERO=7574` respectivamente.

Los campos deben enviarse al servidor para dejar registro de la apuesta. Al recibir la confirmación del servidor se debe imprimir por log: `action: apuesta_enviada | result: success | dni: ${DNI} | numero: ${NUMERO}`.

#### Servidor
Emulará a la _central de Lotería Nacional_. Deberá recibir los campos de la cada apuesta desde los clientes y almacenar la información mediante la función `store_bet(...)` para control futuro de ganadores. La función `store_bet(...)` es provista por la cátedra y no podrá ser modificada por el alumno.
Al persistir se debe imprimir por log: `action: apuesta_almacenada | result: success | dni: ${DNI} | numero: ${NUMERO}`.

#### Comunicación:
Se deberá implementar un módulo de comunicación entre el cliente y el servidor donde se maneje el envío y la recepción de los paquetes, el cual se espera que contemple:
* Definición de un protocolo para el envío de los mensajes.
* Serialización de los datos.
* Correcta separación de responsabilidades entre modelo de dominio y capa de comunicación.
* Correcto empleo de sockets, incluyendo manejo de errores y evitando los fenómenos conocidos como [_short read y short write_](https://cs61.seas.harvard.edu/site/2018/FileDescriptors/).

### Resolución

El formato de los paquetes es el siguiente.

| **field**             	| **bytes**          	|
|-----------------------	|--------------------	|
| nombre_length_bytes   	| [fijo] 1 byte      	|
| nombre_bytes          	| [variable] max 120 	|
| apellido_length_bytes 	| [fijo] 1 byte      	|
| apellido_bytes        	| [variable] max 120 	|
| nacimiento_bytes      	| [fijo] 10 bytes    	|
| documento_bytes       	| [fijo] 4 bytes     	|
| numero_bytes          	| [fijo] 4 bytes     	|


Consta de dos campos variables, cuyo tamaño máximo será de 120 bytes al ser caracteres encodeados en UTF-8 que varían entre 1-4 bytes, y se ha impuesto un límite de 30 caracteres para estos. Se cuenta para los mismos con dos campos que especifican sus longitudes en bytes, para permitir la correcta lectura y decodificación a strings. Estos serán fijos en 1 byte, ya que alcanza para representar una longitud de hasta 255.  
Para el caso del nacimiento, al ser 10 caracteres que se encuentran dentro del rango ASCII, su tamaño será fijo de 10 bytes.  
Para el documento y número, determiné que 4 bytes eran más suficiente para representarlos.
Esto nos dejaría con un paquete de un tamaño máximo de 260 bytes.  
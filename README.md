# TP0: Docker + Comunicaciones + Concurrencia

## Parte 2: Repaso de Comunicaciones

Las secciones de repaso del trabajo práctico plantean un caso de uso denominado **Lotería Nacional**. Para la resolución de las mismas deberá utilizarse como base el código fuente provisto en la primera parte, con las modificaciones agregadas en el ejercicio 4.

### Ejercicio N°7:

Modificar los clientes para que notifiquen al servidor al finalizar con el envío de todas las apuestas y así proceder con el sorteo.
Inmediatamente después de la notificacion, los clientes consultarán la lista de ganadores del sorteo correspondientes a su agencia.
Una vez el cliente obtenga los resultados, deberá imprimir por log: `action: consulta_ganadores | result: success | cant_ganadores: ${CANT}`.

El servidor deberá esperar la notificación de las 5 agencias para considerar que se realizó el sorteo e imprimir por log: `action: sorteo | result: success`.
Luego de este evento, podrá verificar cada apuesta con las funciones `load_bets(...)` y `has_won(...)` y retornar los DNI de los ganadores de la agencia en cuestión. Antes del sorteo no se podrán responder consultas por la lista de ganadores con información parcial.

Las funciones `load_bets(...)` y `has_won(...)` son provistas por la cátedra y no podrán ser modificadas por el alumno.

No es correcto realizar un broadcast de todos los ganadores hacia todas las agencias, se espera que se informen los DNIs ganadores que correspondan a cada una de ellas.

## Resolución
En este ejercicio me valí de los ejercicios anteriores donde el servidor lee los primeros dos bytes para obtener el tamaño del payload de los paquetes. Utilicé este mismo campo para enviar la notificación desde el cliente de que se han enviado todas las apuestas, en forma de un int de 2 bytes con la constante `9000`. Elegí este número ya que el length que usualmente ocupa estos primeros dos bytes no superará los 8kb, y al ser 2 bytes tengo un gran rango de números superando el 8192 para utilizar a mi placer.

Utilicé el mismo campo para el código que el servidor le envía al cliente informando que el paquete contiene los ganadores del sorteo, esta vez con la constante `9001`. Los dos siguientes bytes serán para la longitud en bytes del payload, que es la serie de documentos ganadores (se irá leyendo de a 4 bytes hasta llegar al final).

También tuve que incluir un mensaje al realizar la conexión, donde el cliente enviará en un byte su id, para que el servidor lo pueda almacenar en un diccionario que lo mappea con el socket, y pueda comunicarse y mandarle el mensaje específico de sus ganadores al finalizar el sorteo.

La comunicación se realiza de manera secuencial, es decir que cada cliente se maneja de a uno por vez. Se mantienen sus conexiones abiertas hasta finalizar el sorteo, luego de lo cual se cerrarán todos los sockets correspondientes (no sin antes comunicar los ganadores).  
Los clientes, por su parte, quedarán bloqueados esperando un mensaje del servidor con los ganadores luego de enviar la notificación de que ya han mandado todas las apuestas. Luego de procesarlo, cerrarán la conexión y finalizarán su ejecución.

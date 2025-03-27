# TP0: Docker + Comunicaciones + Concurrencia

## Parte 2: Repaso de Comunicaciones

Las secciones de repaso del trabajo práctico plantean un caso de uso denominado **Lotería Nacional**. Para la resolución de las mismas deberá utilizarse como base el código fuente provisto en la primera parte, con las modificaciones agregadas en el ejercicio 4.

### Ejercicio N°6:
Modificar los clientes para que envíen varias apuestas a la vez (modalidad conocida como procesamiento por _chunks_ o _batchs_). 
Los _batchs_ permiten que el cliente registre varias apuestas en una misma consulta, acortando tiempos de transmisión y procesamiento.

La información de cada agencia será simulada por la ingesta de su archivo numerado correspondiente, provisto por la cátedra dentro de `.data/datasets.zip`.
Los archivos deberán ser inyectados en los containers correspondientes y persistido por fuera de la imagen (hint: `docker volumes`), manteniendo la convencion de que el cliente N utilizara el archivo de apuestas `.data/agency-{N}.csv` .

En el servidor, si todas las apuestas del *batch* fueron procesadas correctamente, imprimir por log: `action: apuesta_recibida | result: success | cantidad: ${CANTIDAD_DE_APUESTAS}`. En caso de detectar un error con alguna de las apuestas, debe responder con un código de error a elección e imprimir: `action: apuesta_recibida | result: fail | cantidad: ${CANTIDAD_DE_APUESTAS}`.

La cantidad máxima de apuestas dentro de cada _batch_ debe ser configurable desde config.yaml. Respetar la clave `batch: maxAmount`, pero modificar el valor por defecto de modo tal que los paquetes no excedan los 8kB. 

Por su parte, el servidor deberá responder con éxito solamente si todas las apuestas del _batch_ fueron procesadas correctamente.

## Resolución

Se utilizó un formato similar al del ejercicio anterior para los paquetes batch. La diferencia es que un mismo batch contiene varios paquetes (con el mismo formato presentado en el ejercicio anterior) contenidos en un mismo paquete batch. Se incluyó un header para especificar la longitud en bytes del payload, que serían estos paquetes de apuestas.

Con este header, es posible leer paquete por paquete de a bytes (valiéndose de los headers de estos) hasta llegar al final del batch.

El cliente envía de a un batch y espera a una respuesta por parte del servidor que llega cuando termina de procesar todas sus apuestas.
Al finalizar, el servidor loggea la cantidad de apuestas procesadas correctamente en un mensaje.   
En caso de que ocurra un error en el procesamiento, loggeará un mensaje de error con la cantidad de apuestas fallidas. A su vez, enviará un mensaje "ERR" al cliente que envió el batch.

La cantidad de paquetes que entren en un batch está definida por el archivo de configuración. La totalidad de estos paquetes, junto con los dos bytes del header del batch, no excederán los 8kb. Si esto ocurre, el paquete que no entre será pasado en un nuevo batch.

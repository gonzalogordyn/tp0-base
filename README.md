# TP0: Docker + Comunicaciones + Concurrencia

## Parte 3: Repaso de Concurrencia
En este ejercicio es importante considerar los mecanismos de sincronización a utilizar para el correcto funcionamiento de la persistencia.

### Ejercicio N°8:

Modificar el servidor para que permita aceptar conexiones y procesar mensajes en paralelo. En caso de que el alumno implemente el servidor en Python utilizando _multithreading_,  deberán tenerse en cuenta las [limitaciones propias del lenguaje](https://wiki.python.org/moin/GlobalInterpreterLock).

## Resolución

Decidí optar por multiprocesamiento para esquivar el GIL y poder aprovechar un paralelismo real. Por cada conexión entrante se lanza un proceso. 
Tuve que hacer uso de un Manager de multiprocessing para poder compartir el diccionario que mappea a los ids de las agencias con sus ganadores correspondientes.  
Utilicé locks para garantizar la exclusión mutua en operaciones peligrosas, como a la hora de escribir las apuestas, y a la hora de incrementar la cantidad de notificaciones recibidas.  
Respecto a esto último, se handlearan las conexiones de los clientes de manera paralela, pero el último proceso en recibir la notificación de que se han mandado las apuestas será el que comience el sorteo. Se encargará de llamar a la función para leer las apuestas, y almacenará los ganadores de cada agencia en el diccionario mencionado previamente.  
Luego de esto, a través de una cola de mensajes le comunicará al proceso principal que deje de escuchar conexiones entrantes, y que se encargue de comunicarle a cada una de las agencias sus ganadores (ya que es quien mantiene un diccionario que mapea a los ids con sus sockets).


# Correcciones

- Arreglé el tema de no cargar el archivo entero, sino de ir leyendo de a chunks. Directamente leo la cantidad máxima de apuestas en un batch y armo el paquete para mandarlo, esperar el ACK, y seguir leyendo desde donde me quedé. 
- Arreglé de que los bytes del header se lean con la función auxiliar para evitar short read.
- Se crea un proceso aparte para monitorear la cola que espera el mensaje de que el sorteo se ha realizado para terminar la ejecución.
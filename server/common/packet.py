class Packet:
    def __init__(self, nombre, apellido, nacimiento, documento, numero):
        if len(nombre) > 30 or len(apellido) > 30:
            raise ValueError("No debe superar los 30 caracteres.")
        if len(nacimiento) != 10:
            raise ValueError("Formato de fecha incorrecto.")
        
        self.nombre = nombre
        self.apellido = apellido
        self.nacimiento = nacimiento
        self.documento = documento
        self.numero = numero

    def serialize(self):
        # Nombre y apellido a bytes
        nombre_bytes = self.nombre.encode('utf-8')
        apellido_bytes = self.apellido.encode('utf-8')

        # Longitud de los nombres en bytes
        nombre_length_bytes = len(nombre_bytes).to_bytes(1, byteorder='big', signed=False)
        apellido_length_bytes = len(apellido_bytes).to_bytes(1, byteorder='big', signed=False)

        # Fecha de nacimiento a bytes, es de 10 caracteres siempre y todos en rango ASCII
        nacimiento_bytes = self.nacimiento.encode('utf-8')

        # Documento y numero a bytes
        documento_bytes = self.documento.to_bytes(4, byteorder='big', signed=False)
        numero_bytes = self.numero.to_bytes(4, byteorder='big', signed=False)

        payload = nombre_length_bytes + nombre_bytes + apellido_length_bytes + apellido_bytes + nacimiento_bytes + documento_bytes + numero_bytes
        payload_length = len(payload).to_bytes(2, byteorder='big', signed=False)
        
        return payload_length + payload

    @classmethod
    def deserialize(cls, byte_data):
        byte_data = byte_data[2:]
        
        # Lectura de nombre
        nombre_length_bytes = int.from_bytes(byte_data[0:1], byteorder='big', signed=False)
        nombre_bytes = byte_data[1:1 + nombre_length_bytes]
        nombre = nombre_bytes.decode('utf-8')

        # Lectura de apellido
        apellido_length_field = 1 + nombre_length_bytes
        apellido_length_bytes = int.from_bytes(byte_data[apellido_length_field:apellido_length_field + 1], byteorder='big', signed=False)
        
        apellido_start = apellido_length_field + 1
        apellido_bytes = byte_data[apellido_start:apellido_start + apellido_length_bytes]
        apellido = apellido_bytes.decode('utf-8')
        
        # Lectura de nacimiento
        nacimiento_start = apellido_start + apellido_length_bytes
        nacimiento_bytes = byte_data[nacimiento_start:nacimiento_start + 10]
        nacimiento = nacimiento_bytes.decode('utf-8')

        # Lectura de documento
        documento_start = nacimiento_start + 10
        documento_bytes = byte_data[documento_start:documento_start + 4]
        documento = int.from_bytes(documento_bytes, byteorder='big', signed=False)

        # Lectura de numero
        numero_start = documento_start + 4
        numero_bytes = byte_data[numero_start:numero_start + 4]
        numero = int.from_bytes(numero_bytes, byteorder='big', signed=False)
               
        return cls(nombre, apellido, nacimiento, documento, numero)
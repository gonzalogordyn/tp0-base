import sys
import yaml

def generate_compose_yaml(num_clients):
    num_clients = int(num_clients)

    compose_data = {
        'name': 'tp0',
        'services': {
            'server': {
                'container_name': 'server',
                'image': 'server:latest',
                'entrypoint': 'python3 /main.py',
                'environment': ['PYTHONUNBUFFERED=1'],
                'networks': ['testing_net'],
                'volumes': [{'type': 'bind', 'source': './server/config.ini', 'target': '/config.ini'}]
            }
        },
        'networks': {
            'testing_net': {
                'ipam': {
                    'driver': 'default',
                    'config': [{'subnet': '172.25.125.0/24'}]
                }
            }
        }
    }

    for i in range(1, num_clients + 1):
        compose_data['services'][f'client{i}'] = {
            'container_name': f'client{i}',
            'image': 'client:latest',
            'entrypoint': '/client',
            'environment': [f'CLI_ID={i}', 'NOMBRE=Nombre', 'APELLIDO=Apellido', 'DOCUMENTO=12345678', 'NACIMIENTO=1950-01-01', 'NUMERO=1234'],
            'networks': ['testing_net'],
            'depends_on': ['server'],
            'volumes': [{'type': 'bind', 'source': './client/config.yaml', 'target': '/config.yaml'}, {'type': 'bind', 'source': f'./.data/agency-{i}.csv', 'target': f'/.data/agency-{i}.csv'}]
        }

    return yaml.dump(compose_data, default_flow_style=False)


if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        print("Uso: python3 mi-generador.py <nombre_archivo> <cantidad_clientes>")
        sys.exit(1)

    output_filename = sys.argv[1]
    num_clients = sys.argv[2]
    
    compose_yaml = generate_compose_yaml(num_clients)
    with open(output_filename, 'w') as f:
        f.write(compose_yaml)
    sys.exit(0)
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
                'environment': ['PYTHONUNBUFFERED=1', 'LOGGING_LEVEL=DEBUG'],
                'networks': ['testing_net']
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
            'environment': [f'CLI_ID={i}', 'CLI_LOG_LEVEL=DEBUG'],
            'networks': ['testing_net'],
            'depends_on': ['server']
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
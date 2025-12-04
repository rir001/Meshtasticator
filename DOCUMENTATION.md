# Interactive Simulation

## Consideraciones

### Numero de nodos
Para 4 nodos funciona bien, para más de esto es necesario aumentar el lsof del terminal donde se ejecuta:
```
ulimit -n 65536
sudo sysctl -w net.core.rmem_max=26214400
sudo sysctl -w net.core.rmem_default=26214400

sudo sysctl -w net.core.wmem_max=26214400
sudo sysctl -w net.core.wmem_default=26214400

sudo sysctl -w net.core.netdev_max_backlog=10000

sudo ip link set lo txqueuelen 20000

sudo sysctl -w net.ipv4.igmp_max_memberships=100
```

Esto corrige el problema pero se espera encontrar una solución alternativa.

En caso de no ejecutarse, los nodos extra no se conectan, es posible verificar esto con el comando:
```
sudo lsof -i :{TCP_PORT}
```

Pada facilitar esta labor se implementó el codigo [viewPorts.py](./viewPorts.py)



## Simulación

Para utilizar el simulador es necesario ejecutar [interactiveSim.py](./interactiveSim.py).
Este tiene los siguintes CLI args: 

- `-s` / `--script` : Para ejecutar es script dentro del mismo archivo.
- `-d` / `--docker` : Para ejecutar el simulador desde doker.
- `--from-file` : Para indicar que los nodos se ubicarán como el archivo [nodeConfig.yaml](./out/nodeConfig.yaml).
- `-f` / `--forward`
- `-p` / `--program` : Para indicar el path del firmware antes de ejecutarlo.
- `-c` / `--collisions`
- `nrNodes`: Numero de nodos.






### Comandos de simulación



cmd
- help
    list commands

- broadcast

- dm

- [?] nodes <id0> [id1, etc.]

- ping

- remove <id>

- [X] req_pos <fromNode> <toNode>

- traceroute

- plot

- exit





cd Documents/uc/drone/meshtasticator/Meshtasticator
source venv/bin/activate
ulimit -n 16384
python interactiveSim.py 4 -s
python interactiveSim.py -s --from-file





watch -n 0.5 'ss -tulpn | grep program'



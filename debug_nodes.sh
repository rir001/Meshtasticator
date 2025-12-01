#!/bin/bash
BIN="/home/rir/Documents/uc/drone/meshtasticator/Meshtasticator/program"
BASE_DIR="/home/rir/.portduino"

echo "--- Iniciando Debug de 5 Nodos ---"

# Lanzamos 5 nodos en background
for i in {0..4}
do
    PORT=$((4403 + i))
    DIR="$BASE_DIR/node$i"
    mkdir -p "$DIR"
    
    echo "Lanzando Nodo $i en puerto $PORT..."
    # -s = simulator, -d = config dir, -h = hwid (usamos 16+i), -p = port
    $BIN -s -d "$DIR" -h $((16 + i)) -p $PORT > "node$i.log" 2>&1 &
    pids[$i]=$!
    
    # Damos un pequeño respiro entre lanzamientos para no saturar la CPU de golpe
    sleep 1
done

echo "Nodos lanzados. PIDs: ${pids[*]}"
echo "Esperando 10 segundos..."
sleep 10

# Verificamos si siguen vivos
echo "--- Estado de los procesos ---"
for pid in "${pids[@]}"; do
    if ps -p $pid > /dev/null; then
        echo "PID $pid: VIVO"
    else
        echo "PID $pid: MUERTO (Revisar logs)"
    fi
done

echo "--- Presiona Ctrl+C para terminar y matar los procesos ---"
wait

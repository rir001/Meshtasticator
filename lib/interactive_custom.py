import time
import csv
from datetime import datetime
from lib.interactive import InteractiveSim, CommandProcessor
from meshtastic import portnums_pb2

def get_time():
    return datetime.now().strftime("%H:%M:%S.%f")


class InteractiveSim(InteractiveSim):

    def __init__(self, args):
        t_start = time.time()
        self.ping_stats = {}  # Transient stats for in-flight pings
        self.ping_results = {}  # Completed ping results: (from_node, to_node) -> {'rtt': float, 'hops': int}
        super().__init__(args)
        t_end = time.time()
        print(f"Simulator started in {t_end - t_start:.2f} seconds")


    def forward_packet(self, receivers, packet, rssis, snrs):
        super().forward_packet(receivers, packet, rssis, snrs)
        
        decoded = packet.get('decoded', {})
        portnum = decoded.get('portnum')
        
        # Handle Simulator wrapping
        if portnum == 'SIMULATOR_APP' or portnum == portnums_pb2.PortNum.SIMULATOR_APP:
            sim_decoded = decoded.get('simulator', {})
            real_portnum = sim_decoded.get('portnum')
        else:
            real_portnum = portnum

        is_reply_app = real_portnum == 'REPLY_APP' or real_portnum == portnums_pb2.PortNum.REPLY_APP
        
        # DEBUG
        print(f"DEBUG: ID={packet['id']} From={packet['from']} To={packet['to']} Port={portnum} RealPort={real_portnum}")

        # Check Ping Request Reaching Destination
        if is_reply_app and 'requestId' not in decoded:
            pkt_id = packet['id']
            if pkt_id in self.ping_stats:
                dest_hwid = packet['to']
                # Check if destination is in receivers
                if any(r.hwId == dest_hwid for r in receivers):
                    initial_hl = self.ping_stats[pkt_id]['initial_hl']
                    current_hl = packet.get('hopLimit', 0)
                    hops = (initial_hl - current_hl) + 1
                    self.ping_stats[pkt_id]['req_hops'] = hops
                    # print(f"DEBUG: Ping Request reached dest. Hops={hops}")
        
        # Check Ping Reply Reaching Origin
        if 'requestId' in decoded:
            req_id = decoded['requestId']
            if req_id in self.ping_stats:
                origin_hwid = self.ping_stats[req_id]['from']
                if any(r.hwId == origin_hwid for r in receivers):
                    # Reached origin
                    hop_start = packet.get('hopStart', 3)
                    current_hl = packet.get('hopLimit', 0)
                    hops_rep = (hop_start - current_hl) + 1
                    
                    total_hops = self.ping_stats[req_id]['req_hops'] + hops_rep
                    rtt = time.time() - self.ping_stats[req_id]['start_time']
                    
                    # Store in ping_results - convert hwId to nodeId (HW_ID_OFFSET is 16)
                    from_node = origin_hwid - 16
                    to_node = packet['from'] - 16
                    
                    # Only store if no previous result or if this one is faster (shorter RTT = BFS path)
                    key = (from_node, to_node)
                    if key not in self.ping_results or rtt < self.ping_results[key]['rtt']:
                        self.ping_results[key] = {
                            'rtt': rtt,
                            'hops': total_hops
                        }
                        print(f"[{get_time()}] Ping reply from N{to_node} to N{from_node}: RTT={rtt:.2f}s, Hops={total_hops}")
                    else:
                        print(f"[{get_time()}] Ping reply from N{to_node} to N{from_node}: RTT={rtt:.2f}s, Hops={total_hops} (ignored, slower path)")
                    
                    # del self.ping_stats[req_id]
            else:
                 pass
                 # print(f"DEBUG: Reply with RequestId {req_id} not found in stats.")

        for node in receivers:
            print(f"[{get_time()}] N{node.nodeid} recibió el mensaje con ID: {packet['id']}.")

    def on_receive(self, interface, packet):
        decoded = packet.get('decoded', {})
        portnum = decoded.get('portnum')
        
        if portnum == 'SIMULATOR_APP' or portnum == portnums_pb2.PortNum.SIMULATOR_APP:
            sim_decoded = decoded.get('simulator', {})
            real_portnum = sim_decoded.get('portnum')
        else:
            real_portnum = portnum

        is_reply_app = real_portnum == 'REPLY_APP' or real_portnum == portnums_pb2.PortNum.REPLY_APP
        
        if is_reply_app and 'requestId' not in decoded:
             pkt_id = packet['id']
             self.ping_stats[pkt_id] = {
                 'start_time': time.time(),
                 'from': packet['from'],
                 'to': packet['to'],
                 'initial_hl': packet.get('hopLimit', 3),
                 'req_hops': 0
             }
        super().on_receive(interface, packet)

    def send_broadcast(self, text, fromNode):
        print(f"[{get_time()}] N{fromNode} enviando broadcast: {text}")
        super().send_broadcast(text, fromNode)

    def send_ping(self, fromNode, toNode):
        print(f"[{get_time()}] N{fromNode} enviando ping a N{toNode}")
        super().send_ping(fromNode, toNode)

    def trace_route(self, fromNode, toNode):
        print(f"[{get_time()}] N{fromNode} enviando trace route a N{toNode}")
        super().trace_route(fromNode, toNode)

    def send_dm(self, text, fromNode, toNode):
        print(f"[{get_time()}] N{fromNode} enviando DM a N{toNode}: {text}")
        super().send_dm(text, fromNode, toNode)

    def request_position(self, fromNode, toNode):
        print(f"[{get_time()}] N{fromNode} solicitando posición a N{toNode}")
        super().request_position(fromNode, toNode)

    def traceroute_all_combinations(self, wait_time=10):
        """
        Send traceroute between all combinations of nodes.
        Args:
            wait_time: Time to wait after each traceroute for reply (seconds)
        """
        print(f"\n{'='*60}")
        print(f"[{get_time()}] Iniciando traceroute entre todas las combinaciones de nodos")
        print(f"{'='*60}")
        
        num_nodes = len(self.nodes)
        total_routes = num_nodes * (num_nodes - 1)  # All pairs excluding self
        completed = 0
        
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i != j:  # Skip self-traceroute
                    completed += 1
                    print(f"\n[{get_time()}] Traceroute {completed}/{total_routes}: N{i} -> N{j}")
                    self.trace_route(i, j)
                    time.sleep(wait_time)
        
        print(f"\n[{get_time()}] Traceroutes completados. Esperando respuestas finales...")
        time.sleep(5)  # Extra wait for any pending replies

    def ping_all_combinations(self, wait_time=10):
        """
        Send pings between all combinations of nodes and wait for results.
        Args:
            wait_time: Time to wait after each ping for reply (seconds)
        """
        print(f"\n{'='*60}")
        print(f"[{get_time()}] Iniciando pings entre todas las combinaciones de nodos")
        print(f"{'='*60}")
        
        num_nodes = len(self.nodes)
        total_pings = num_nodes * (num_nodes - 1)  # All pairs excluding self-ping
        completed = 0
        
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i != j:  # Skip self-ping
                    completed += 1
                    print(f"\n[{get_time()}] Ping {completed}/{total_pings}: N{i} -> N{j}")
                    self.send_ping(i, j)
                    time.sleep(wait_time)
        
        print(f"\n[{get_time()}] Pings completados. Esperando respuestas finales...")
        time.sleep(5)  # Extra wait for any pending replies

    def get_network_analysis(self):
        """
        Analyze ping results and return network statistics.
        Returns a dictionary with:
        - max_rtt: Maximum round-trip time and the node pair
        - max_hops: Maximum hops and the node pair
        - avg_rtt: Average round-trip time
        - avg_hops: Average number of hops
        - results_matrix: Dictionary of all results
        - missing_pairs: List of node pairs without results
        """
        if not self.ping_results:
            print("No hay resultados de ping aún.")
            return None
        
        results = {
            'max_rtt': {'value': 0, 'pair': None},
            'max_hops': {'value': 0, 'pair': None},
            'min_rtt': {'value': float('inf'), 'pair': None},
            'min_hops': {'value': float('inf'), 'pair': None},
            'avg_rtt': 0,
            'avg_hops': 0,
            'results_matrix': self.ping_results.copy(),
            'missing_pairs': [],
            'total_pairs': 0,
            'successful_pairs': 0
        }
        
        total_rtt = 0
        total_hops = 0
        count = 0
        
        for (from_node, to_node), data in self.ping_results.items():
            rtt = data['rtt']
            hops = data['hops']
            
            if rtt > results['max_rtt']['value']:
                results['max_rtt']['value'] = rtt
                results['max_rtt']['pair'] = (from_node, to_node)
            
            if rtt < results['min_rtt']['value']:
                results['min_rtt']['value'] = rtt
                results['min_rtt']['pair'] = (from_node, to_node)
            
            if hops > results['max_hops']['value']:
                results['max_hops']['value'] = hops
                results['max_hops']['pair'] = (from_node, to_node)
            
            if hops < results['min_hops']['value']:
                results['min_hops']['value'] = hops
                results['min_hops']['pair'] = (from_node, to_node)
            
            total_rtt += rtt
            total_hops += hops
            count += 1
        
        if count > 0:
            results['avg_rtt'] = total_rtt / count
            results['avg_hops'] = total_hops / count
        
        # Find missing pairs
        num_nodes = len(self.nodes)
        results['total_pairs'] = num_nodes * (num_nodes - 1)
        results['successful_pairs'] = count
        
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i != j and (i, j) not in self.ping_results:
                    results['missing_pairs'].append((i, j))
        
        return results

    def print_network_analysis(self):
        """Print a formatted network analysis report."""
        analysis = self.get_network_analysis()
        if not analysis:
            return
        
        print(f"\n{'='*60}")
        print(f"         ANÁLISIS DE RED - LATENCIA Y SALTOS")
        print(f"{'='*60}")
        
        print(f"\nESTADÍSTICAS GENERALES:")
        print(f"   Pares exitosos: {analysis['successful_pairs']}/{analysis['total_pairs']}")
        
        print(f"\nLATENCIA (RTT):")
        if analysis['max_rtt']['pair']:
            print(f"   Máxima: {analysis['max_rtt']['value']:.2f}s (N{analysis['max_rtt']['pair'][0]} -> N{analysis['max_rtt']['pair'][1]})")
        if analysis['min_rtt']['pair']:
            print(f"   Mínima: {analysis['min_rtt']['value']:.2f}s (N{analysis['min_rtt']['pair'][0]} -> N{analysis['min_rtt']['pair'][1]})")
        print(f"   Promedio: {analysis['avg_rtt']:.2f}s")
        
        print(f"\nSALTOS (HOPS):")
        if analysis['max_hops']['pair']:
            print(f"   Máximo: {analysis['max_hops']['value']} (N{analysis['max_hops']['pair'][0]} -> N{analysis['max_hops']['pair'][1]})")
        if analysis['min_hops']['pair']:
            print(f"   Mínimo: {analysis['min_hops']['value']} (N{analysis['min_hops']['pair'][0]} -> N{analysis['min_hops']['pair'][1]})")
        print(f"   Promedio: {analysis['avg_hops']:.1f}")
        
        if analysis['missing_pairs']:
            print(f"\nPARES SIN RESPUESTA ({len(analysis['missing_pairs'])}):")
            for pair in analysis['missing_pairs']:
                print(f"   N{pair[0]} -> N{pair[1]}")
        
        # Print results matrix
        print(f"\nMATRIZ DE RESULTADOS:")
        print(f"   {'From/To':<8}", end="")
        num_nodes = len(self.nodes)
        for j in range(num_nodes):
            print(f"{'N'+str(j):>12}", end="")
        print()
        
        for i in range(num_nodes):
            print(f"   N{i:<7}", end="")
            for j in range(num_nodes):
                if i == j:
                    print(f"{'---':>12}", end="")
                elif (i, j) in self.ping_results:
                    data = self.ping_results[(i, j)]
                    print(f"{data['rtt']:.1f}s-{data['hops']}H".rjust(12), end="")
                else:
                    print(f"{'FAIL':>12}", end="")
            print()
        
        print(f"\n{'='*60}\n")

    def export_results_csv(self, filename="network_analysis.csv"):
        """
        Export ping results to a CSV file.
        Args:
            filename: Name of the CSV file to create
        """
        if not self.ping_results:
            print("No hay resultados para exportar.")
            return
        
        analysis = self.get_network_analysis()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"out/{timestamp}_{filename}"
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header with summary
            writer.writerow(['# Network Analysis Results'])
            writer.writerow(['# Timestamp', timestamp])
            writer.writerow(['# Successful Pairs', f"{analysis['successful_pairs']}/{analysis['total_pairs']}"])
            writer.writerow(['# Max RTT', f"{analysis['max_rtt']['value']:.2f}s", f"N{analysis['max_rtt']['pair'][0]}->N{analysis['max_rtt']['pair'][1]}"])
            writer.writerow(['# Max Hops', analysis['max_hops']['value'], f"N{analysis['max_hops']['pair'][0]}->N{analysis['max_hops']['pair'][1]}"])
            writer.writerow(['# Avg RTT', f"{analysis['avg_rtt']:.2f}s"])
            writer.writerow(['# Avg Hops', f"{analysis['avg_hops']:.1f}"])
            writer.writerow([])
            
            # Detailed results
            writer.writerow(['from_node', 'to_node', 'rtt_seconds', 'hops', 'status'])
            
            num_nodes = len(self.nodes)
            for i in range(num_nodes):
                for j in range(num_nodes):
                    if i != j:
                        if (i, j) in self.ping_results:
                            data = self.ping_results[(i, j)]
                            writer.writerow([i, j, f"{data['rtt']:.3f}", data['hops'], 'SUCCESS'])
                        else:
                            writer.writerow([i, j, '', '', 'FAIL'])
        
        print(f"Resultados exportados a: {output_file}")
        return output_file
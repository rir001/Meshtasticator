import time
from datetime import datetime
from lib.interactive import InteractiveSim, CommandProcessor

def get_time():
    return datetime.now().strftime("%H:%M:%S.%f")


class InteractiveSim(InteractiveSim):

    def __init__(self, args):
        t_start = time.time()
        super().__init__(args)
        t_end = time.time()
        print(f"Simulator started in {t_end - t_start:.2f} seconds")


    def forward_packet(self, receivers, packet, rssis, snrs):
        super().forward_packet(receivers, packet, rssis, snrs)
        for node in receivers:
            print(f"[{get_time()}] N{node.nodeid} recibió el mensaje con ID: {packet['id']}.")

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
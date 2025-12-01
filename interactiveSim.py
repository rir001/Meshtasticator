#!/usr/bin/env python3
""" Simulator for letting multiple instances of native programs communicate via TCP as if they did via their LoRa chip.
    Usage: python3 interactiveSim.py [nrNodes] [-p <full-path-to-program>] [-d] [-s]
    Use '-d' for Docker.
    Use '-s' to specify what should be sent using this script.
"""
import os
import time
import argparse
from lib.interactive import CommandProcessor
from lib.interactive_custom import InteractiveSim

parser = argparse.ArgumentParser(prog='interactiveSim')
parser.add_argument('-s', '--script', action='store_true')
parser.add_argument('-d', '--docker', action='store_true')
parser.add_argument('--from-file', action='store_true')
parser.add_argument('-f', '--forward', action='store_true')
parser.add_argument('-p', '--program', type=str, default=os.getcwd())
parser.add_argument('-c', '--collisions', action='store_true')
parser.add_argument('nrNodes', type=int, nargs='?', choices=range(0, 11), default=0)


sim = InteractiveSim(parser.parse_args())


if sim.script: 
    try:
        time.sleep(45)
        sim.show_nodes()

        print("pings")
        for i in range(len(sim.nodes)):
            sim.send_broadcast("Hi all", i)
            time.sleep(10)

            for j in range(len(sim.nodes)):
                print(i, j)    
                sim.send_ping(i, j)
                time.sleep(10)
                sim.trace_route(i, j)
                time.sleep(10)


        time.sleep(1)  # Wait until messages are sent
        sim.graph.plot_metrics(sim.nodes)  # Plot airtime metrics
        sim.graph.init_routes(sim)  # Visualize the route of messages sent
    except KeyboardInterrupt:
        sim.graph.plot_metrics(sim.nodes)
        sim.graph.init_routes(sim)
else:  # Normal usage with commands
    CommandProcessor().cmdloop(sim)

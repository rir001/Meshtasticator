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
from lib.interactive import InteractiveSim

parser = argparse.ArgumentParser(prog='interactiveSim')
parser.add_argument('-s', '--script', action='store_true')
parser.add_argument('-d', '--docker', action='store_true')
parser.add_argument('--from-file', action='store_true')
parser.add_argument('-f', '--forward', action='store_true')
parser.add_argument('-p', '--program', type=str, default=os.getcwd())
parser.add_argument('-c', '--collisions', action='store_true')
parser.add_argument('nrNodes', type=int, nargs='?', choices=range(0, 20), default=0)


sim = InteractiveSim(parser.parse_args())


if sim.script: 
    try:
        sim.show_nodes()

        n_nodes = len(sim.nodes)
        print(f"\nNodos: {n_nodes}")
        t = (n_nodes ** 2) * 6
        print(f"Tiempo estimado: {t}")
        time.sleep(t)
        sim.show_nodes()


    except KeyboardInterrupt:
        sim.print_network_analysis()  # Show analysis on interrupt
        sim.graph.plot_metrics(sim.nodes)
        sim.graph.init_routes(sim)

else:
    CommandProcessor().cmdloop(sim)

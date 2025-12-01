import os
import argparse
#from lib.interactive import TCP_PORT_OFFSET

TCP_PORT_OFFSET = 4404


parser = argparse.ArgumentParser(prog='testPorts')
parser.add_argument('nrNodes', type=int, nargs='?', choices=range(0, 11), default=0)
parser.add_argument('TCPPortOffset', type=int, nargs='?', default=TCP_PORT_OFFSET)
args = parser.parse_args()

os.system("clear")

for n in range(args.nrNodes):
    print(n)
    print(TCP_PORT_OFFSET + n)
    os.system(f"sudo lsof -i :{TCP_PORT_OFFSET + n}")


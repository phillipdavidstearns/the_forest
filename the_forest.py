#!/usr/bin/python3

#------------------------------------------------------
#
# the_forest.py
#
# A script to translate network traffic into lighting control
# should be run on a raspberry pi.
# Raspberry Pi needs to be connected to a network
# Raspberry Pi GPIO is used to output controlsignals
# via a 4094 shift register
# The output of the shift register can be used to trigger
# devices connected to Solid State Relays.

import os
import sys
import argparse
from signal import *
import socket
import time
import select

if os.getuid() != 0:
	print("Must be run as root.")
	sys.exit(1)

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--socket-blocking", action='store_true', default=False, required=False, help="non-blocking by default")
ap.add_argument("-i", "--interface", default="wlan0", required=False, help="[if]")
ap.add_argument("-c", "--chunk-size", type=int, default=2048, required=False, help="chunk size in frames") # not sure if I need this
ap.add_argument("-r", "--frame-rate", type=int, default=30, required=False, help="frames per second")
ap.add_argument("-t", "--timeout", type=float, default=0.0, required=False, help="socket timeout in seconds")
ap.add_argument("-p", "--print-packet", action='store_true', default=False, required=False, help="print packet to console")
ap.add_argument("-b", "--bytes", type=int, default=4, required=False, help="number of bytes to display per frame")
args = ap.parse_args()

packets = []
SOCKET_BLOCKING = args.socket_blocking
IFACE = args.interface
CHUNK = args.chunk_size
RATE = args.frame_rate
BYTES = args.bytes

if args.timeout > 0.0:
	TIMEOUT = args.timeout
else:
	TIMEOUT = 1 / CHUNK

PRINT = args.print_packet

# sanity check to confirm argument parsing

print("SOCKET_BLOCKING: " + str(SOCKET_BLOCKING))
print("INTERFACE: " + str(IFACE))
print("CHUNK SIZE: " + str(CHUNK))
print("FRAME RATE: " + str(RATE))
print("SOCKET TIMEOUT: " + str(TIMEOUT))

s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
try:
	s.bind((IFACE, 0))
except:
	print("Failed to bind to interface: " + IFACE)
	sys.exit(1)
s.setblocking(SOCKET_BLOCKING)

def read_sockets(socket, buffer):
	if SOCKET_BLOCKING:
		readable,_,_ = select.select(socket, [], [], TIMEOUT)
		for s in readable:
			try:
				data = s.recvfrom(65536)
				if data:
					buffer += data
			except:
				pass
	else:
		if len(buffer) < 65536:
			try:
				data = socket.recv(65536)
				if data:
					buffer += data
			except:
				pass

def extract_frames(buffer, bytes):
	chunk = []
	# assemble bytes into chunk
	for i in range(bytes):
		try:
			byte = buffer[i]
			print(str(i),end=', ')
			print("")
			if PRINT: print(chr(byte),end='')
		except:
			byte = 0
		chunk.append(byte)
		print(chunk)
		print(len(chunk))
		sys.exit(0)
	buffer = buffer[frames:]
	return chunk

def write_packets(packets):
	print(packets)
	for p in range(packets):
		for i in range(8):
			print(str(i>>8&1),end='')
	print("")
	return

def shutdown(socket):
	# bring down the pyaudio stream
	print('Closing socket '+str(IFACE)+'...')
	try:
		socket.close()
	except:
		print("Error closing socket.")
	print('Peace out!')
	sys.exit(0)

# catch control+c
def SIGINT_handler(sig, frame):
	print('\nInterrupt code: ' +str(sig) + ' received!')
	shutdown(s)

# catch termination signals from the system
def SIGTERM_handler(sig, frame):
	print('\nInterrupt code: ' +str(sig) + 'received!')
	shutdown(s)

def main():
	# interrupt and terminate signal handling
	signal(SIGINT, SIGINT_handler)
	signal(SIGTERM, SIGTERM_handler)

	print("Sniffing packets...")

	while True:
		#give the processor a rest
		time.sleep(1/CHUNK)
		read_sockets(s, packets)
		write_packets(extract_frames(packets,bytes))

main()


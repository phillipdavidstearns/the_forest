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
import subprocess
import argparse
from signal import *
import socket
import time
import select
import CD4094 as IO

#------------------------------------------------------------------------
#

def extract_bytes(packets, qty):
	chunk = []
	# assemble bytes into chunk
	for i in range(qty):
		try:
			_byte = packets[i]
			if PRINT: print(chr(_byte),end='')
		except:
			_byte = 0
		chunk.append(_byte)
	packets = packets[qty:]
	return packets, chunk

def write_bytes(data):
	channelStates=[]
	for b in data:
		for i in range(8):
			channelStates.append(b >> i & 1)
			print(str(channelStates[i]),end='')
	print("")
	return channelStates

#------------------------------------------------------------------------
#

def shutdown(socket, sig):
	debug("\nInterrupt code: " + str(sig) + " received!")
	shutdownIO()
	socket.close()
	sys.exit(0)

#------------------------------------------------------------------------
#	Signal Interrupt/Terminate Handlers

# catch control+c
def SIGINT_handler(socket, sig, frame):
	shutdown(socket, sig)

# catch termination signals from the system
def SIGTERM_handler(socket, sig, frame):
	shutdown(socket, sig)

#------------------------------------------------------------------------
# IO up/down

def startupIO():
	IO.init(pins, channels)
	IO.clear()
	IO.enable()

def shutdownIO():
	IO.disable()
	IO.clear()
	IO.cleanup()

#------------------------------------------------------------------------
# main

def main():

	if os.getuid() != 0:
		print("Must be run as root.")
		sys.exit(1)

	ap = argparse.ArgumentParser()
	# ap.add_argument("-s", "--socket-blocking", action='store_true', default=False, required=False, help="non-blocking by default")
	ap.add_argument("-i", "--interface", default="wlan0", required=False, help="[if]")
	ap.add_argument("-c", "--chunk-size", type=float, default=2048, required=False, help="chunk size in frames") # not sure if I need this
	ap.add_argument("-r", "--frame-rate", type=float, default=30, required=False, help="frames per second")
	ap.add_argument("-t", "--timeout", type=float, default=0.0, required=False, help="socket timeout in seconds")
	ap.add_argument("-b", "--frame-size", type=int, default=4, required=False, help="number of bytes to display per frame")
	ap.add_argument('-v', "--verbose", action='store_true', default=False, help='Verbose mode. Display debug messages')
	args = ap.parse_args()

	# SOCKET_BLOCKING = args.socket_blocking
	IFACE = args.interface
	CHUNK = args.chunk_size
	RATE = args.frame_rate
	BYTES = args.frame_size
	verbose=args.verbose
	# future: make arguments for these
	TIMEOUT=10 
	HOST = ''
	PORT = 31337
	
	#------------------------------------------------------------------------
	#	verbose or debug mode

	def debug(message):
		if verbose:
			print(message)

	if verbose:
		debug("Verbose mode. Displaying debug messeges")

	if args.timeout > 0.0:
		TIMEOUT = args.timeout
	else:
		TIMEOUT = 1 / CHUNK

	# sanity check to confirm argument parsing

	# debug("SOCKET_BLOCKING: " + str(SOCKET_BLOCKING))
	debug("INTERFACE: " + str(IFACE))
	debug("CHUNK SIZE: " + str(CHUNK))
	debug("FRAME RATE: " + str(RATE))
	debug("SOCKET TIMEOUT: " + str(TIMEOUT))

	# initalize TCP socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# interrupt and terminate signal handling
	signal(s, SIGINT, SIGINT_handler)
	signal(s, SIGTERM, SIGTERM_handler)
	packets = []
	startupIO()

	channels = 32 # number of output channels

	# Pin assignments
	# outputs
	strobe = 17 # latch strobe GPIO pin
	data = 27 # data GPIO pin
	clock = 22 # clock GPIO pin
	enable = 23 # IOister enable GPIO pin

	# make composite lists to pass along to IO
	pins = [ strobe, data, clock, enable ]

	# from example at https://docs.python.org/3.7/library/socket.html#example
	
	try:
		s.bind((HOST, PORT))
	except:
		debug("Could not bind socket")
		s.close()
		sys.exit(1)
	s.listen(1)

	while True:
		conn, addr = s.accept()
		with conn:
			debug('Connected from' + str(addr))
			while True:
				data = conn.recv(CHUNK)
				if not data: break
				packets += data
				while len(packets) > 0:
					packets, chunk = extract_bytes(packets, BYTES)
					print(packets)
					IO.update(write_bytes(chunk))
					time.sleep(1/RATE)
				try:
					message = data.decode('UTF-8').split('\r')[0]
				except:
					pass
				if message == "exit":
					debug("Closing connection...")
					conn.shutdown(socket.SHUT_RDWR)
					conn.close()
					break


if __name__ == '__main__':
	main()

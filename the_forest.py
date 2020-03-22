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

# object for our socket
s = object()

#------------------------------------------------------------------------
#

def extract_bytes(packets, qty):
	chunk = []*qty
	# assemble bytes into chunk
	for i in range(qty):
		try:
			_byte = packets[i]
		except:
			_byte = 0
		chunk.append(_byte)
	packets = packets[qty:]
	return packets, chunk

def write_bytes(data, channels):
	channelStates=[]*channels
	for i in range(len(data)):
		b = data[i]
		for j in range(8):
			channelStates.append(b >> j & 1)
	# print(channelStates)
	return channelStates

#------------------------------------------------------------------------
#

def shutdown(s, sig):
	print("")
	shutdownIO()
	s.shutdown(socket.SHUT_RDWR)
	s.close()
	sys.exit(0)

#------------------------------------------------------------------------
#	Signal Interrupt/Terminate Handlers

# catch control+c
def SIGINT_handler(sig, frame):
	shutdown(s, sig)

# catch termination signals from the system
def SIGTERM_handler(sig, frame):
	shutdown(s, sig)

#------------------------------------------------------------------------
# IO up/down

def startupIO(pins, channels):
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

	global s
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# interrupt and terminate signal handling
	signal(SIGINT, SIGINT_handler)
	signal(SIGTERM, SIGTERM_handler)

	#-------------------------------------------------------------------
	# argument stuff
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--interface", default="wlan0", required=False, help="[if]")
	ap.add_argument("-l","--lhost-ip", default="", required=False, help="LHOST IP")
	ap.add_argument("-p","--lhost-port", type=int, default=31337, required=False, help="LHOST PORT")
	ap.add_argument("-c", "--chunk-size", type=float, default=2048, required=False, help="chunk size in frames") # not sure if I need this
	ap.add_argument("-r", "--frame-rate", type=float, default=30, required=False, help="frames per second")
	ap.add_argument("-b", "--frame-size", type=int, default=4, required=False, help="number of bytes to display per frame")
	ap.add_argument('-v', "--verbose", action='store_true', default=False, help='Verbose mode. Display debug messages')
	args = ap.parse_args()

	IFACE = args.interface
	CHUNK = args.chunk_size
	RATE = args.frame_rate
	BYTES = args.frame_size
	VERBOSE = args.verbose
	HOST = ''
	PORT = 31337

	#------------------------------------------------------------------------
	#	verbose or debug mode

	def debug(message):
		if VERBOSE:
			print(message)

	if VERBOSE:
		debug("Verbose mode. Displaying debug messeges")

	# initalize TCP socket

	# from example at https://docs.python.org/3.7/library/socket.html#example
	try:
		s.bind((HOST, PORT))
	except:
		print("Could not bind socket"+ str(HOST) +":" +str(PORT))
		s.close()
		sys.exit(1)
	s.listen(1)

	packets = []

	channels = 32 # number of output channels

	# Pin assignments
	# outputs
	strobe = 17 # latch strobe GPIO pin
	data = 27 # data GPIO pin
	clock = 22 # clock GPIO pin
	enable = 23 # IOister enable GPIO pin
	# make composite lists to pass along to IO
	pins = [ strobe, data, clock, enable ]
	startupIO(pins, channels)

	while True:
		messages = []
		conn, addr = s.accept()
		with conn:
			debug('Connected from' + str(addr))
			while True:
				data = conn.recv(CHUNK)
				if not data: break
				try: 
					for line in data.decode('UTF-8'):
						messages += line.rstrip('\r\n')
				except:
					pass
				
				for message in messages:
					print(message)
					if message == "close":
						debug("Closing connection...")
						conn.shutdown(socket.SHUT_RDWR)
						conn.close()
						break
					packets += message.encode()
				# while len(packets) > 0 and len(packets) >= 4:
					packets, chunk = extract_bytes(packets, BYTES)
					IO.update(write_bytes(chunk, channels))
					time.sleep(1/RATE)


if __name__ == '__main__':
	main()

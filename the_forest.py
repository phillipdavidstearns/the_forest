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
import pyaudio
import time
import select
import re

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
args = ap.parse_args()

SOCKET_BLOCKING
IFACE = args.interface
CHUNIK = args.chunk_size
FRAME = args.frame_rate

if args.timeout > 0.0:
	TIMEOUT = args.timeout
else:
	TIMEOUT = 1 / CHUNK

PRINT = args.print_packet

s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
try:
	s.bind(IFACE, 0)
except:
	print("Failed to bind to interface: "+IFACE)
	sys.exit(1)


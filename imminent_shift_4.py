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
import time
import CD4094 as IO
from ShiftRegister import ShiftRegister

#------------------------------------------------------------------------
#

def shutdown():
	IO.stop()
	sys.exit(0)

#------------------------------------------------------------------------
#	Signal Interrupt/Terminate Handlers

# catch control+c
def SIGINT_handler(sig, frame):
	shutdown()

# catch termination signals from the system
def SIGTERM_handler(sig, frame):
	shutdown()

#------------------------------------------------------------------------
# main

def main():

	lfsr = ShiftRegister()
	lfsr.randomize()

	if os.getuid() != 0:
		print("Must be run as root.")
		sys.exit(1)

	# interrupt and terminate signal handling
	signal(SIGINT, SIGINT_handler)
	signal(SIGTERM, SIGTERM_handler)

	#-------------------------------------------------------------------
	# argument stuff
	ap = argparse.ArgumentParser()
	ap.add_argument("-r", "--frame-rate", type=float, default=30, required=False, help="frames per second")
	ap.add_argument('-v', "--verbose", action='store_true', default=False, help='Verbose mode. Display debug messages')
	args = ap.parse_args()

	RATE = args.frame_rate
	VERBOSE = args.verbose

	#------------------------------------------------------------------------
	#	verbose or debug mode

	def debug(message):
		if VERBOSE:
			print(message)

	if VERBOSE:
		debug("Verbose mode. Displaying debug messeges")

	
	channels = 32 # number of output channels

	# Pin assignments
	# outputs
	strobe = 17 # latch strobe GPIO pin
	data = 27 # data GPIO pin
	clock = 22 # clock GPIO pin
	enable = 23 # IOister enable GPIO pin
	# make composite lists to pass along to IO
	pins = [ strobe, data, clock, enable ]
	IO.init(pins, channels)

	while True:
		start_time = time.time()
		output=lfsr.lfsrLeft()
		print(output)
		IO.update(output)
		stop_time = time.time()
		time.sleep((1/RATE) - ( stop_time - start_time ))

if __name__ == '__main__':
	main()

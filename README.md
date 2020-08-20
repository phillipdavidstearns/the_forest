# The Forest

A network accessible interactive light installation made for [Brahman-Ai](https://brahman.ai).

## Hardware

* Made for Raspberry Pi
* Tested on Raspberry Pi Zero W, Raspberry Pi 3 B+, Raspberry Pi 4 B
* See [2DollarDMX](https://github.com/phillipdavidstearns/2DollarDMX) for more details.

## Installation

* clone this repo locally: `git clone`

### Requirements:

* Install [`rpi-cd4094`](https://github.com/phillipdavidstearns/rpi-cd4094)
  1. `ssh` into your Raspberry Pi
  1. Clone rpi-cd4094: `git clone https://github.com/phillipdavidstearns/rpi-cd4094.git`
  1. Install rpi-cd4094: `cd rpi-cd4094; sudo python3 setup.py install`

### the_forest.py

* run from the local cloned repo: `sudo python3 the_forest.py`
* Install as systemd servie
  1. You'll have to modify the service file to include the actual path to `the_forest.py`
  1. `sudo cp the_forest.service /lib/systemd/system/`
  1. `sudo systemctl daemon-relaod` 
  1. `sudo systemctl start the_forest.service`
  
### wifi_traffic.py

* run from the local cloned repo: `sudo python3 wifi_traffic.py`
* Install as systemd servie
  1. You'll have to modify the service file to include the actual path to `wifi_traffic.py`
  1. `sudo cp wifi_traffic.service /lib/systemd/system/`
  1. `sudo systemctl daemon-relaod` 
  1. `sudo systemctl start wifi_traffic.service`

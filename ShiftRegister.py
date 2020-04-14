#!/usr/bin/python3
from random import randint

class ShiftRegister:

	def __init__(self, channels=32, tap1=16, tap1_en=True, tap2=15, tap2_en=True):
		self.register = [0]*channels
		self.tap1 = tap1
		self.tap1_en = tap1_en
		self.tap2 = tap2
		self.tap2_en = tap2_en

	def set(self, Q):
		if len(Q) == len(self.register):
			self.register = Q

	def setBit(self, Q, val):
		if Q < len(self.register):
			if val == 0:
				self.register[Q] = 0
			else:
				self.register[Q] = 1
	def randomize(self):
		for i in range(len(self.register)):
			self.register[i] = randint(0,1)
		return self.register

	def getBit(self, Q):
		if Q < len(self.register):
			return self.register[Q]
		else:
			return 0

	def shiftLeft(self, data=0):
		temp = [0] * len(self.register)
		for i in range(len(self.register)):
			if i > 0:
				temp[i] = self.register[i-1]
			elif i <= 0:
				temp[i] = data
		self.register = temp
		return self.register

	def shiftRight(self, data=0):
		temp = [0] * len(self.register)
		for i in range(len(self.register)):
			if i < len(self.register)-1:
				temp[i]=self.register[i+1]
			elif i == len(self.register)-1:
				temp[i] = data
		self.register = temp
		return self.register

	def lfsrLeft(self, data=-1):
		t1 = self.register[self.tap1] & self.tap1_en
		t2 = self.register[self.tap2] & self.tap2_en
		data = t1 ^ t2
		self.shiftLeft(data)
		return self.register

	def lfsrRight(self, data=-1):
		if data = -1:
			t1 = self.register[self.tap1] & self.tap1_en
			t2 = self.register[self.tap2] & self.tap2_en
			data = t1 ^ t2
		self.shiftRight(data)
		return self.register

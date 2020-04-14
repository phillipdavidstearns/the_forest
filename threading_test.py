#!/usr/bin/python3

from threading import Timer

class Repeater(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class Counter:

	UP = 1
	DOWN = 0

	def __init__(self):
		self.count = 0
		self.clk = 0
		self.direction = self.UP

	def clock(self,clk):
		if self.clk == 0 and clk == 1:
			if self.direction == self.UP:
				self.inc()
			elif self.direction == self.DOWN:
				self.dec()
		self.clk = clk
		return self.count

	def get(self,Q):
		if Q < 32 and Q >= 0:
			return self.count >> Q & 1
		else:
			return 0

	def inc(self):
		self.count += 1
		return self.count

	def dec(self):
		self.count += 1
		return self.count

class Toggle:
	def __init__(self):
		self.state = 0

	def toggle(self):
		self.state ^= 1
		return self.state

	def get(self):
		return self.state

	def set(self,state):
		if state == 1:
			self.state = 1
		else:
			self.state = 0
		return self.state

c=Counter()
t=Toggle()

# def count(c):
# 	print(c.inc())

# def toggle(t):
# 	print(t.toggle())

def displayCount(c, t):
	c.clock(t.toggle())
	print(c.get(3))

t1 = Repeater(0.125, displayCount, [c, t])
t1.start()

from threading import Timer
import time

def printit():
	Timer(1.0, printit).start()
	print "Hello, World!"

printit()


for i in range(100):
	print i
	time.sleep(1)
# continue with the rest of your code
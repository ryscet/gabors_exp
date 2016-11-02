#!python2
from psychopy import parallel, core
port = parallel.ParallelPort(53504)
print(port)
port.setData(255)
core.wait(2)
port.setData(0)
out = port.readData()
print(out)
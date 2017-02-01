import numpy as np 
import matplotlib.pyplot as plt

def exponential_function(x):
    return 2**(-0.5*x +4)


plt.style.use('ggplot')

steps = np.arange(0, 13, 1)

fig, axes = plt.subplots()

exp_y = np.array([exponential_function(x) for x in steps])

axes.plot(steps, exp_y)
axes.scatter(steps, exp_y)

plt.show()


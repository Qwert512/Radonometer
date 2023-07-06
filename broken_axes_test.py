import matplotlib.pyplot as plt
from brokenaxes import brokenaxes
import numpy as np

fig = plt.figure(figsize=(10, 4))
bax = brokenaxes(xlims=((0, .1), (.4, .7), (1, 1.3)), ylims=[(-1, 1)], hspace=.05)
x = np.linspace(0, 1.3, 100)
bax.plot(x, np.sin(10 * x), label='sin')
bax.plot(x, np.cos(10 * x), label='cos')
bax.legend(loc=3)
bax.set_xlabel('time')
bax.set_ylabel('value')
plt.title("broken on the inside")
plt.savefig("broken.png")
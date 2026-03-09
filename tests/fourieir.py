from scipy.fft import fft, fftfreq
import numpy as np
# Number of sample points
N = 1000
# sample spacing
T = (1/N)*10


x = np.linspace(0.0, N*T, N, endpoint=False)
# y = np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)

# def input_force(t):
#     return np.sin(10*t/np.pi) if t <=10 else 0

def input_force(t):
    return np.where(t <= 1, np.sin(2*x*np.pi*0.5), 0)

y = input_force(x)
# y = np.sin(2*np.pi*x*10)

yf = fft(y)
xf = fftfreq(N, T)[:N//2]

y_values = 2.0/N * np.abs(yf[0:N//2])
indicies = np.where(y_values >=0.05)[0]
max_considered_freq = xf[indicies[-1]]

print(max_considered_freq)

import matplotlib.pyplot as plt
plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
plt.grid()
plt.show()

plt.plot(x, y)
plt.show()
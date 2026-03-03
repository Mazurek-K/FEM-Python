import numpy as np
import matplotlib.pyplot as plt

# Define Hermite shape functions for a beam element of length L
def N1(x, L):
    xi = x / L
    return 1 - 3 * xi**2 + 2 * xi**3

def N2(x, L):
    xi = x / L
    return x * (1 - xi)**2

def N3(x, L):
    xi = x / L
    return 3 * xi**2 - 2 * xi**3

def N4(x, L):
    xi = x / L
    return x * (xi**2 - xi)

# Parameters
L = 1.0  # Length of the beam element
x = np.linspace(0, L, 100)  # Points along the element

# Evaluate shape functions
N1_values = N1(x, L)
N2_values = N2(x, L)
N3_values = N3(x, L)
N4_values = N4(x, L)

# Plot the shape functions
plt.figure(figsize=(10, 6))
plt.plot(x, N1_values, label=r'$N_1(x)$ (Displacement at Node 1)')
plt.plot(x, N2_values, label=r'$N_2(x)$ (Rotation at Node 1)')
plt.plot(x, N3_values, label=r'$N_3(x)$ (Displacement at Node 2)')
plt.plot(x, N4_values, label=r'$N_4(x)$ (Rotation at Node 2)')

plt.title('Hermite Shape Functions for a Beam Element')
plt.xlabel('x / L')
plt.ylabel('Shape Function Value')
plt.axhline(0, color='black', linewidth=0.5, linestyle='--')
plt.axvline(0, color='black', linewidth=0.5, linestyle='--')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.show()

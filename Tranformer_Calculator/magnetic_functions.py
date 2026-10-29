import matplotlib.pyplot as plt
import numpy as np



def sqr_wave(fs, phase, time):
    T = 1 / fs
    return (((time + phase / 360 * T) % T) < T / 2).astype(int)

def bridge_out(V, totemA, totemB): return V * (totemA - totemB)

def transformer_induction(V, n, A, dt, start=0):
    V = np.asarray(V, dtype=float)
    V = V - np.mean(V)
    B = np.concatenate(([0], np.cumsum(V[:-1]) * dt / (n * A)))
    B = B - (np.max(B) + np.min(B)) / 2

    return start + B
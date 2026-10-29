import numpy as np



VsW = 40
VsB = 90

ILmax = 35e-3
ILmin = 5e-3

Vo = 7
Vz = 3.3
Vref = 2.5

g = Vo/Vref - 1

R2 = 250e3
Ika = 1e-3

Rz = (Vo - Vz) / (35e-3)

R1 = g * R2

Idiv = Vo/(R1 + R2)

Rs = (VsW - Vo) / (Idiv + ILmax + Ika)

Ika = (VsB - Vo) / Rs - Idiv - ILmin

print(f"Rs = {np.round(Rs,2)} Ohm")
print(f"R1 = {np.round(R1,2)} Ohm")
print(f"R2 = {np.round(R2,2)} Ohm")
print(f"Rz = {np.round(Rz,2)} Ohm")

print(Ika)
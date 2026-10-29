import numpy as np
import json

# Unidades: Bmax mT; Ae/Aw mm²; Ve mm³; AL nH/turn²; Ploss mW/cm³.
# Cotas geométricas B, D, E, F y M en mm.
# Aw conserva la convención por mitad de las fórmulas originales.
# Ploss es el límite de ensayo a 25 °C, 100 kHz y 200 mT.

data = [
    {
        'id': '0T42019EC',
        'Bmax': 0.5,
        'Ae': 29,
        # Aw = D * M. M=3.25 es cota de referencia.
        'D': 7.7,
        'M': 3.25,
        'Aw': np.round(7.7 * 3.25, 2),  # 25.02 mm²
        'Ve': 1460,
        'AL': 1540,
        'Ploss': 590
    },
    {
        'id': '0T44444EC',
        'Bmax': 0.5,
        'Ae': 172,
        # Aw = D * (E - F) / 2, por mitad y lado.
        'D': 16.1,
        'E': 32.5,
        'F': 15.2,
        'Aw': np.round(16.1 * (32.5 - 15.2) / 2, 2),  # 139.27 mm²
        'Ve': 17800,
        'AL': 4640,
        'Ploss': 630
    },
    {
        'id': '0T43939EC',
        'Bmax': 0.5,
        'Ae': 123,
        # Aw = D * (E - F) / 2, por mitad y lado.
        'D': 14.2,
        'E': 29.3,
        'F': 12.8,
        'Aw': np.round(14.2 * (29.3 - 12.8) / 2, 2),  # 117.15 mm²
        'Ve': 11500,
        'AL': 3650,
        'Ploss': 500
    },
    {
        'id': '0T-44949-EC',
        'Bmax': 0.5,
        'Ae': 209,
        # Aw = D * (E - F) / 2, por mitad y lado.
        'D': 17.7,
        'E': 36.1,
        'F': 16.7,
        'Aw': np.round(17.7 * (36.1 - 16.7) / 2, 2),  # 171.69 mm²
        'Ve': 24000,
        'AL': 5140,
        'Ploss': 630
    },
    {
        'id': '0T42523EC',
        'Bmax': 0.5,
        'Ae': 55,
        # Aw = D * M. D=9.05 es mínimo; M=3.65 es nominal. Aw nominal no documentado.
        'D': 9.05,
        'M': 3.65,
        'Aw': np.round(9.05 * 3.65, 2),  # 33.03 mm²
        'Ve': 3300,
        'AL': 2660,
        'Ploss': 590
    },
    {
        'id': '0T42625UG',
        'Bmax': 0.5,
        'Ae': 108,
        # Aw = D * (E - F) / 2, por mitad y lado.
        'D': 8.05,
        'E': 22.5,
        'F': 12.0,
        'Aw': np.round(8.05 * (22.5 - 12.0) / 2, 2),  # 42.26 mm²
        'Ve': 6530,
        'AL': 6010,
        'Ploss': 590
    },
    {
        'id': '0T42620UG',
        'Bmax': 0.5,
        'Ae': 109,
        # Aw = D * (E - F) / 2, por mitad y lado.
        'D': 5.75,
        'E': 22.5,
        'F': 12.0,
        'Aw': np.round(5.75 * (22.5 - 12.0) / 2, 2),  # 30.19 mm²
        'Ve': 5470,
        'AL': 7020,
        'Ploss': 590
    },
    {
        'id': '0T42016UG',
        'Bmax': 0.5,
        'Ae': 59.1,
        # Aw = D * (E - F) / 2, por mitad y lado.
        'D': 5.15,
        'E': 18.0,
        'F': 8.8,
        'Aw': np.round(5.15 * (18.0 - 8.8) / 2, 2),  # 23.69 mm²
        'Ve': 2330,
        'AL': 4080,
        'Ploss': 590
    },
    {
        'id': '0T45050UG',
        'Bmax': 0.5,
        'Ae': 314,
        # Aw = D * (E - F) / 2, por mitad y lado.
        'D': 18.05,
        'E': 44.0,
        'F': 20.0,
        'Aw': np.round(18.05 * (44.0 - 20.0) / 2, 2),  # 216.6 mm²
        'Ve': 37100,
        'AL': 9200,
        'Ploss': 630
    },
    {
        'id': '0T43230UG',
        'Bmax': 0.5,
        'Ae': 142,
        # Aw = D * (E - F) / 2, por mitad y lado.
        'D': 10.65,
        'E': 27.5,
        'F': 13.5,
        'Aw': np.round(10.65 * (27.5 - 13.5) / 2, 2),  # 74.55 mm²
        'Ve': 12500,
        'AL': 6570,
        'Ploss': 630
    },
    {
        'id': '0T44040UG',
        'Bmax': 0.5,
        'Ae': 175,
        # Aw = D * (E - F) / 2, por mitad y lado.
        'D': 14.75,
        'E': 37.0,
        'F': 14.9,
        'Aw': np.round(14.75 * (37.0 - 14.9) / 2, 2),  # 162.99 mm²
        'Ve': 20500,
        'AL': 6100,
        'Ploss': 12.9 * 1e6 / 20500
    },
    {
        'id': '0T41506TC',
        'Bmax': 0.5,
        'Ae': 11.2,
        # B: diámetro interior nominal sin recubrimiento.
        'B': 7.37,
        'Aw': np.round(np.pi * 7.37**2 / 4, 2),  # 42.66 mm²
        'Ve': 343,
        'AL': 1320,
        'Ploss': 500
    },
    {
        'id': '0T-40603-TC',
        'Bmax': 0.5,
        'Ae': 4.28,
        # B: diámetro interior nominal sin recubrimiento.
        'B': 3.05,
        'Aw': np.round(np.pi * 3.05**2 / 4, 2),  # 7.31 mm²
        'Ve': 55.8,
        'AL': 1200,
        'Ploss': 520
    },
    {
        'id': 'ZT41605TC',
        'Bmax': 0.5,
        'Ae': 15.6,
        # B: diámetro interior nominal sin recubrimiento.
        'B': 9.07,
        'Aw': np.round(np.pi * 9.07**2 / 4, 2),  # 64.61 mm²
        'Ve': 580,
        'AL': 1580,
        'Ploss': 715
    },
    {
        'id': 'ZT42206TC',
        'Bmax': 0.5,
        'Ae': 25.8,
        # B: diámetro interior nominal sin recubrimiento.
        'B': 13.7,
        'Aw': np.round(np.pi * 13.7**2 / 4, 2),  # 147.41 mm²
        'Ve': 1395,
        'AL': 1790,
        'Ploss': 640
    },
    {
        'id': 'ZT43813TC',
        'Bmax': 0.5,
        'Ae': 114.2,
        # B: diámetro interior nominal sin recubrimiento.
        'B': 19.0,
        'Aw': np.round(np.pi * 19.0**2 / 4, 2),  # 283.53 mm²
        'Ve': 9462,
        'AL': 5190,
        'Ploss': 715
    },
    {
        'id': 'ZT44015TC',
        'Bmax': 0.5,
        'Ae': 138,
        # B: diámetro interior nominal sin recubrimiento.
        'B': 26.2,
        'Aw': np.round(np.pi * 26.2**2 / 4, 2),  # 539.13 mm²
        'Ve': 14205,
        'AL': 5040,
        'Ploss': 610
    },
    {
        'id': 'ZT43825TC',
        'Bmax': 0.5,
        'Ae': 231,
        # B: diámetro interior nominal sin recubrimiento.
        'B': 19.0,
        'Aw': np.round(np.pi * 19.0**2 / 4, 2),  # 283.53 mm²
        'Ve': 19152,
        'AL': 10500,
        'Ploss': 550
    },
    {
        'id': 'ZT47313TC',
        'Bmax': 0.5,
        'Ae': 210,
        # B: diámetro interior nominal sin recubrimiento.
        'B': 38.9,
        'Aw': np.round(np.pi * 38.9**2 / 4, 2),  # 1188.47 mm²
        'Ve': 34771,
        'AL': 4790,
        'Ploss': 880
    },
    {
        'id': 'NT42819UG',
        'Bmax': 0.5,
        'Ae': 89.1,
        # Aw = D * (E - F) / 2, por mitad y lado.
        'D': 6.2,
        'E': 21.2,
        'F': 10.9,
        'Aw': np.round(6.2 * (21.2 - 10.9) / 2, 2),  # 31.93 mm²
        'Ve': 4310,
        'AL': 5500,
        'Ploss': 590
    },
    {
        'id': 'NT42316UG',
        'Bmax': 0.5,
        'Ae': 55.4,
        # Aw = D * (E - F) / 2, por mitad y lado.
        'D': 5.5,
        'E': 17.0,
        'F': 8.55,
        'Aw': np.round(5.5 * (17.0 - 8.55) / 2, 2),  # 23.24 mm²
        'Ve': 2440,
        'AL': 4100,
        'Ploss': 590
    },
    {
        'id': 'NT41812UG',
        'Bmax': 0.5,
        'Ae': 31.2,
        # Aw = D * (E - F) / 2, por mitad y lado.
        'D': 4.0,
        'E': 12.4,
        'F': 6.4,
        'Aw': np.round(4.0 * (12.4 - 6.4) / 2, 2),  # 12.0 mm²
        'Ve': 1040,
        'AL': 2830,
        # Densidad publicada; 0.7 W/set / 1040 mm³ implica 673.076923.
        # Se conserva 642 conforme a la prioridad de densidad directa.
        'Ploss': 642
    },
    {
        'id': 'ZT41003TC',
        'Bmax': 0.5,
        'Ae': 7.3,
        # B: diámetro interior nominal sin recubrimiento.
        'B': 4.75,
        'Aw': np.round(np.pi * 4.75**2 / 4, 2),  # 17.72 mm²
        'Ve': 151,
        'AL': 1330,
        'Ploss': 715
    },
    {
        'id': '0T40601TC',
        'Bmax': 0.5,
        'Ae': 2,
        # B: diámetro interior nominal sin recubrimiento.
        'B': 3.05,
        'Aw': np.round(np.pi * 3.05**2 / 4, 2),  # 7.31 mm²
        'Ve': 26.7,
        'AL': 592,
        'Ploss': 500
    },
]


with open("database_cores.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)
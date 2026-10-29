"""Verifica data sin modificarla. Auditoría de los PDFs aportados el 09-10-2026.
Aw respeta las fórmulas solicitadas por mitad; consultar las reservas del informe.
"""
import numpy as np

REFERENCIA = [{'id': '0T42019EC', 'Bmax': 0.5, 'Ae': 29, 'Aw': 25.02, 'Ve': 1460, 'AL': 1540, 'Ploss': 590}, {'id': '0T44444EC', 'Bmax': 0.5, 'Ae': 172, 'Aw': 139.27, 'Ve': 17800, 'AL': 4640, 'Ploss': 630}, {'id': '0T43939EC', 'Bmax': 0.5, 'Ae': 123, 'Aw': 117.15, 'Ve': 11500, 'AL': 3650, 'Ploss': 500}, {'id': '0T-44949-EC', 'Bmax': 0.5, 'Ae': 209, 'Aw': 171.69, 'Ve': 24000, 'AL': 5140, 'Ploss': 630}, {'id': '0T42523EC', 'Bmax': 0.5, 'Ae': 55, 'Aw': 33.03, 'Ve': 3300, 'AL': 2660, 'Ploss': 590}, {'id': '0T42625UG', 'Bmax': 0.5, 'Ae': 108, 'Aw': 42.26, 'Ve': 6530, 'AL': 6010, 'Ploss': 590}, {'id': '0T42620UG', 'Bmax': 0.5, 'Ae': 109, 'Aw': 30.19, 'Ve': 5470, 'AL': 7020, 'Ploss': 590}, {'id': '0T42016UG', 'Bmax': 0.5, 'Ae': 59.1, 'Aw': 23.69, 'Ve': 2330, 'AL': 4080, 'Ploss': 590}, {'id': '0T45050UG', 'Bmax': 0.5, 'Ae': 314, 'Aw': 216.6, 'Ve': 37100, 'AL': 9200, 'Ploss': 630}, {'id': '0T43230UG', 'Bmax': 0.5, 'Ae': 142, 'Aw': 74.55, 'Ve': 12500, 'AL': 6570, 'Ploss': 630}, {'id': '0T44040UG', 'Bmax': 0.5, 'Ae': 175, 'Aw': 162.99, 'Ve': 20500, 'AL': 6100, 'Ploss': 629.2682926829268}, {'id': '0T41506TC', 'Bmax': 0.5, 'Ae': 11.2, 'Aw': 42.66, 'Ve': 343, 'AL': 1320, 'Ploss': 500}, {'id': '0T-40603-TC', 'Bmax': 0.5, 'Ae': 4.28, 'Aw': 7.31, 'Ve': 55.8, 'AL': 1200, 'Ploss': 520}, {'id': 'ZT41605TC', 'Bmax': 0.5, 'Ae': 15.6, 'Aw': 64.61, 'Ve': 580, 'AL': 1580, 'Ploss': 715}, {'id': 'ZT42206TC', 'Bmax': 0.5, 'Ae': 25.8, 'Aw': 147.41, 'Ve': 1395, 'AL': 1790, 'Ploss': 640}, {'id': 'ZT43813TC', 'Bmax': 0.5, 'Ae': 114.2, 'Aw': 283.53, 'Ve': 9462, 'AL': 5190, 'Ploss': 715}, {'id': 'ZT44015TC', 'Bmax': 0.5, 'Ae': 138, 'Aw': 539.13, 'Ve': 14205, 'AL': 5040, 'Ploss': 610}, {'id': 'ZT43825TC', 'Bmax': 0.5, 'Ae': 231, 'Aw': 283.53, 'Ve': 19152, 'AL': 10500, 'Ploss': 550}, {'id': 'ZT47313TC', 'Bmax': 0.5, 'Ae': 210, 'Aw': 1188.47, 'Ve': 34771, 'AL': 4790, 'Ploss': 880}, {'id': 'NT42819UG', 'Bmax': 0.5, 'Ae': 89.1, 'Aw': 31.93, 'Ve': 4310, 'AL': 5500, 'Ploss': 590}, {'id': 'NT42316UG', 'Bmax': 0.5, 'Ae': 55.4, 'Aw': 23.24, 'Ve': 2440, 'AL': 4100, 'Ploss': 590}, {'id': 'NT41812UG', 'Bmax': 0.5, 'Ae': 31.2, 'Aw': 12.0, 'Ve': 1040, 'AL': 2830, 'Ploss': 642}, {'id': 'ZT41003TC', 'Bmax': 0.5, 'Ae': 7.3, 'Aw': 17.72, 'Ve': 151, 'AL': 1330, 'Ploss': 715}, {'id': '0T40601TC', 'Bmax': 0.5, 'Ae': 2, 'Aw': 7.31, 'Ve': 26.7, 'AL': 592, 'Ploss': 500}]

RESERVAS = {
    ('0T42523EC', 'Aw'): '33.03 usa D_min=9.05 y M_nom=3.65; Aw nominal no documentado.',
    ('NT41812UG', 'Ploss'): '642 publicado; 0.7 W/set y Ve=1040 implican 673.076923. Mantener 642 según regla.'
}

def verificar_data(data):
    campos = {'id', 'Bmax', 'Ae', 'Aw', 'Ve', 'AL', 'Ploss'}
    diferencias = []
    indices = {}
    for i, nucleo in enumerate(data):
        if set(nucleo) != campos:
            diferencias.append((i, 'estructura', set(nucleo), campos))
        identificador = nucleo.get('id')
        if identificador in indices:
            diferencias.append((identificador, 'id', 'duplicado', 'único'))
        indices[identificador] = nucleo
    for esperado in REFERENCIA:
        identificador = esperado['id']
        actual = indices.get(identificador)
        if actual is None:
            diferencias.append((identificador, 'id', 'ausente', identificador))
            continue
        for campo, valor in esperado.items():
            recibido = actual.get(campo)
            if campo == 'id':
                coincide = recibido == valor
            else:
                try:
                    coincide = bool(np.isclose(recibido, valor, rtol=0, atol=1e-9))
                except (TypeError, ValueError):
                    coincide = False
            if not coincide:
                diferencias.append((identificador, campo, recibido, valor))
    esperados = {n['id'] for n in REFERENCIA}
    for identificador in indices.keys() - esperados:
        diferencias.append((identificador, 'id', identificador, 'no incluido en las 24 fuentes'))
    return diferencias, dict(RESERVAS)

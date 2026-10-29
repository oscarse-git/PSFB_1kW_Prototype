import json
import os
import pandas as pd

from trasformer_functions import *

def get_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_full_transformer(param, transformer):
    results = {}

    results['id'] = transformer['id']
    results['type'] = transformer['type_id']

    results['IpNom'], results['IsNom'] = current_windings(param["P"], param["VoutDC"], param["ratio"])

    results['n1'], results['n2'] = windings(param["VinDC"], param["ratio"], 0.5/param['fs'], 
                                            transformer['Bmax'], transformer['Ae'] * 1e-6)
    
    results['newRatio'] = np.round(results['n2']/results['n1'], 4)

    results['V2max'] = np.round(param['VinDC'] * results['newRatio'], 2)

    results['V1nom'] = np.round((param['VoutDC'] + 2 * param['Vf']) / results['newRatio'], 2)

    results['Aw'] = winding_surface(param['secP'], param['secS'], 
                                    results['n1'], results['n2'], param['fillFactor'])

    results['Bmax'] = calculate_induction(param['VinDC'], 0.5/param['fs'], 
                                          results['n1'], transformer['Ae'] * 1e-6)
    
    results['Bnom'] = calculate_induction(results['V1nom'], 0.5/param['fs'], 
                                          results['n1'], transformer['Ae'] * 1e-6)

    # results['Rp'], results['Rs'] = calculate_resistance(transformer, param['secP'], param['secS'],
    #                                                     results['n1'], results['n2'])

    for loss_dict in transformer['core_loss_specification']:
        tempMeas = loss_dict['temperature_C']
        fMeas = loss_dict['frequency_Hz']
        BmaxMeas = loss_dict['flux_density_mT'] * 1e-3
        lossDensity = loss_dict['maximum_density_mW_per_cm3'] * 1e3
        volume = transformer['Ve'] * 1e-9
        
        temp = core_loss_estimation(volume, lossDensity, fMeas, BmaxMeas,
                                    param['fs'], results['Bnom'])

        results[f'P_loss {tempMeas}C lower'] = temp[0]
        results[f'P_loss {tempMeas}C upper'] = temp[1]
    
    results['Lp'], results['Ls'] = calculate_inductance(transformer['AL'] * 1e-9, 
                                                        results['n1'], results['n2'])
    
    return results

def sweep_all_database(param, path):
    database = get_data(path)

    results = []
    for transformer in database:
        os.system('cls' if os.name == 'nt' else 'clear')
        result = calculate_full_transformer(param, transformer)
        print_result(result, param, transformer)

        if check_result(result, param, transformer): results.append(result)

    df = pd.DataFrame(results)
    df.to_excel("Transformers.xlsx", index=False)

def calculate_specific_transformer(name, param, path):
    os.system('cls' if os.name == 'nt' else 'clear')

    database = get_data(path)
    for element in database:
        if element['id'] == name: transformer = element

    result = calculate_full_transformer(param, transformer)
    print_result(result, param, transformer)
        
def check_result(result, param, transformer):
    flag = True
    
    if result['Aw'] < correct_transformer_Aw(transformer): flag = False
    elif result['Bmax'] >= transformer['Bmax']: flag = False

    return flag

def print_result(result, param, transformer):
    print()
    print(transformer['id'])
    print()
    print(f"I1max = {result['IpNom']} A")
    print(f"I2max = {result['IsNom']} A")
    print()
    print(f'n1 = {result['n1']}')
    print(f'n2 = {result['n2']}')
    print(f'Real Ratio = {result['newRatio']}')
    print()
    print(f'MAX: VinDC = {param['VinDC']} V ===> VoutDC = {np.round(param['VinDC']*result['newRatio'] - 2 * param['Vf'], 2)} V')
    print(f'NOM: VinDC = {result['V1nom']} V ===> VoutDC = {param['VoutDC']} V')
    print()
    print(f"Bmax = {result['Bmax']} T")
    print(f"Bnom = {result['Bnom']} T")
    print()
    print(f"Diameter Primary = {diameter(param['secP'])} mm")
    print(f"Diameter Secondary = {diameter(param['secS'])} mm")
    print(f"Aw_real = {result['Aw']} mm2")
    print(f"Aw_available = {transformer['Aw']*2} mm2")
    print()
    
    print()
    
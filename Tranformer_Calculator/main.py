from trasformer_functions import *
from main_funtions import *

        
if __name__ == '__main__':

    path = r"database_cores.json"
    selectedTransformer = "0T42016UG"

    param = { # general parameters for all transformers
        "VinDC" : 400.0,
        "P" : 1000.0,
        "fs" : 400e3,

        "V2max" : 100.0,
        "VoutDC" : 84.0,

        "ratio" : 0.25,
        "secP" : 0.5,       
        "secS" : 1.5,
        "fillFactor" : 0.4,

        "Vf" : 2
    }

    transformer = {
        "id": "B65875A0000R049",
        "type_id": "PQ",
        "material": "N49",

        "Ae": 62.9,       # mm²
        "Amin": 54.4,     # mm²
        "Ve": 2850,      # mm³
        "le": 45.2,      # mm
        "AL": 2000,      # nH/turn²
        "Bmax": .4,     # T - No especificado
        "Aw": np.round(14 * (18-8.8)/2,4),       # mm² - No especificado

        "core_loss_specification": [
            {
                "temperature_C": 100,
                "frequency_Hz": 500e3,
                "flux_density_mT": 50,
                "maximum_density_mW_per_cm3": 315.79
            }
        ]
    }

    result = calculate_full_transformer(param, transformer, calculate_loss=True)

    print_result(result, param, transformer)
    df = pd.DataFrame([result])
    df.to_excel("Selected_Transformer.xlsx", index=False)




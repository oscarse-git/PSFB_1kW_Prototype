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
        "secP" : 1.5,       
        "secS" : 2.5,
        "fillFactor" : 0.4,

        "Vf" : 2
    }


    sweep_all_database(param, path)
    calculate_specific_transformer(selectedTransformer, param, path)



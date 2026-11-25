import pandas as pd

from excel_manipulation_functions import *


if __name__ == "__main__":

    fileBence = "BOM_Bence.xlsx"
    fileOscar = "BOM_Oscar.xlsx"

    bomBence = pd.read_excel(fileBence, sheet_name="BOM")
    bomOscar = pd.read_excel(fileOscar, sheet_name="BOM")

    bomBence["Shop"] = get_urls(fileBence, bomBence)

    print(bomBence['Shop'])
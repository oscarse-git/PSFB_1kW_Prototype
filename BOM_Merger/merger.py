import pandas as pd
from excel_manipulation_functions import *
from merger_functions import *

if __name__ == "__main__":

    fileBence = "BOM_Bence.xlsx"
    fileOscar = "BOM_Oscar.xlsx"

    bomOscar = pd.read_excel(fileOscar, sheet_name="BOM")
    bomBence = pd.read_excel(fileBence, sheet_name='BOM')

    board_bom = pd.read_excel(
        fileBence,
        sheet_name='Board BOM',
        header=4
    )

    footprint_map = (
        board_bom
        .dropna(subset=['Order list group', 'PCB footprint'])
        .drop_duplicates(subset='Order list group')
        .set_index('Order list group')['PCB footprint']
    )

    bomBence['Footprint'] = bomBence['Part / specification'].map(footprint_map)

    bomBence["Shop"] = get_urls(fileBence, bomBence)

    colsTemDF = ['Specification', 'manufacturer id','value', 'case code', 
                 'dielectric', 'Voltage Rating','tolerance', 
                 'Price/unit', 'Buy qty', 'Total Cost', 'Shop URL']

    temDFoscar = pd.DataFrame(columns=colsTemDF)
    temDFbence = pd.DataFrame(columns=colsTemDF)

    tempDFoscar = extract_data_Oscar(bomOscar, temDFoscar)
    tempDFbence = extract_data_Bence(bomBence, temDFbence)

    # tempDFoscar.to_excel('test_oscar.xlsx')
    # tempDFbence.to_excel('test_bence.xlsx')

    mergedBOM, errorDict = merge_boms(tempDFbence, tempDFoscar)

    export_merged_bom(mergedBOM, errorDict, "Merged_BOM.xlsx")



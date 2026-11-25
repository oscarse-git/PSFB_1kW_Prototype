import pandas as pd

dtypes = {
    "Footprint": str,
    "Designation": str,
    "Quantity": float
}

bom = pd.read_excel("BOM.xlsx", sheet_name="BOM", dtype=dtypes)
pcbComp = pd.read_csv("PSFB.csv", sep=";", index_col=False, dtype=dtypes)


common_columns = bom.columns.intersection(pcbComp.columns)

bom = bom[common_columns]
pcbComp = pcbComp[common_columns]

exclude = pcbComp.loc[
    pcbComp["Footprint"].str.contains("PinHeader|TestPoint", na=False),
    "Designation"
].tolist()
exclude.extend(["MAIN TRANSFORMER", "HVDC_POWER_IN", "VOUT_CHARGER",
    "Power_Terminal_12V", "L"])



matches = pd.MultiIndex.from_frame(pcbComp).isin(
    pd.MultiIndex.from_frame(bom))

print(pcbComp[
    (~matches) &
    (~pcbComp["Designation"].isin(exclude))
])

matches = pd.MultiIndex.from_frame(bom).isin(
    pd.MultiIndex.from_frame(pcbComp))


print()
print(bom[~matches])
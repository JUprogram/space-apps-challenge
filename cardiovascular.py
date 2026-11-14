import pandas as pd

data = pd.read_csv("BRSMCF_CFT70_2D_Echo_All.csv")

print("First five rows:\n")
print(data.head())

print("COLUMN NAMES: \n")
print(data.columns.tolist())

print("DATSET INFO: \n")
print(data.info())

print("STATISTICAL SUMMARY: \n")
print(data.describe(include="all"))


print("\n--- DATASET SIZE ---")
print(data.shape)

# 4. Check column types and missing values
print("\n--- DATASET INFORMATION ---")
data.info()

print("\n--- MISSING VALUES ---")
print(data.isnull().sum())    


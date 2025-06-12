import pandas as pd
import numpy as np

df = pd.read_csv('simulation_results.csv')
arr = df['average_survival_rate'][0]
arr = arr.lstrip('[').rstrip(']')
arr = np.fromstring(arr, sep=',')
print(arr)
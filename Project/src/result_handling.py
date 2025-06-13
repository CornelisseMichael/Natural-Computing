import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def normalize_to_percentages(arr):
    max_val = arr.max()
    return (arr / max_val) * 100

def string_to_array(s):
    return np.fromstring(s.lstrip('[').rstrip(']'), sep=',')


df = pd.read_csv('./csv-outputs/offices_1_results.csv')
print(df.head())
df['average_survival_rate'] = df['average_survival_rate'].apply(string_to_array)
df['average_survival_rate'] = df['average_survival_rate'].apply(normalize_to_percentages)
grouped = df.groupby('evacuee_density')
grouped_arrays = {evacuee_density: group['average_survival_rate'].tolist() for evacuee_density, group in grouped}
print(grouped_arrays)

labels = np.flip(np.unique(df['scenario'].values))
print(labels)

for key, value in grouped_arrays.items():
    for a in value:
        plt.plot(a)
    # plt.title(key)
    plt.ylabel("Percentage")
    plt.xlabel("Time")
    # plt.legend(labels)
    plt.show()


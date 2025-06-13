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


# survival_rates = df['average_survival_rate'].values
# labels = df['evacuee_density'].values
# survival_rates = [np.fromstring(sr.lstrip('[').rstrip(']'), sep=',') for sr in survival_rates]
# # survival_rates = np.asarray(survival_rates)
# print(survival_rates)
#
#
#
# for i, sr in enumerate(survival_rates):
#     # np.fromstring(sr.lstrip('[').rstrip(']'), sep=',')
#     survival_rates[i] = normalize_to_percentages(sr)
#
# for i, sr in enumerate(survival_rates):
#     # if i < 3:
#     #     c = 'blue'
#     # elif i < 6:
#     #     c = 'red'
#     # elif i < 9:
#     #     c = 'green'
#     # else:
#     #     c = 'orange'
#     plt.plot(sr)
#     plt.legend(labels)
#
# plt.show()


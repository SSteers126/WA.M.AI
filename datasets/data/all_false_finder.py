import pandas as pd

# Prints every frame that 1 or more consecutive frames of no zones having any notes is observed.
# Use to check for any errors with unlabelled frames

df = pd.read_csv("FiNALE set 1/TODO_dear-doppelganger-advanced-12-played/8_zone_presence_labels.csv")

all_false = False

for count, row in enumerate(df.itertuples()):
    if not any(row[2:]):
        if not all_false:
            all_false = True
            print(row[0])
    else:
        all_false = False

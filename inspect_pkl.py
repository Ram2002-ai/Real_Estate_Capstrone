import pickle as pkl
import pandas as pd

try:
    with open("files/pkl.files/df.pkl", 'rb') as f:
        df = pkl.load(f)
    print("Columns:", df.columns.tolist())
    print("Head:", df.head(1).to_dict())
except Exception as e:
    print(f"Error: {e}")

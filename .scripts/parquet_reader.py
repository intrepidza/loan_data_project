import pandas as pd
from pathlib import Path

file_path = Path(__file__).parent.parent.joinpath('loan_data.parquet')

df = pd.read_parquet(str(file_path))

print(df)

import os
import pandas as pd

path = "./temp/20241010-050032_plans/"
for filename in os.listdir(path):
  dataframes = pd.read_html(os.path.join(path, filename))

for df in dataframes:
  print(df.to_string(index=False))

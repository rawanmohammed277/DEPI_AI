import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
from datetime import datetime

df= pd.read_excel(r'ecommerce_orders.xlsx')
print(df)

df.shape
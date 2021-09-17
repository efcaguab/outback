# %%
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
# %%
con = sqlite3.connect("outback.db")
df = pd.read_sql_query("SELECT * from Listing", con)
con.close()

# %%
# Price vs year
plt.scatter(df['year'], np.log(df['price']), c = df['kilometers'])
# Price vs kilometers
plt.scatter(df['kilometers'], np.log(df['price']), c = df['year'])

# %%
df = df.dropna()
df['price_total'] = np.where(df['on_road_costs'] == 1, df['price'], df['price'] + 300) 
X = df[['year', 'kilometers']]
y = np.log(df['price_total'])
regr = linear_model.LinearRegression()
regr.fit(X, y)
df['predicted_price'] = np.exp(regr.predict(X))
df['discount'] = (df['predicted_price'] - df['price_total'])/df['predicted_price'] * 100

# %%
df.boxplot('discount', 'city', figsize=(10,30), vert = False)
df.boxplot('discount', 'price_type', figsize=(10,30), vert = False)
# %%
df['discount' > 0]
# %%
deals = df[(df['discount'] > 0) & (df['price_total'] < 18500) & (df['kilometers'] < 200000) & (df['kilometers'] > 20000)]
deals.sort_values('discount')
# %%
deals.to_csv("deals.csv")
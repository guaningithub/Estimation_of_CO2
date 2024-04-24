import math
import sqlalchemy
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from deepforest import CascadeForestRegressor
from sklearn.metrics import mean_squared_error
import pyodbc
import pandas as pd
import time

# 获取开始时间
start_time = time.time()
print("start_time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 连接到 SQL Server 数据库
connection_string = "Driver={SQL Server};Server=DESKTOP-ELNVR1U;Database=OCO_2_L2_2014_2022;Integrated Security=true"
conn = pyodbc.connect(connection_string)

query = "SELECT * FROM MATCHINGDATA_05570140 ORDER BY YearMonth,lat,lon"
# query1 = "SELECT * FROM MATCHINGDATA_005 ORDER BY YearMonth,lat,lon"
query1 = "SELECT * FROM MergeData_05570140  WHERE YearMonth>=202201 and YearMonth<=202212 ORDER BY YearMonth,lat,lon"

# 从数据库中读取数据到 DataFrame
df = pd.read_sql(query, conn)
predict_Data = pd.read_sql(query1, conn)
predict_Data = predict_Data.astype('float64')


x_train = df[
    ['YearMonth', 'lat', 'lon', 'NightLight', 'windu', 'windv', 'pres', 'temp', 'blh','relh']]
y_train = df['AvgXCO2']

x_predict = predict_Data[
    ['YearMonth', 'lat', 'lon', 'NightLight', 'windu', 'windv', 'pres', 'temp', 'blh','relh']]


model = CascadeForestRegressor(partial_mode='true',
                               n_estimators=5,
                               n_jobs=-1,  ##-1 所有线程  n个线程
                               )

model.fit(x_train, y_train)
y_predict = model.predict(x_predict)

# print("\nTesting RMSE: {:.3f}".format(rmse))
np.savetxt('data/202201_202212_XCO2.txt', y_predict)


model.clean()
# loaded_model = CascadeForestRegressor.load('predictData_XCO2')

# 关闭数据库连接
conn.close()


# 获取结束时间
end_time = time.time()
print("end_time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 计算程序运行时间
duration = end_time - start_time

# 将秒转换为小时、分钟和秒
hours = duration // 3600
minutes = (duration % 3600) // 60
seconds = duration % 60

print(f'Duration: {hours:.0f} hours, {minutes:.0f} minutes, {seconds:.2f} seconds')

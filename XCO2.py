from deepforest import CascadeForestRegressor
from skopt import BayesSearchCV
from sklearn.model_selection import KFold, train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from scipy.stats import pearsonr
from datetime import datetime
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import time
from matplotlib import rcParams

# 获取开始时间
start_time = time.time()
print("start_time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

query = "SELECT * FROM MATCHINGDATA_005 WHERE YearMonth>=201501 and YearMonth<=201612 ORDER BY YearMonth,lat,lon"
query1 = "SELECT * FROM MergeData WHERE YearMonth>=201501 and YearMonth<=201612 ORDER BY YearMonth,lat,lon"

# 从数据库中读取数据到 DataFrame
df = pd.read_sql(query, conn)
predict_Data = pd.read_sql(query1, conn)
predict_Data = predict_Data.astype('float64')

# 提取特征和目标
x_train = df[['YearMonth', 'lat', 'lon', 'NightLight', 'windu', 'windv', 'pres', 'temp', 'blh', 'relh']]
y_train = df['AvgXCO2']

x_predict = predict_Data[['YearMonth', 'lat', 'lon', 'NightLight', 'windu', 'windv', 'pres', 'temp', 'blh', 'relh']]

# 数据归一化
scaler = MinMaxScaler()
x_train_scaled = scaler.fit_transform(x_train)
x_predict_scaled = scaler.transform(x_predict)

# 分割数据集用于贝叶斯优化
x_train, x_val, y_train, y_val = train_test_split(x_train_scaled, y_train, test_size=0.2, random_state=42)

# 贝叶斯优化的参数搜索空间
param_space = {
    'n_bins': (50, 255),  # bin 的数量
    'bin_subsample': (10000, 300000),  # 进行分箱操作的样本数
    'n_estimators': (2, 10),  # 每层估计器数量
    'n_trees': (50, 200),  # 每个估计器的树的数量
    'min_samples_split': (2, 20),  # 每个节点最小样本数
    'min_samples_leaf': (1, 20),  # 每个叶子节点最小样本数
}

# 初始化CascadeForestRegressor
cfr = CascadeForestRegressor(random_state=42)

# 初始化贝叶斯搜索
bayes_search = BayesSearchCV(
    estimator=cfr,
    search_spaces=param_space,
    n_iter=16,  # 设置迭代次数
    cv=5,  # 交叉验证折数
    n_jobs=-1,  # 并行作业数量
    scoring='neg_mean_squared_error',
    random_state=42
)

# 进行贝叶斯优化参数搜索
bayes_search.fit(x_train, y_train)
best_params = bayes_search.best_params_
print("Best parameters found: ", best_params)
print("time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 使用最佳参数进行十倍交叉验证
kf = KFold(n_splits=10, shuffle=True, random_state=42)
y_true_all = []
y_pred_all = []

for train_index, test_index in kf.split(x_train_scaled):
    x_train_fold, x_test_fold = x_train_scaled[train_index], x_train_scaled[test_index]
    y_train_fold, y_test_fold = y_train[train_index], y_train[test_index]

    # 使用最佳参数初始化CascadeForestRegressor
    best_cfr = CascadeForestRegressor(**best_params, random_state=42, n_jobs=-1)

    # 训练模型
    best_cfr.fit(x_train_fold, y_train_fold)

    # 预测
    y_pred_fold = best_cfr.predict(x_test_fold)

    # 将 y_pred_fold 转换为一维数组
    y_pred_fold_flattened = np.round(y_pred_fold.flatten(), 2)

    # 存储实际值和预测值
    y_true_all.extend(y_test_fold)
    y_pred_all.extend(y_pred_fold_flattened)

# 转换为 numpy 数组并确保数据类型一致
y_true_all = np.array(y_true_all, dtype=np.float64)
y_pred_all = np.array(y_pred_all, dtype=np.float64)

data_save = pd.DataFrame({
    'y_true': y_true_all,
    'y_pred': y_pred_all,
})

data_save.to_csv('CFR_10fold_true_pred.csv', index=False)

# 计算评估指标
MSE = mean_squared_error(y_true_all, y_pred_all)
RMSE = np.sqrt(MSE)
R, _ = pearsonr(y_true_all, y_pred_all)
R2_sklearn = r2_score(y_true_all, y_pred_all)
MAE = mean_absolute_error(y_true_all, y_pred_all)

print("R2_sklearn:", R2_sklearn)
print("R:", R)
print("MAE:", MAE)

# 初始化Deep Forest模型
model = CascadeForestRegressor(**best_params,
                               partial_mode='true',
                               # n_estimators=5,
                               n_jobs=-1  # -1 使用所有线程
                               )

# 训练模型
model.fit(x_train_scaled, y_train)

# 进行预测
y_predict = model.predict(x_predict_scaled)

# 保存预测结果
np.savetxt('data/201501_202212_XCO2.txt', y_predict)

# 清理模型
model.clean()
# 关闭数据库连接
conn.close()

# 获取结束时间
end_time = time.time()
print("end_time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 计算程序运行时间
duration = end_time - start_time
hours = duration // 3600
minutes = (duration % 3600) // 60
seconds = duration % 60

print(f'Duration: {hours:.0f} hours, {minutes:.0f} minutes, {seconds:.2f} seconds')

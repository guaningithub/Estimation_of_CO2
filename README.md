# Estimation_of_CO2
- 从文章提供的OCO-2卫星数据和辅助数据链接中下载数据集；
 所有数据重采样为统一分辨率:0.05°，重采样代码为项目中的”resample.py”
- 为了便于数据数据操作，使用”tiff_to_sql.py”将数据存储至SQL Server数据库中;使用matching.sql对CO2数据和辅助数据进行时空匹配；
- 对匹配后的数据使用”XCO2.py”进行训练和估算数据；
- 最后，对估算后的数据进行验证的评价指标R、RMSE、MAE等直接调用python库就可以，这里不再赘述。
-----------------------------------------------
- Download the dataset from the provided links for OCO-2 satellite data and auxiliary data mentioned in the article.
- Resample all data to a uniform spatial resolution of 0.05° using the "resample.py" script included in the project.
- For ease of data manipulation, utilize the "tiff_to_sql.py" script to store the data in a SQL Server database.
- Employ the "matching.sql" script to perform spatiotemporal matching between the CO2 and auxiliary data.
- Utilize the "XCO2.py" script to train and estimate the CO2 concentrations based on the matched data.
- Finally,  assess the accuracy of the estimated data using standard evaluation metrics such as the correlation coefficient (R), root mean square error (RMSE), mean absolute error (MAE), etc. These metrics can be calculated using appropriate Python libraries, although specific details are not provided here.

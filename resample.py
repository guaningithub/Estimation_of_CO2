# -*- coding: UTF-8 -*-

import os
from osgeo import gdal
import numpy as np

# 定义输入目录和输出目录
input_dir = r'G:\05570140\t2m'
# output_dir = r'C:\Users\user\Desktop\CO2_14_22\tif\predict\2.5\2015'
output_dir = r'G:\05570140\005\t2m'
# 定义目标分辨率（重采样后的分辨率）
target_resolution = 0.05

# 遍历输入目录下的所有 TIFF 文件
for filename in os.listdir(input_dir):
    if filename.endswith('.tif') or filename.endswith('.tiff'):
        input_file = os.path.join(input_dir, filename)
        output_file = os.path.join(output_dir, filename)

        # 打开输入文件
        dataset = gdal.Open(input_file, gdal.GA_ReadOnly)

        # 获取输入文件的投影信息和地理转换参数
        projection = dataset.GetProjection()
        geotransform = dataset.GetGeoTransform()

        # 获取输入文件的原始分辨率
        original_resolution = geotransform[1]

        # 计算目标地理转换参数
        x_size = int(dataset.RasterXSize * original_resolution / target_resolution)
        y_size = int(dataset.RasterYSize * original_resolution / target_resolution)
        new_geotransform = (
            geotransform[0], target_resolution, geotransform[2], geotransform[3], geotransform[4], -target_resolution)

        # 创建输出文件
        driver = gdal.GetDriverByName('GTiff')
        output_dataset = driver.Create(output_file, x_size, y_size, dataset.RasterCount,
                                       dataset.GetRasterBand(1).DataType)

        # 设置投影信息和地理转换参数
        output_dataset.SetProjection(projection)
        output_dataset.SetGeoTransform(new_geotransform)

        # 设置 NoData 值
        output_dataset.GetRasterBand(1).SetNoDataValue(np.nan)

        # 执行重采样，并设置 NoData 值
        gdal.ReprojectImage(dataset, output_dataset, None, None, gdal.GRA_Bilinear, options=['NUM_THREADS=ALL_CPUS'])

        # 关闭数据集
        dataset = None
        output_dataset = None

        print(f"重采样完成: {input_file} -> {output_file}")
print("The end")

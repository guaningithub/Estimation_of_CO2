
import os
import glob
from datetime import datetime
import pyodbc
import rasterio
import numpy as np
import time

# 获取开始时间
start_time = time.time()
print("start_time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 连接到 SQL Server 数据库
connection_string = "Driver={SQL Server};Server=DESKTOP-ELNVR1U;Database=OCO_2_L2_2014_2022;Integrated Security=true"

try:
    # 建立数据库连接
    conn = pyodbc.connect(connection_string)

    # 创建游标
    cursor = conn.cursor()

    # 开始事务
    conn.autocommit = False

    # 创建数据库表（如果需要）
    create_table_query = '''
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='CO2_05570140_0_05')
        CREATE TABLE CO2_05570140_0_05 (
            time VARCHAR(10),
            lat FLOAT,
            lon FLOAT,
            XCO2 FLOAT
        )
    '''
    cursor.execute(create_table_query)

    # 输入文件夹路径
    folder_path = r'G:\05570140\CO2\tif'

    # 获取文件夹下所有 TIFF 图片的路径
    tiff_files = glob.glob(os.path.join(folder_path, '*.tif'))

    # 逐个读取 TIFF 图片的像素值和对应的经纬度，并插入数据库表中
    for tiff_file in tiff_files:
        try:
            # 获取文件名
            file_name = os.path.basename(tiff_file)

            # # # 去除文件名后缀
            file_name_without_ext = os.path.splitext(file_name)[0]

            #去除文件名后缀
            file_name_without_ext = os.path.splitext(file_name)[0]
            need_time = '20' + file_name_without_ext[11:17]
            print('开始读取' + need_time + '数据...')

            # 读取 TIFF 图片
            with rasterio.open(tiff_file) as src:
                # 获取经纬度
                lons, lats = np.meshgrid(src.bounds.left + np.arange(src.width) * src.res[0],
                                         src.bounds.top - np.arange(src.height) * src.res[1])

                # 保留两位小数（四舍五入）并将经纬度转换为浮点数
                lons = np.round(lons, 2).astype(float)
                lats = np.round(lats, 2).astype(float)

                # 读取像素值
                data = src.read(1)

                # 将经纬度和像素值扁平化为一维数组
                lons_flat = lons.flatten()
                lats_flat = lats.flatten()
                data_flat = data.flatten()

            # 生成对应的经度、纬度和数据的列表
            rows = []
            for lon, lat, value in zip(lons_flat, lats_flat, data_flat):
                # 跳过无效值为 NaN 或 NoData 的情况
                if np.isnan(value) or value == src.nodata:
                    continue

                # 处理有效数据
                rows.append((str(need_time), lat, lon, float(value)))

            # 插入数据到数据库表
            if rows:
                insert_query = 'INSERT INTO CO2_05570140_0_05 (time, lat, lon, XCO2) VALUES (?, ?, ?, ?)'
                cursor.executemany(insert_query, rows)
                print(need_time + '数据插入完成')
            else:
                print(need_time + '没有有效数据插入')

        except Exception as e:
            print(f"Error processing file {tiff_file}: {str(e)}")
            # 回滚事务
            conn.rollback()
            continue

            print(need_time + '数据插入完成')

        except Exception as e:
            print(f"Error processing file {tiff_file}: {str(e)}")
            # 回滚事务
            conn.rollback()
            continue

        print(need_time + '数据插入完成')
    # 提交事务
    conn.commit()

    print("Data insertion completed.")

except Exception as e:
    print("Error connecting to the database:", str(e))

finally:
    # 关闭游标和数据库连接
    if cursor:
        cursor.close()
    if conn:
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

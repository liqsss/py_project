import pandas as pd

# 创建 DataFrame
data = {
            'Open': [100, 102, 105],
                'High': [110, 108, 112],
                    'Low': [95, 98, 103]
                    }
df = pd.DataFrame(data, index=['2023-01-01', '2023-01-02', '2023-01-03'])

# iloc：按位置选择
print("iloc 示例:")
print(df.iloc[0, 1])          # 输出：110（第0行第1列）
print(df.iloc[1:3, 0:2])     # 选择第1-2行，第0-1列

# loc：按标签选择
print("\nloc 示例:")
print(df.loc['2023-01-02', 'High'])  # 输出：108
print(df.loc['2023-01-01':'2023-01-02', ['Open', 'Low']])

# at：快速修改
df.at['2023-01-03', 'Low'] = 100
print("\n修改后的 DataFrame:")
print(df)

my_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# 取前3个元素
print(my_list[0:3])    # 输出: [0, 1, 2]

# 取索引2到5（不包含5）
print(my_list[2:5])   # 输出: [2, 3, 4]

# 从索引3到末尾
print(my_list[3:])     # 输出: [3, 4, 5, 6, 7, 8, 9]

# 每隔2个元素取一次
print(my_list[::2])    # 输出: [0, 2, 4, 6, 8]

# 反转列表
print(my_list[::-1])   # 输出: [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

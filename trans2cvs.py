import pandas as pd
import json

with open("single-y.json", "r", encoding='utf-8') as f:
    data = json.loads(f.read())    # load的传入参数为字符串类型
#data = data["single"]["x3"]
pano = data["panoramic"]

# 创建一个DataFrame
#df = pd.DataFrame(data)
dp = pd.DataFrame(pano)
# 将DataFrame保存为Excel文件
output_file = 'data-y.xlsx'
#df.to_excel(output_file, index=False)
dp.to_excel(output_file, index=False)
print(f"Data has been successfully converted and saved to '{output_file}'.")

import pandas as pd
import numpy as np

'''
python数据处理三剑客之一pandas
https://pandas.pydata.org/pandas-docs/stable/user_guide 
https://www.pypandas.cn/docs/getting_started/10min.html
'''

dates = pd.date_range('20130101', periods=6)
df = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list('ABCD'))
print(dates)
print(df)

df2 = pd.DataFrame({'A': 1.,
                    'B': pd.Timestamp('20130102'),
                    'C': pd.Series(1, index=list(range(4)), dtype='float32'),
                    'D': np.array([3] * 4, dtype='int32'),
                    'E': pd.Categorical(["test", "train", "test", "train"]),
                    'F': 'foo'})
print(df2)
print(df2.dtypes)
print(df.head())
print(df.tail(5))
print(df.index)
print(df.columns)
df.describe() # 统计数据摘要
df.T # index columns互转
df.sort_index(axis=1, ascending=False) # 排序，axis=1 是columns，axis=1 是index
df.sort_values(by='B') # 按值排序 按B列中的值排序

# 切行
df.A
df['A']
# 切行
df['20130102':'20130104']
df[0:3]


import pandas as pd
import numpy as np

df = pd.DataFrame({'A': ['foo', 'bar', 'foo', 'bar',
                         'foo', 'bar', 'foo', 'foo'],
                   'B': ['one', 'one', 'two', 'three',
                         'two', 'two', 'one', 'three'],
                   'C': np.random.randn(8),
                   'D': np.random.randn(8)})

print(df)
groupedA = df.groupby('A').describe()
groupedAB = df.groupby(['A', 'B'])['C']
print('---'*18)
for a, b in groupedAB:
    print('--'*18)
    print(a)
    print('-' * 18)
    print(b)

import os
from itertools import groupby
import pandas as pd

def go():
    a = [1,2,3,4,5,6]
    # [print(x) for x in a]
    # [print(x) for x in a]
    a1 = groupby(a, key=lambda k: (k/2))
    for i in a1:
        print(i)
    for i in a1:
        print(i)

go()
# print(newList)
import os
import re
from itertools import groupby

import fuckit as fuckit
import pandas as pd
from tenacity import retry, stop_after_delay, wait_fixed


def go():
    a = [1, 2, 3, 4, 5, 6]
    # [print(x) for x in a]
    # [print(x) for x in a]
    a1 = groupby(a, key=lambda k: (k / 2))
    for i in a1:
        print(i)
    for i in a1:
        print(i)


class TryDo:
    def __init__(self, func, times=3):
        self.tries = times
        self.func = func

    def __iter__(self):
        self.currentTry = 1
        return self

    def __next__(self):
        if self.currentTry > self.tries:
            raise StopIteration(False)
        else:
            self.currentTry += 1
            self.func()
            raise StopIteration(True)

    # def do(self):


@retry(stop=stop_after_delay(3), wait=wait_fixed(2))
def stop_after_10_s():
    print("Stopping after 10 seconds")
    raise Exception


# f = iter( TryDo(do_something, 5))

# stop_after_10_s()
def errorfunc():
    raise Exception


def okfunc():
    print("ok")


# with fuckit:
#     errorfunc()
#     okfunc()
# re.match()

r = re.search(r'(?<=999)-?((?P<alpha>([A-Z](?![A-Z])))|(?P<num>\d(?!\d)))', "IPTD-999-B-彼女の姉貴とイケナイ関係-RIO", re.I)
#
print(r.groupdict())
print(r.groupdict()['alpha'])
print(r.group(2))
import re

line = "Cats are smarter than dogs"
matchObj = re.search(r'(?<=a)(.*) are (.*?) .*', line, re.M | re.I)
if matchObj:
    print("matchObj.group() : ", matchObj.group())
    print("matchObj.group(1) : ", matchObj.group(1))
    print("matchObj.group(2) : ", matchObj.group(2))
else:
    print("No match!!")

# print(r[-1])
# print(newList)

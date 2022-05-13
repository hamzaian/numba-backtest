import pandas as pd
import utils
import plotly.graph_objects as go

import numpy as np
#import matplotlib.pyplot as plt
import pandas_datareader as web
import pprint
from numba import jit,njit,vectorize

data_load = np.load("wt.npy", mmap_mode=None, allow_pickle=True, fix_imports=True, encoding='ASCII')
print(data_load)

'''
def my_func(a):

    """Average first and last element of a 1-D array"""

    return (a[0] + a[-1]) * 0.5

b = np.array([[1,2,3], [4,5,6], [7,8,9]])

np.apply_along_axis(my_func, 0, b)
array([4., 5., 6.])

np.apply_along_axis(my_func, 1, b)
array([2.,  5.,  8.])
'''

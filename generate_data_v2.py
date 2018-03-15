import os
import shutil
import sys
from time import time
from uuid import uuid4

import numpy as np
import pandas as pd

from data_manager2 import file_processor
from returns_quantization import add_returns_in_place
from utils import *

np.set_printoptions(threshold=np.nan)
pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)




def get_price_direction(btc_df, btc_slice, i, slice_size):
    last_price = btc_slice[-2:-1]['price_close'].values[0]
    next_price = btc_df[i + slice_size:i + slice_size + 1]['price_close'].values[0]
    if last_price < next_price:
        class_name = 'UP'
    else:
        class_name = 'DOWN'
    return class_name



def generate_cnn_dataset(data_folder, bitcoin_file, bitcoin_file_test):
    btc_df = file_processor(bitcoin_file)
    btc_df, levels = add_returns_in_place(btc_df)

    print('-' * 80)
    print('Those values should be roughly equal to 1/len(levels):')
    for ii in range(len(levels)):
        print(ii, np.mean((btc_df['close_price_returns_labels'] == ii).values))
    print(levels)
    print('-' * 80)

    slice_size = 40
    test_every_steps = 10
    n = len(btc_df) - slice_size

    shutil.rmtree(data_folder, ignore_errors=True)
    cycles = int((1e6)/2)
    for epoch in range(int(cycles)):
        st = time()

        # choose a random starting point
        i = np.random.choice(n)
        # take following 40 time periods (total 41)
        btc_slice = btc_df[i:i + slice_size]

        if btc_slice.isnull().values.any():
            # sometimes prices are discontinuous and nothing happened in one 5min bucket.
            # in that case, we consider this slice as wrong and we raise an exception.
            # it's likely to happen at the beginning of the data set where the volumes are low.
            raise Exception('NaN values detected. Please remove them.')

        class_name = get_price_direction(btc_df, btc_slice, i, slice_size)
        save_dir = os.path.join(data_folder, 'train', class_name)
        if epoch % test_every_steps == 0:
            save_dir = os.path.join(data_folder, 'valid', class_name)
        mkdir_p(save_dir)
        filename = save_dir + '/' + str(uuid4()) + '.png'
        save_to_file(btc_slice, filename=filename)
        print('epoch = {0}, time = {1:.3f}, filename = {2}'.format(str(epoch).zfill(8), time() - st, filename))

        
    btc_df = file_processor(bitcoin_file_test)
    nrow = len(btc_df)
    for epoch in range(int(nrow-slice_size-1)):
        st = time()

        # choose a random starting point
        i = epoch
        # take following 40 time periods (total 41)
        btc_slice = btc_df[i:i + slice_size]

        if btc_slice.isnull().values.any():
            # sometimes prices are discontinuous and nothing happened in one 5min bucket.
            # in that case, we consider this slice as wrong and we raise an exception.
            # it's likely to happen at the beginning of the data set where the volumes are low.
            raise Exception('NaN values detected. Please remove them.')

        class_name = get_price_direction(btc_df, btc_slice, i, slice_size)
        save_dir = os.path.join(data_folder, 'test', class_name)
        mkdir_p(save_dir)
        filename = save_dir + '/' + str(uuid4()) + '.png'
        save_to_file(btc_slice, filename=filename)
        print('epoch = {0}, time = {1:.3f}, filename = {2}'.format(str(epoch).zfill(8), time() - st, filename))
        
        

def main():
    PATH = 'data/btc/'
    data_file = f'{PATH}train2015_01_27__2018_02_06.csv'
    data_file_test = f'{PATH}test2018_02_06__2018_03_06.csv'
    data_folder = f'{PATH}btcgraphs/1/'
    
    generate_cnn_dataset(data_folder, data_file, data_file_test)


if __name__ == '__main__':
    main()

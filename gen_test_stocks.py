import os
import shutil
import sys
from time import sleep, time
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
#     last_price = btc_slice[-2:-1]['price_close'].values[0]
    lp = btc_slice[-1:]['price_close']
    last_price = lp.values[0]
    lp2 = btc_df[i + slice_size-1:i + slice_size]['price_close']
    last_price2 = lp2.values[0]
    np = btc_df[i + slice_size:i + slice_size + 1]['price_close']
    next_price = np.values[0]
    
    if last_price != last_price2:
        print(lp)
        print(lp2)
        print("last_price: " + str(last_price))
        print("last_price2: " + str(last_price2))
        print("next_price: " + str(next_price))
        df1 = btc_slice['price_close']
        df2 = btc_df[i:i+slice_size+1]['price_close']
        result = pd.concat([df2, df1], axis=1, join_axes=[df2.index])
        print(result.tail())
        print("\n\n")
        raise Exception("We aren't getting the same prices")
        print("HELP!!!")
        time.sleep(60)
        print("SOMETHING WENT WRONG")
        
        
    if last_price < next_price:
        class_name = 'UP'
    else:
        class_name = 'DOWN'
    return class_name



def generate_images(data_file, data_folder, stock_name):
    
    stock_df = pd.read_table(data_file, sep=',', header=1, index_col=0, names=
                           ['price_open', 'price_high', 'price_low', 'price_close'])



    #saving things to stockgraphs/test_... folders
    save_dir = os.path.join(data_folder, 'test_' + stock_name)
    shutil.rmtree(save_dir, ignore_errors=True)
    mkdir_p(save_dir)
    
    slice_size = 40

        
    btc_df = stock_df
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
        filename = save_dir + '/' + class_name + str(uuid4()) + '.png'
        save_to_file(btc_slice, filename=filename)
        print('epoch = {0}, time = {1:.3f}, filename = {2}'.format(str(epoch).zfill(8), time() - st, filename))
        
        

def main():
    PATH = 'data/btc/'
    data_folder = f'{PATH}stockgraphs/'
    

    stock_names = ['msft', 'fb', 'goog', 'aapl']

    for s in stock_names:
        print('Working on '+s, end='     \r')
        data_file = f'{PATH}stock_data_{s}.csv'
        generate_images(data_file, data_folder, stock_name=s+"2")

    


if __name__ == '__main__':
    main()

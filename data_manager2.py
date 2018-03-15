import datetime

import pandas as pd


# http://api.bitcoincharts.com/v1/csv/

def file_processor(data_file):
    print('Reading bitcoin market data file here: {}.'.format(data_file))

    # create df from tick data
    # [unix timestamp, price, volume]
    # use the timestamp as the index
    d = pd.read_table(data_file, sep=',', header=0, index_col=0, names=['price', 'volume'])

    # map the index to datetime
    d.index = d.index.map(lambda ts: datetime.datetime.fromtimestamp(int(ts)))
    d.index.names = ['DateTime_UTC']

    # split the prices into 5 minute groups 
    p = pd.DataFrame(d['price'].resample('5Min').ohlc().bfill())
    p.columns = ['price_open', 'price_high', 'price_low', 'price_close']

    # sum volume by 5 minute chunks
    v = pd.DataFrame(d['volume'].resample('5Min').sum())
    v.columns = ['volume']
    p['volume'] = v['volume']

    print('Done')
    return p



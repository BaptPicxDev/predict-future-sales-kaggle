import pandas as pd
from tqdm import tqdm
import datetime as dt
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pmdarima
import numpy as np


# Constants
train_set = 'data/sales_train.csv'
test_set = 'data/test.csv'
subs_set = 'data/sample_submission.csv'
items = 'data/items.csv'
categories = 'data/item_categories.csv'
shops = 'data/shops.csv'


def run():
    # Open the .csv file
    df_train_set = pd.read_csv(train_set, parse_dates=["date"]) # Training
    df_test_set = pd.read_csv(test_set) # Test
    df_subs_set = pd.read_csv(subs_set) # Sample submission
    df_shops_set = pd.read_csv(shops) # Shops
    df_items_set = pd.read_csv(items) # Items
    df_categories_set = pd.read_csv(categories) # Categories

    print(f"Train/Initial shape: {df_train_set.shape}.")
    print(f"Test/Initial shape: {df_train_set.shape}.")
    print(f"Sub/Initial shape: {df_train_set.shape}.")

    # Creating the df_train
    df_train_shop = pd.merge(df_train_set, df_shops_set, on='shop_id', how='inner')
    df_train_shop_item = pd.merge(df_train_shop, df_items_set, on='item_id', how='inner')
    df_train = pd.merge(df_train_shop_item, df_categories_set, on='item_category_id', how='inner')

    # Creating the df_test / df_subs
    df_test_shop = pd.merge(df_test_set, df_shops_set, on='shop_id', how='inner')
    df_test_shop_items = pd.merge(df_test_shop, df_items_set, on='item_id', how='inner')
    df_test = pd.merge(df_test_shop_items, df_categories_set, on='item_category_id', how='inner')

    # Train
    df_train_rows, df_train_columns = df_train.shape

    # Test
    df_test_rows, df_test_columns = df_test.shape
    print('Train set : \n train.csv : {} (rows/columns).'.format(df_train.shape))
    print('Test set : \n test.csv : {} (rows/columns).'.format(df_test.shape))
    print('Total nan values (train) : {}'.format(df_train.isnull().sum().sum()))
    print('Total nan values (test) : {}'.format(df_test.isnull().sum().sum()))
    df_train = (
        df_train
        .rename(
            columns={
                'shop_name': 'shop_name (RUSSIA)',
                'item_name': 'item_name (RUSSIA)',
                'item_category_name': 'item_category_name (RUSSIA)',
            }
        )
    )
    df_test = (
        df_test
        .rename(
            columns={
                'shop_name': 'shop_name (RUSSIA)',
                'item_name': 'item_name (RUSSIA)',
                'item_category_name': 'item_category_name (RUSSIA)',
            }
        )
    )
    print(f"Final shape: {df_train_set.shape}.")

    print("Creating pivot table")
    index = ["shop_id", "item_id", "item_category_id"]
    df_train_pivot = df_train.pivot_table(
        index=index,
        columns=["date_block_num"],
        values=["item_cnt_day"],
    #     fill_value=0,
        aggfunc="sum",
        margins=True,
    )
    df_train_pivot.columns = [col[1] for col in df_train_pivot.columns] # drop None columns
    df_train_pivot = df_train_pivot.reset_index(index)
    max_date_block_num = df_train.date_block_num.max()
    df_train_pivot["topredict"] = pd.isna
    df_train_pivot = df_train_pivot.drop(columns=["All"])

    print("Filtering pivot table")
    df_train_pivot_filtered = (
        pd.merge(
            left=df_train_pivot,
            right=df_test,
            on=["shop_id", "item_id", "item_category_id"],
        )
    )
    return df_train_pivot_filtered

def train(df_train_pivot_filtered):
    for index, row in tqdm(df_train_pivot_filtered.iterrows(), total=df_train_pivot_filtered.shape[0]):
        data = row[range(33)]
        mean = data.mean()
        if pd.isna(mean):
            mean = 0.0
        data = data.fillna(mean)
        data = data.astype(np.float64)
        try:
            r = pmdarima.arima.auto_arima(y=data.values)
        except UserWarning:
            pass
        # model
        model = SARIMAX(data.values, order=r.order, seasonal_order=(0, 0, 0, 0)) #r.seasonal_order)
        try:
            model_fit = model.fit(disp=0)
        except Exception:
            continue
        # predict
        predicted_values = model_fit.forecast()[0]
        df_train_pivot_filtered.loc[index] = df_train_pivot_filtered.loc[index].fillna(data.mean())
        df_train_pivot_filtered.loc[index, "topredict"] = predicted_values[0]

    df_train_pivot_filtered.to_csv(f"data/df{dt.datetime.now().date()}.csv", header=True, sep=";")

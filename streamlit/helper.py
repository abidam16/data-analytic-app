import pandas as pd
import numpy as np
from datetime import datetime
import geopandas as gpd
import matplotlib.pyplot as plt
import streamlit as st

class DataAnalysis:
    def __init__(self, df):
        self.df = df

    def create_sum_revenue_df(self):
        sorted_sum_revenue = self.df.groupby('seller_id').sum(numeric_only=True)[['payment_value_y']].reset_index().sort_values('payment_value_y', ascending=False)
        sorted_sum_revenue.rename(columns={
            'payment_value_y': 'revenue'
        }, inplace=True)
        return sorted_sum_revenue
    
    def create_sum_spend_df(self):
        sorted_sum_spend = self.df.groupby('customer_id').sum(numeric_only=True)[['total_spend']].reset_index().sort_values('total_spend', ascending=False)
        return sorted_sum_spend
    
    def create_count_product_df(self):
        sorted_count_prod = self.df.groupby('product_category_name_english').count()[['order_id']].reset_index().sort_values('order_id', ascending=False)
        sorted_count_prod.rename(columns={
            'order_id': 'product_count'
        }, inplace=True)
        return sorted_count_prod
    
    def create_revenue_by_month_year_df(self):
        revenue_by_month = self.df.dropna(subset='order_delivered_customer_date')
        revenue_by_month['year'] = revenue_by_month['order_delivered_customer_date'].dt.year
        revenue_by_month['month'] = revenue_by_month['order_delivered_customer_date'].dt.month
        count_order_by_month = revenue_by_month.groupby(['year', 'month']).agg({
            'order_id': 'count',
            'payment_value_y': 'sum'
        }).reset_index().sort_values(['year', 'month'])
        count_order_by_month.rename(columns={
            'order_id': 'order_count',
            'payment_value_y': 'revenue'
        }, inplace=True)
        return count_order_by_month
    
    def create_mean_delivery_time_df(self):
        new_orders_data = self.df.dropna(subset='order_delivered_customer_date')
        new_orders_data['day_difference'] = (new_orders_data['order_delivered_customer_date'] - new_orders_data['order_purchase_timestamp']) / np.timedelta64(1, 'D')
        mean_day_diff = new_orders_data.groupby('seller_id').mean(numeric_only=True)['day_difference'].reset_index().sort_values('day_difference', ascending=True)
        mean_day_diff['day_difference'] = mean_day_diff['day_difference'].round(2)
        return mean_day_diff
    
    def create_mean_estimated_diff_df(self):
        new_orders_data = self.df.dropna(subset='order_delivered_customer_date')
        new_orders_data['day_estimated_difference'] = (new_orders_data['order_estimated_delivery_date'] - new_orders_data['order_delivered_customer_date']) / np.timedelta64(1, 'D')
        mean_day_est_diff = new_orders_data.groupby('seller_id').mean(numeric_only=True)['day_estimated_difference'].reset_index().sort_values('day_estimated_difference', ascending=False)
        mean_day_est_diff['day_estimated_difference'] = mean_day_est_diff['day_estimated_difference'].round(2)
        return mean_day_est_diff
    
    def create_review_df(self):
        count_rating = self.df.groupby('review_score').count()['order_id'].reset_index().sort_values('order_id', ascending=False)
        count_rating.rename(columns={
            'order_id': 'rating_count'
        }, inplace=True)
        return count_rating
    
    def create_rfm_df(self):
        new_cust_data = self.df.dropna(subset='order_delivered_customer_date')[['customer_id',
                                                                           'order_estimated_delivery_date',
                                                                           'payment_value_y']].sort_values(['customer_id', 'order_estimated_delivery_date'])

        new_cust_data['recency'] = (pd.to_datetime('today') - new_cust_data['order_estimated_delivery_date']).dt.days
        frequency_data = self.df.groupby('customer_id')['order_id'].count().reset_index()
        frequency_data.rename(columns= {'order_id': 'frequency'}, inplace = True)
        new_cust_data = new_cust_data.merge(frequency_data, on = 'customer_id', how = 'left')
        recency_scores = [5, 4, 3, 2, 1]
        frequency_scores = [1, 2, 3, 4, 5]
        monetary_scores = [1, 2, 3, 4, 5]

        new_cust_data['recency_score'] = pd.cut(new_cust_data['recency'], bins = 5, labels= recency_scores)
        new_cust_data['frequency_score'] = pd.cut(new_cust_data['frequency'], bins = 5, labels= frequency_scores)
        new_cust_data['monetary_score'] = pd.cut(new_cust_data['payment_value_y'], bins= 5, labels= monetary_scores)

        new_cust_data['recency_score'] = new_cust_data['recency_score'].astype(int)
        new_cust_data['frequency_score'] = new_cust_data['frequency_score'].astype(int)
        new_cust_data['monetary_score'] = new_cust_data['monetary_score'].astype(int)

        new_cust_data['RFM_score'] = new_cust_data['recency_score'] + new_cust_data['frequency_score'] + new_cust_data['monetary_score']

        segment_labels = ['Low-Value', 'Mid-Value', 'High-Value']
        new_cust_data['value_segment'] = pd.qcut(new_cust_data['RFM_score'], q= 3, labels= segment_labels)

        new_cust_data['RFM_customer_segments'] = ''

        new_cust_data.loc[new_cust_data['RFM_score'] >= 9, 'RFM_customer_segments'] = 'Champions'
        new_cust_data.loc[(new_cust_data['RFM_score'] >= 6) & (new_cust_data['RFM_score'] < 9), 'RFM_customer_segments'] = 'Potential Loyalists'
        new_cust_data.loc[(new_cust_data['RFM_score'] >= 5) & (new_cust_data['RFM_score'] < 6), 'RFM_customer_segments'] = 'At-Risk Customers'
        new_cust_data.loc[(new_cust_data['RFM_score'] >= 4) & (new_cust_data['RFM_score'] < 5), 'RFM_customer_segments'] = 'Cannot Lose'
        new_cust_data.loc[(new_cust_data['RFM_score'] >= 3) & (new_cust_data['RFM_score'] < 4), 'RFM_customer_segments'] = 'Lost'

        segment_product_counts = new_cust_data.groupby(['value_segment', 'RFM_customer_segments']).size().reset_index(name = 'count')
        segment_product_counts = segment_product_counts.sort_values('count', ascending= False)
        segment_product_counts = segment_product_counts[segment_product_counts['count'] > 1]
        return new_cust_data, segment_product_counts
    
class GeoAnalysis:
    def __init__(self, cust_df, sell_df):
        self.cust_df = cust_df
        self.sell_df = sell_df

    def plot_customer_geolocation(self):
        gcdf = gpd.GeoDataFrame(
            self.cust_df, geometry=gpd.points_from_xy(self.cust_df.geolocation_lng, self.cust_df.geolocation_lat), crs="EPSG:4326"
        )
        street_map = gpd.read_file('data/ne_10m_admin_0_countries.shp')
        fig, ax = plt.subplots(figsize=(35, 35))
        street_map.plot(ax=ax)
        ax.axis('off')
        gcdf.plot(ax=ax, color="red", alpha=0.2, markersize=5)
        ax.set_title('Peta Persebaran Customer', fontsize=50)
        st.pyplot(fig)
        return
    
    def plot_seller_geolocation(self):
        gsdf = gpd.GeoDataFrame(
            self.sell_df, geometry=gpd.points_from_xy(self.sell_df.geolocation_lng, self.sell_df.geolocation_lat), crs="EPSG:4326"
        )
        street_map = gpd.read_file('data/ne_10m_admin_0_countries.shp')
        fig, ax = plt.subplots(figsize=(35, 35))
        street_map.plot(ax=ax)
        plt.axis('off')
        gsdf.plot(ax=ax, color="red", alpha=0.2, markersize=5)
        ax.set_title('Peta Persebaran Seller', fontsize=50)
        st.pyplot(fig)
        return
        
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from babel.numbers import format_currency
import geopandas as gpd
from helper import DataAnalysis, GeoAnalysis

sns.set(style='dark')

all_data = pd.read_csv('data/new_all_data.csv')
geo_cust_data = pd.read_csv('data/geo_cust_data.csv')
geo_sell_data = pd.read_csv('data/geo_sell_data.csv')
all_data.sort_values('order_purchase_timestamp', inplace=True)
datetime_column = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 
                   'order_delivered_customer_date', 'order_estimated_delivery_date']
all_data.sort_values(by=datetime_column, inplace=True)
all_data.reset_index(inplace=True)

for column in datetime_column:
    all_data[column] = pd.to_datetime(all_data[column])

min_date = all_data['order_purchase_timestamp'].min()
max_date = all_data['order_purchase_timestamp'].max()

with st.sidebar:
    st.image('data/logo.png')

    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date, value=[min_date, max_date]
    )

main_df = all_data[(all_data["order_purchase_timestamp"] >= str(start_date)) & 
                   (all_data["order_purchase_timestamp"] <= str(end_date))]

helper_func = DataAnalysis(main_df)
sum_revenue_df = helper_func.create_sum_revenue_df()
sum_spend_df = helper_func.create_sum_spend_df()
count_product_df = helper_func.create_count_product_df()
revenue_by_month_year_df = helper_func.create_revenue_by_month_year_df()
mean_delivery_time_df = helper_func.create_mean_delivery_time_df()
mean_estimated_diff_df = helper_func.create_mean_estimated_diff_df()
review_df = helper_func.create_review_df()
cust_df, segment_product_df = helper_func.create_rfm_df()

plot_func = GeoAnalysis(geo_cust_data, geo_sell_data)

st.header('E-Commerce Dashboard :shopping_trolley:')

st.subheader('Monthly Order')
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
x_label = [f'{months[i-1]} {j}' for i, j in zip(revenue_by_month_year_df['month'], revenue_by_month_year_df['year'])]

col1, col2 = st.columns(2)

with col1:
    total_orders = revenue_by_month_year_df.order_count.sum()
    st.metric('Total orders', value=total_orders)

with col2:
    total_revenue = revenue_by_month_year_df.revenue.sum()
    st.metric('Total revenue', value=total_revenue)

fig, ax = plt.subplots(figsize=(35, 15))
sns.lineplot(x=x_label, y=revenue_by_month_year_df["revenue"], marker="o", linewidth=3, color='cornflowerblue', ax=ax)
ax.tick_params(axis='x', labelrotation=60, labelsize=30)
ax.set_title('Revenue by Month', fontsize=50, pad=30)
ax.set_ylabel('Revenue', fontsize=30)
ax.set_xlabel('Month', fontsize=30)
st.pyplot(fig)

st.subheader('Highest & Lowest Seller Revenue')

fig, ax = plt.subplots(1, 2, figsize=(35, 15))

max_value = sum_revenue_df['revenue'].head(5).max()
colors_high = ['silver' if v != max_value else 'cornflowerblue' for v in sum_revenue_df['revenue'].head(5)]
sns.barplot(x=sum_revenue_df['seller_id'].head(5).str[:10],
            y=sum_revenue_df['revenue'].head(5),
            palette=colors_high, ax=ax[0])
for i, v in enumerate(sum_revenue_df['revenue'].head(5)):
    if v == max_value:
        ax[0].text(i, v, str(v), ha='center', va='bottom', fontsize=25, color='cornflowerblue')

ax[0].set_xlabel('Seller Id', fontsize=30)
ax[0].set_ylabel('Revenue', fontsize=30)
ax[0].set_title('Highest Revenue', fontsize=50, pad=30)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=30)

min_value = sum_revenue_df['revenue'].tail(5).min()
colors_low = ['silver' if v != min_value else 'firebrick' for v in sum_revenue_df['revenue'].tail(5)]
sns.barplot(x=sum_revenue_df['seller_id'].tail(5).iloc[::-1].str[:10],
            y=sum_revenue_df['revenue'].tail(5).iloc[::-1],
            palette=colors_low[::-1], ax=ax[1])
for i, v in enumerate(sum_revenue_df['revenue'].tail(5).iloc[::-1]):
    if v == min_value:
        ax[1].text(i, v, str(v), ha='center', va='bottom', fontsize=25, color='firebrick')

ax[1].set_xlabel('Seller Id', fontsize=30)
ax[1].set_ylabel('Revenue', fontsize=30)
ax[1].set_title('Lowest Revenue', fontsize=50, pad=30)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.subheader('Highest & Lowest Customer Spend')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
max_value = sum_spend_df['total_spend'].head(5).max()
colors_high = ['silver' if v != max_value else 'cornflowerblue' for v in sum_spend_df['total_spend'].head(5)]
sns.barplot(x=sum_spend_df['customer_id'].head(5).str[:10],
            y=sum_spend_df['total_spend'].head(5),
            palette=colors_high, ax=ax[0])
for i, v in enumerate(sum_spend_df['total_spend'].head(5)):
    if v == max_value:
        ax[0].text(i, v, str(v), ha='center', va='bottom', fontsize=30, color='cornflowerblue')

ax[0].set_xlabel('Customer Id', fontsize=30)
ax[0].set_ylabel('Spend', fontsize=30)
ax[0].set_title('Highest Customer Spend', fontsize=50, pad=30)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=30)

min_value = sum_spend_df['total_spend'].tail(5).min()
colors_low = ['silver' if v != min_value else 'firebrick' for v in sum_spend_df['total_spend'].tail(5)]
sns.barplot(x=sum_spend_df['customer_id'].tail(5).iloc[::-1].str[:10],
            y=sum_spend_df['total_spend'].tail(5).iloc[::-1],
            palette=colors_low[::-1], ax=ax[1])
for i, v in enumerate(sum_spend_df['total_spend'].tail(5).iloc[::-1]):
    if v == min_value:
        ax[1].text(i, v, str(v), ha='center', va='bottom', fontsize=30, color='firebrick')

ax[1].set_xlabel('Customer Id', fontsize=30)
ax[1].set_ylabel('Spend', fontsize=30)
ax[1].set_title('Lowest Customer Spend', fontsize=50, pad=30)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.subheader('Popular & Unpopular product')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
max_value = count_product_df['product_count'].head(5).max()
colors_high = ['silver' if v != max_value else 'cornflowerblue' for v in count_product_df['product_count'].head(5)]
sns.barplot(x=count_product_df['product_category_name_english'].head(5),
            y=count_product_df['product_count'].head(5),
            palette=colors_high, ax=ax[0])
for i, v in enumerate(count_product_df['product_count'].head(5)):
    if v == max_value:
        ax[0].text(i, v, str(v), ha='center', va='bottom', fontsize=30, color='cornflowerblue')

ax[0].set_xlabel('Product category', fontsize=30)
ax[0].set_ylabel('Total sold', fontsize=30)
ax[0].set_title('Most Popular Product', fontsize=50, pad=30)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=30, labelrotation=15)

min_value = count_product_df['product_count'].tail(5).min()
colors_low = ['silver' if v != min_value else 'firebrick' for v in count_product_df['product_count'].tail(5)]
sns.barplot(x=count_product_df['product_category_name_english'].tail(5).iloc[::-1],
            y=count_product_df['product_count'].tail(5).iloc[::-1],
            palette=colors_low[::-1], ax=ax[1])
for i, v in enumerate(count_product_df['product_count'].tail(5).iloc[::-1]):
    if v == min_value:
        ax[1].text(i, v, str(v), ha='center', va='bottom', fontsize=30, color='firebrick')

ax[1].set_xlabel('Product category', fontsize=30)
ax[1].set_ylabel('Total sold', fontsize=30)
ax[1].set_title('Most Unpopular Product', fontsize=50, pad=30)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=30, labelrotation=15)

st.pyplot(fig)

st.subheader('Most Responsive & Unresponsive Seller')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
max_value = mean_delivery_time_df['day_difference'].head(5).min()
colors_high = ['silver' if v != max_value else 'cornflowerblue' for v in mean_delivery_time_df['day_difference'].head(5)]
sns.barplot(x=mean_delivery_time_df['seller_id'].head(5).str[:10],
            y=mean_delivery_time_df['day_difference'].head(5),
            palette=colors_high, ax=ax[0])
for i, v in enumerate(mean_delivery_time_df['day_difference'].head(5)):
    if v == max_value:
        ax[0].text(i, v, str(v), ha='center', va='bottom', fontsize=30, color='cornflowerblue')

ax[0].set_xlabel('Seller Id', fontsize=30)
ax[0].set_ylabel('Day difference', fontsize=30)
ax[0].set_title('Most Responsive Seller', fontsize=50, pad=30)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=30)

min_value = mean_delivery_time_df['day_difference'].tail(5).max()
colors_low = ['silver' if v != min_value else 'firebrick' for v in mean_delivery_time_df['day_difference'].tail(5)]
sns.barplot(x=mean_delivery_time_df['seller_id'].tail(5).iloc[::-1].str[:10],
            y=mean_delivery_time_df['day_difference'].tail(5).iloc[::-1],
            palette=colors_low[::-1], ax=ax[1])
for i, v in enumerate(mean_delivery_time_df['day_difference'].tail(5).iloc[::-1]):
    if v == min_value:
        ax[1].text(i, v, str(v), ha='center', va='bottom', fontsize=30, color='firebrick')

ax[1].set_xlabel('Seller Id', fontsize=30)
ax[1].set_ylabel('Day difference', fontsize=30)
ax[1].set_title('Most Unresponsive Seller', fontsize=50, pad=30)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.subheader('Fastest & Slowest Package Delivery Than Estimated')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
max_value = mean_estimated_diff_df['day_estimated_difference'].head(5).max()
colors_high = ['silver' if v != max_value else 'cornflowerblue' for v in mean_estimated_diff_df['day_estimated_difference'].head(5)]
sns.barplot(x=mean_estimated_diff_df['seller_id'].head(5).str[:10],
            y=mean_estimated_diff_df['day_estimated_difference'].head(5),
            palette=colors_high, ax=ax[0])
for i, v in enumerate(mean_estimated_diff_df['day_estimated_difference'].head(5)):
    if v == max_value:
        ax[0].text(i, v, str(v), ha='center', va='bottom', fontsize=30, color='cornflowerblue')

ax[0].set_xlabel('Seller Id', fontsize=30)
ax[0].set_ylabel('Day difference', fontsize=30)
ax[0].set_title('Fastest Package Delivary Than Estimated', fontsize=50, pad=30)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=30)

min_value = mean_estimated_diff_df['day_estimated_difference'].tail(5).min()
colors_low = ['silver' if v != min_value else 'firebrick' for v in mean_estimated_diff_df['day_estimated_difference'].tail(5)]
sns.barplot(x=mean_estimated_diff_df['seller_id'].tail(5).iloc[::-1].str[:10],
            y=mean_estimated_diff_df['day_estimated_difference'].tail(5).iloc[::-1],
            palette=colors_low[::-1], ax=ax[1])
for i, v in enumerate(mean_estimated_diff_df['day_estimated_difference'].tail(5).iloc[::-1]):
    if v == min_value:
        ax[1].text(i, v-1, str(v), ha='center', va='top', fontsize=30, color='firebrick')

ax[1].set_xlabel('Seller Id', fontsize=30)
ax[1].set_ylabel('Day difference', fontsize=30)
ax[1].set_title('Slowest Package Delivary Than Estimated', fontsize=50, pad=30)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.subheader('Customer Review')

fig, ax = plt.subplots(figsize=(35, 15))
max_value = review_df['rating_count'].max()
colors_high = ['silver' if v != max_value else 'cornflowerblue' for v in review_df['rating_count']]
sns.barplot(x=review_df['review_score'],
            y=review_df['rating_count'],
            palette=colors_high,
            order=review_df.review_score,
            ax=ax)
for i, v in enumerate(review_df['rating_count']):
    if v == max_value:
        ax.text(i, v, str(v), ha='center', va='bottom', fontsize=30, color='cornflowerblue')

ax.set_xlabel('Rating', fontsize=30)
ax.set_ylabel('Customer count', fontsize=30)
ax.set_title('Customer Satisfaction Rating', fontsize=50, pad=30)
ax.tick_params(axis='y', labelsize=30)
ax.tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.subheader('RFM Analysis')

segment_counts = cust_df['value_segment'].value_counts().reset_index()
segment_counts.columns = ['value_segment', 'count']

fig, ax = plt.subplots(figsize=(35, 15))
max_value = segment_counts['count'].max()
colors_high = ['silver' if v != max_value else 'cornflowerblue' for v in segment_counts['count']]
sns.barplot(x=segment_counts['value_segment'],
            y=segment_counts['count'],
            palette=colors_high,
            ax=ax)
for i, v in enumerate(segment_counts['count']):
    if v == max_value:
        ax.text(i, v, str(v), ha='center', va='bottom', fontsize=30, color='cornflowerblue')

ax.set_xlabel('Category', fontsize=30)
ax.set_ylabel('Customer count', fontsize=30)
ax.set_title('Customer Category Based On RFM Value', fontsize=50, pad=30)
ax.tick_params(axis='y', labelsize=30)
ax.tick_params(axis='x', labelsize=30)

st.pyplot(fig)

x_label = [f'{i}-{j}' for i, j in zip(segment_product_df['value_segment'],
                                      segment_product_df['RFM_customer_segments'])]

fig, ax = plt.subplots(figsize=(35, 15))
max_value = segment_product_df['count'].max()
colors_high = ['silver' if v != max_value else 'cornflowerblue' for v in segment_product_df['count']]
sns.barplot(x=x_label,
            y=segment_product_df['count'],
            palette=colors_high,
            ax=ax)
for i, v in enumerate(segment_product_df['count']):
    if v == max_value:
        ax.text(i, v, str(v), ha='center', va='bottom', fontsize=30, color='cornflowerblue')

ax.set_xlabel('Category', fontsize=30)
ax.set_ylabel('Customer count', fontsize=30)
ax.set_title('Customer Category Based On RFM Score', fontsize=50, pad=30)
ax.tick_params(axis='x', labelrotation=15)
ax.tick_params(axis='y', labelsize=30)
ax.tick_params(axis='x', labelsize=30)

st.pyplot(fig)

tab1, tab2 = st.tabs(['Customer', 'Seller'])

with tab1:
    st.subheader('Customer Geolocation')
    plot_func.plot_customer_geolocation()

with tab2:
    st.subheader('Seller Geolocation')
    plot_func.plot_seller_geolocation()

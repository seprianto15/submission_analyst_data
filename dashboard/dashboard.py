import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_high_order_df(df):
    high_order_df = df.groupby('product_category_name').order_item_id.sum().sort_values(ascending=False).reset_index()
    
    return high_order_df

def create_low_order_df(df):
    low_order_df = df.groupby('product_category_name').order_item_id.sum().sort_values(ascending=True).reset_index()
    
    return low_order_df

def create_on_time_delivery_df(df):
    on_time_delivery_df = df[df['status_delivery'] == 'On Time'].groupby(by='customer_city').order_id.nunique().reset_index()
    
    return on_time_delivery_df

def create_late_delivery_df(df):
    late_delivery_df = df[df['status_delivery'] == 'Delay'].groupby(by='customer_city').order_id.nunique().reset_index().sort_values(by='order_id', ascending=False)
    
    return late_delivery_df

def create_rfm_df(df):
    rfm_df = df.groupby(by='customer_id', as_index=False).agg({
        'order_purchase_timestamp' : 'max',
        'order_id' : 'nunique',
        'price' : 'sum'
        })
    
    rfm_df.columns = ['customer_id', 'max_order_timestamp', 'frequency', 'monetary']
    rfm_df['max_order_timestamp'] = rfm_df['max_order_timestamp'].dt.date
    recent_date = all_df['order_purchase_timestamp'].dt.date.max()
    rfm_df['recency'] = rfm_df['max_order_timestamp'].apply(lambda x: (recent_date - x).days)
    rfm_df.drop('max_order_timestamp', axis=1, inplace=True)
      
    return rfm_df

all_df = pd.read_csv("https://raw.githubusercontent.com/seprianto15/submission_analyst_data/refs/heads/master/dashboard/all_data.csv")

datetime_columns = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date',
                    'order_delivered_customer_date', 'order_estimated_delivery_date', 'shipping_limit_date']
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://img.icons8.com/?size=100&id=cjGKAQLQz2TV&format=png&color=0000000")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                (all_df["order_approved_at"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
high_order_df = create_high_order_df(main_df)
low_order_df = create_low_order_df(main_df)
on_time_delivery_df = create_on_time_delivery_df(main_df)
late_delivery_df = create_late_delivery_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header('Warung Kopi Analysis Dashboard :baby:')

st.subheader('Daily Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)


st.subheader("Best & Worst Performing Product")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

# Chart best performing product

sns.barplot(
    x='order_item_id',
    y='product_category_name',
    data=high_order_df.head(5),
    palette='Greens_d',
    ax=ax[0]
)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

# Chart worst performing product

sns.barplot(
    x='order_item_id',
    y='product_category_name',
    data=low_order_df.head(5),
    palette='Reds_d',
)
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()

st.pyplot(fig)

st.subheader("Number of On-Time Deliveries vs Number of Late Deliveries by City")

col1, col2 = st.columns(2)

with col1:
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    sns.barplot(
        x='order_id',
        y='customer_city',
        data=on_time_delivery_df.sort_values(by="order_id", ascending=False).head(5),
        palette='Greens_d',
        ax=ax
    )
    
    ax.set_title("Number of On-Time Deliveries by City", loc="center", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)

with col2:
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    sns.barplot(
        x='order_id',
        y='customer_city',
        data=late_delivery_df.sort_values(by="order_id", ascending=False).head(5),
        palette='Reds_d',
        ax=ax
    )
    
    ax.set_title("Number of Late Deliveries by City", loc="center", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)

st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)
 
st.caption('Copyright (c) Sianipar 2025')

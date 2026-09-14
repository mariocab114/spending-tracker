import streamlit as st
import pandas as pd
from categorizer import categorize

st.title("💰 Spending Tracker")
st.write("Upload a CSV of your transactions to see them categorized and summarized.")

uploaded_file = st.file_uploader("Upload your transactions CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df["category"] = df["description"].apply(categorize)

    st.subheader("Spending by Category")
    category_totals = df.groupby("category")["amount"].sum()
    st.bar_chart(category_totals)

    st.subheader("Total Spent")
    st.metric(label="Total", value=f"${df['amount'].sum():,.2f}")

    st.subheader("All Transactions")
    st.dataframe(df)
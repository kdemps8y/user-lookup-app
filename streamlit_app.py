import streamlit as st
import sqlite3
import pandas as pd

st.title("User Lookup")

user_id = st.text_input("Enter User ID (e.g. u001):")

if user_id:
    conn = sqlite3.connect("users.db")
    df = pd.read_sql_query("SELECT * FROM users WHERE user_id = ?", conn, params=(user_id,))
    conn.close()

    if df.empty:
        st.warning("No user found.")
    else:
        st.success("User found:")
        st.dataframe(df)

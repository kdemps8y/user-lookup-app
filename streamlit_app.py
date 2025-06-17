import streamlit as st
import pandas as pd
from hashlib import sha3_256
from io import BytesIO

st.title("User Lookup from Hashed Export")

# Upload the hashed export Excel file
uploaded_file = st.file_uploader("Upload users_hashed_export.xlsx", type="xlsx")

# Input for user ID
user_id = st.text_input("Enter User ID (e.g., u001):")

def hash_id(user_id, table_name):
    return sha3_256(f"{user_id}{table_name}".encode()).hexdigest()

if uploaded_file and user_id:
    # Load all sheets
    xls = pd.ExcelFile(uploaded_file)
    sheets = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}

    # Reconstruct the user row
    record = {"user_id": user_id}
    for table, df in sheets.items():
        if not isinstance(df, pd.DataFrame):
            continue  # skip if sheet didn't load as a DataFrame
        df.columns = df.columns.map(str).str.strip()  # normalize column names
        if df.empty or "Primary_Key" not in df.columns:
            continue  # skip empty or invalid sheets
        h = hash_id(user_id, table)
        match = df[df['Primary_Key'] == h]
        if not match.empty:
            value = match.iloc[0, 1]  # second column is the value
            record[table.lower()] = value
        else:
            record[table.lower()] = "(not found)"

    df_user = pd.DataFrame([record])
    st.success("User found:")
    st.dataframe(df_user)

    # Enable download of reconstructed row
    output = BytesIO()
    df_user.to_excel(output, index=False, engine='openpyxl')
    st.download_button(
        label="Download users_from_db.xlsx",
        data=output.getvalue(),
        file_name="users_from_db.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif uploaded_file and not user_id:
    st.info("Please enter a user ID to reconstruct data.")
elif user_id and not uploaded_file:
    st.info("Please upload users_hashed_export.xlsx to proceed.")



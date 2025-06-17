
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
    xls = pd.ExcelFile(uploaded_file)
    sheets = {
        sheet: df.rename(columns=lambda x: str(x).strip())
        for sheet, df in {s: xls.parse(s) for s in xls.sheet_names}.items()
    }

    record = {"user_id": user_id}

    # Assemble full_name
    def get_value(table):
        df = sheets.get(table)
        if df is not None and not df.empty and "Primary_Key" in df.columns:
            h = hash_id(user_id, table)
            match = df[df["Primary_Key"] == h]
            if not match.empty:
                return match.iloc[0, 1]
        return "(not found)"

    first_name = get_value("FirstName")
    last_name = get_value("LastName")
    record["full_name"] = f"{first_name} {last_name}".strip()
    record["phone_number"] = get_value("Phone")
    record["date_of_birth"] = get_value("DateOfBirth")
    record["gender"] = get_value("Gender")
    
    # Assemble address
    addr_parts = [get_value(f"Addr{i}") for i in range(5)]
    if addr_parts[0] != "":
        record["address"] = f"{addr_parts[0]} {addr_parts[1]}, {addr_parts[2]}, {addr_parts[3]} {addr_parts[4]}"
    else:
        record["address"] = f"{addr_parts[1]}, {addr_parts[2]}, {addr_parts[3]} {addr_parts[4]}"

    # Assemble IP address
    ip_parts = [get_value(f"IP{i}") for i in range(4)]
    record["ip_address"] = ".".join(ip_parts)

    # Assemble device_id
    device_type = get_value("Device0")
    device_token = get_value("Device1")
    record["device_id"] = f"{device_type}_{device_token}"

    # Assemble location
    lat_int = get_value("LAT0")
    lat_frac = get_value("LAT1")
    lon_int = get_value("LON0")
    lon_frac = get_value("LON1")
    try:
        lat = float(lat_int) + float(lat_frac)
        lon = float(lon_int) + float(lon_frac)
        record["location_lat"] = round(lat, 6)
        record["location_lon"] = round(lon, 6)
    except:
        record["location_lat"] = "(not found)"
        record["location_lon"] = "(not found)"

    # Health status
    record["health_status"] = get_value("HealthStatus")

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


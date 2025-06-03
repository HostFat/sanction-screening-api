import requests
import os
from dotenv import load_dotenv
import json
import streamlit as st
import re
import pandas as pd

# Load environment variables
load_dotenv()
api_key = os.getenv('API_KEY')

addresses = [
    'LNwgtMxcKUQ51dw7bQL1yPQjBVZh6QEqsd',
    '0x184BD594a5f06ABb86c75dFcCa588071dc11d6D0',
    '0x1da5821544e25c636c1417ba96ade4cf6d2f9b5a', 
    'qznpd2tsk0l3hwdcygud3ch4tgxjwg5ptqa93ltwj4'
]

headers = {
    'X-API-Key': api_key,
    'Accept': 'application/json',
}

st.title("Chainalysis Digital Currency Address Extractor")

# === Table Preparation ===
extracted_rows = []

# === Detailed View Per Address ===
for address in addresses:
    url = f'https://public.chainalysis.com/api/v1/address/{address}'
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        st.warning(f"Failed to fetch data for {address}")
        continue

    data = response.json()

    with st.expander(f"Sanctioned Address: {address}"):
        st.json(data)

        st.subheader('Description Breakdown')

        identifications = data.get("identifications", [])
        description = ""
        name = "N/A"
        category = "N/A"

        if identifications and isinstance(identifications, list):
            id_obj = identifications[0]
            description = id_obj.get("description", "")
            name = id_obj.get("name", "N/A")
            category = id_obj.get("category", "N/A")

        # Regex match for: Digital Currency Address - <SYM> <ADDRESS>
        pattern = r"(?:alt\.\s*)?Digital Currency Address - ([A-Z]{2,4}) ([a-zA-Z0-9]{26,64})"
        matches = re.findall(pattern, description)

        if matches:
            st.write("**Extracted Digital Currency Addresses:**")
            for abbr, addr in matches:
                st.badge(f"{abbr} {addr}", color="green", icon="💰")
                # Append to table data
                extracted_rows.append({
                    "Sanctioned Address": address,
                    "Name": name,
                    "Category": category,
                    "Currency": abbr,
                    "Associated Address": addr,
                })
        else:
            st.write("No digital currency addresses found.")

# === Final Table View ===
if extracted_rows:
    st.subheader("📊 Extracted Digital Currency Table")
    df = pd.DataFrame(extracted_rows)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No digital currency addresses extracted.")

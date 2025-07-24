import streamlit as st
from dotenv import load_dotenv
import os
import requests
import re
import pandas as pd

from components.login import authenticate_user, logout

# Load API key
load_dotenv()
api_key = 'b212869ae2e19709e66b162d9e969d71861166c63a43b950e611d3fc41fd0c0d'

# Default hardcoded addresses
initial_addresses = [
    # 'LNwgtMxcKUQ51dw7bQL1yPQjBVZh6QEqsd',
    # '0x184BD594a5f06ABb86c75dFcCa588071dc11d6D0',
    # '0x1da5821544e25c636c1417ba96ade4cf6d2f9b5a', 
    # 'qznpd2tsk0l3hwdcygud3ch4tgxjwg5ptqa93ltwj4',
    # 'bc1q2jys00x2rgdkm3xnewuucqacytu0a7echupu8y'
]

headers = {
    'X-API-Key': api_key,
    'Accept': 'application/json',
}

st.set_page_config(
    page_title="Chainalysis Sanction Address Lookup",
    page_icon="💰",
    layout="centered",
)

if authenticate_user():
    if st.button("🔒 Logout"):
        logout()

    st.title("Chainalysis Digital Currency Address Extractor")
    extracted_rows = []

    # === Step 1: Capture User Input ===
    with st.form("wallet_search_form"):
        new_address = st.text_input("🔍 Enter a Wallet Address to Search:")
        submitted = st.form_submit_button("Search")

    # === Step 2: Save New Address in Session State ===
    if submitted and new_address:
        if "user_addresses" not in st.session_state:
            st.session_state.user_addresses = []
        if new_address not in st.session_state.user_addresses and new_address not in initial_addresses:
            st.session_state.user_addresses.append(new_address)

    # Combine all addresses
    user_addresses = st.session_state.get("user_addresses", [])
    all_addresses = user_addresses + initial_addresses

    # === Step 3: Query Chainalysis API ===
    processed = set()
    for address in all_addresses:
        if address in processed:
            continue
        processed.add(address)

        url = f'https://public.chainalysis.com/api/v1/address/{address}'
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            st.warning(f"⚠️ Failed to fetch data for {address}")
            continue

        data = response.json()

        with st.expander(f"Sanctioned Address: {address}"):
            st.json(data)
            st.subheader("Description Breakdown")

            identifications = data.get("identifications", [])
            description = ""
            name = "N/A"
            category = "N/A"

            if identifications and isinstance(identifications, list):
                id_obj = identifications[0]
                description = id_obj.get("description", "")
                name = id_obj.get("name", "N/A")
                category = id_obj.get("category", "N/A")

            # Match address format
            pattern = r"(?:alt\.\s*)?Digital Currency Address - ([A-Z]{2,4}) ([a-zA-Z0-9]{26,64})"
            matches = re.findall(pattern, description)

            if matches:
                st.write("**Extracted Associated Addresses:**")
                for abbr, addr in matches:
                    st.badge(f"{abbr} {addr}", color="green", icon="💰")
                    extracted_rows.append({
                        "Sanctioned Address": address,
                        "Name": name,
                        "Category": category,
                        "Currency": abbr,
                        "Associated Address": addr,
                    })
            else:
                st.write("No associated addresses found.")
                extracted_rows.append({
                    "Sanctioned Address": address,
                    "Name": name,
                    "Category": category,
                    "Currency": "None",
                    "Associated Address": "None",
                })

    # === Final Table ===
    if extracted_rows:
        st.subheader("📊 Extracted Digital Currency Table")
        df = pd.DataFrame(extracted_rows)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No digital currency addresses extracted.")

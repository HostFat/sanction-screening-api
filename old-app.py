import requests
import os
from dotenv import load_dotenv
import json
import streamlit as st
import re


load_dotenv()  # Load environment variables from .env file

api_key = os.getenv('API_KEY')  # Ensure you have set your API key in the environment variables

# print("API Key:", api_key)


addresses = [
    'LNwgtMxcKUQ51dw7bQL1yPQjBVZh6QEqsd',
    '0x184BD594a5f06ABb86c75dFcCa588071dc11d6D0'
]


headers = {
    'X-API-Key': api_key,
    'Accept': 'application/json',
}

st.title("Chainalysis Address Lookup")

for address in addresses:
    url = f'https://public.chainalysis.com/api/v1/address/{address}'
    response = requests.get(url, headers=headers)
    data = response.json()

    with st.expander(f"Address: {address}"):
        st.json(data)

        st.subheader('Description Breakdown')

        identifications = data.get("identifications", [])

        if identifications and isinstance(identifications, list):
            # Use the first item in the list (or loop through all if needed)
            description = identifications[0].get("description", "")
        else:
            description = ""

        # print("Description:", description)

        # Regex to match: Digital Currency Address - <SYM> <ADDRESS>
        pattern = r"(?:alt\.\s*)?Digital Currency Address - ([A-Z]{2,4}) ([a-zA-Z0-9]{26,62})"
        matches = re.findall(pattern, description)

        if matches:
            st.write("**Extracted Digital Currency Addresses:**")
            for abbr, addr in matches:
                st.badge(f"{abbr} {addr}", color="green", icon="💰")
        else:
            st.write("No digital currency addresses found in description.")


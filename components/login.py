import streamlit as st
import hashlib
import uuid

def generate_token():
    return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

def creds_entered():
    if st.session_state["user"].strip() == "admin" and st.session_state['password'].strip() == "admin":
        st.session_state["authenticated"] = True
        token = generate_token()
        st.session_state["auth_token"] = token
        st.query_params["token"] = token  # official query param API
    else:
        st.session_state["authenticated"] = False
        if not st.session_state["password"]:
            st.warning("Please enter your password.")
        elif not st.session_state["user"]:
            st.warning("Please enter your username.")
        else:
            st.error("Invalid credentials. Please try again.")

def authenticate_user():
    token_from_url = st.query_params.get("token", None)

    if "authenticated" not in st.session_state and token_from_url:
        st.session_state["authenticated"] = True
        st.session_state["auth_token"] = token_from_url
        return True

    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.text_input(label="Username", key="user", on_change=creds_entered)
        st.text_input(label="Password", type="password", key="password", on_change=creds_entered)
        if st.button("Login"):
            creds_entered()
        return False
    else:
        st.toast("You are authenticated!", icon="✅")
        return True

def logout():
    st.session_state.clear()
    st.query_params.clear()  # clear URL params
    st.rerun()

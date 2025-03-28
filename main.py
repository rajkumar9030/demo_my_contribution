import streamlit as st
import pandas as pd
import sqlite3
import os
from email_utils import send_mail
import matplotlib.pyplot as plt

# DB connection
def get_connection():
    return sqlite3.connect('database.db', check_same_thread=False)

def fetch_resources():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM resources", conn)
    conn.close()
    return df

def update_resources(new_data):
    conn = get_connection()
    for res, qty in new_data.items():
        conn.execute("UPDATE resources SET quantity = ? WHERE resource = ?", (qty, res))
    conn.commit()
    conn.close()

# Apply custom styling
st.set_page_config(page_title="Resource Manager", layout="centered")
st.markdown('<style>' + open('styles.css').read() + '</style>', unsafe_allow_html=True)

# Email history list
if 'email_history' not in st.session_state:
    st.session_state.email_history = []

def home():
    st.title("🌱 Resource Optimization System")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Resource Update", use_container_width=True):
            st.session_state.page = "update"
    with col2:
        if st.button("📊 Resource Optimizer", use_container_width=True):
            st.session_state.page = "manager"

def resource_update():
    st.title("🔄 Update Resources")
    df = fetch_resources()
    st.dataframe(df, use_container_width=True)
    
    with st.form("update_form"):
        new_data = {}
        for _, row in df.iterrows():
            qty = st.number_input(f"Enter new quantity for {row['resource']}", value=int(row['quantity']), min_value=0)
            new_data[row['resource']] = qty
        if st.form_submit_button("✅ Update", use_container_width=True):
            update_resources(new_data)
            st.success("Resources updated successfully!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "home"

def resource_manager():
    st.title("📊 Resource Optimizer")
    df = fetch_resources()
    st.dataframe(df, use_container_width=True)

    # Dynamic email input
    st.subheader("📩 Manager Email Configuration")
    fertilizer_pesticide_seed_email = st.text_input("Enter Email for Fertilizer, Pesticides & Seeds")
    machinery_labour_email = st.text_input("Enter Email for Machinery & Labour")

    # Additional sender details
    st.subheader("📌 Your Contact Details")
    sender_name = st.text_input("Your Name")
    sender_mobile = st.text_input("Your Mobile Number")
    sender_colony = st.text_input("Your Colony")

    with st.form("require_form"):
        required = {}
        for _, row in df.iterrows():
            required_qty = st.number_input(f"Enter required {row['resource']} quantity", min_value=0)
            required[row['resource']] = required_qty
        submitted = st.form_submit_button("Submit", use_container_width=True)

    if submitted:
        shortages_fertilizer = {}
        shortages_machinery = {}

        for _, row in df.iterrows():
            shortfall = required[row['resource']] - row['quantity']
            if shortfall > 0:
                if row['resource'] in ["Fertilizer (kg)", "Pesticides (liters)", "Seeds (kg)"]:
                    shortages_fertilizer[row['resource']] = shortfall
                elif row['resource'] in ["Machinery (units)", "Labour (workers)"]:
                    shortages_machinery[row['resource']] = shortfall

        sender_info = f"\n\nBest Regards,\n{sender_name}\n📞 {sender_mobile}\n🏡 {sender_colony}"

        if shortages_fertilizer and fertilizer_pesticide_seed_email:
            email_subject = "🚨 Shortage Alert: Fertilizer, Pesticides & Seeds"
            email_body = "Dear Manager,\n\nThe following resources are running low:\n"
            email_body += "\n".join([f"🔹 {res}: Need {qty} more" for res, qty in shortages_fertilizer.items()])
            email_body += sender_info
            response = send_mail(email_subject, email_body, fertilizer_pesticide_seed_email)
            st.session_state.email_history.append(f"Sent to {fertilizer_pesticide_seed_email}: {email_subject}")
            st.info(response)

        if shortages_machinery and machinery_labour_email:
            email_subject = "🚨 Shortage Alert: Machinery & Labour"
            email_body = "Dear Manager,\n\nThe following resources are running low:\n\n"
            email_body += "\n".join([f"🔹 {res}: Need {qty} more" for res, qty in shortages_machinery.items()])
            email_body += sender_info
            response = send_mail(email_subject, email_body, machinery_labour_email)
            st.session_state.email_history.append(f"Sent to {machinery_labour_email}: {email_subject}")
            st.info(response)

        if not shortages_fertilizer and not shortages_machinery:
            st.success("✅ All resources are sufficient.")

    # Show email history
    st.subheader("📨 Sent Emails")
    if st.session_state.email_history:
        for email in st.session_state.email_history:
            st.write(email)
    else:
        st.write("No emails sent yet.")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("📈 Show Visualization", use_container_width=True):
        visualize(df, required)
    
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "home"

def visualize(available, requested):
    if not requested:
        st.warning("No requested data to visualize")
        return
    
    resources = available['resource'].tolist()
    available_qty = available['quantity'].tolist()
    requested_qty = [requested[res] for res in resources]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    bar_width = 0.35
    index = range(len(resources))
    
    ax.bar(index, available_qty, bar_width, label='Available', color='green')
    ax.bar([i + bar_width for i in index], requested_qty, bar_width, label='Requested', color='red')
    
    ax.set_xlabel('Resources')
    ax.set_ylabel('Quantity')
    ax.set_title('Available vs Requested Resources')
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(resources)
    ax.legend()
    
    st.pyplot(fig)

# App flow control
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if st.session_state.page == "home":
    home()
elif st.session_state.page == "update":
    resource_update()
elif st.session_state.page == "manager":
    resource_manager()

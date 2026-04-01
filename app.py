import streamlit as st
import pandas as pd
import datetime
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Work-Gratitude Management", layout="wide")

# Mock Database (In a real app, link this to Supabase/SQL)
if 'db' not in st.session_state:
    st.session_state.db = {
        "employees": {
            "E001": {"name": "Mithra", "monthly": 15000, "hours": 12, "role": "Admin", "rating": 5.0},
            "E002": {"name": "Staff_A", "monthly": 12000, "hours": 10, "role": "Employee", "rating": 4.8}
        },
        "attendance": [] # Stores: id, date, login_time, approved, location
    }

# --- LOGIC FUNCTIONS ---
def get_per_minute_rate(monthly, shift_hours):
    daily = monthly / 30
    working_mins = (shift_hours * 60) - 40 # Minus 40m lunch
    return daily / working_mins

# --- UI ---
st.title("🙏 Employee Gratitude & Salary Meter")

sidebar = st.sidebar
user_id = sidebar.text_input("Enter Employee ID (e.g., E001)", value="E001")
role = st.session_state.db["employees"][user_id]["role"]

if role == "Admin":
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Approvals", "Marketplace"])
else:
    tab1, tab2 = st.tabs(["My Clock-In", "Marketplace"])

# --- TAB 1: ATTENDANCE & METER ---
with tab1:
    emp = st.session_state.db["employees"][user_id]
    st.header(f"Welcome, {emp['name']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Clock-In Action")
        img_file = st.camera_input("Facial Recognition Login")
        location = st.text_input("Current Location (GPS Data)")
        
        if st.button("Submit for Approval") and img_file:
            st.session_state.db["attendance"].append({
                "id": user_id,
                "time": datetime.datetime.now(),
                "status": "Pending",
                "loc": location
            })
            st.warning("Login submitted. Waiting for Manager approval.")

    with col2:
        st.subheader("💰 Live Earnings Meter")
        rpm = get_per_minute_rate(emp['monthly'], emp['hours'])
        
        # Simulated "Ticking" Placeholder
        placeholder = st.empty()
        
        # Check if approved for today
        is_approved = any(a['id'] == user_id and a['status'] == "Approved" for a in st.session_state.db["attendance"])
        
        if is_approved:
            while True:
                # Calculate progress since 9 AM (for demo purposes)
                now = datetime.datetime.now()
                start_time = now.replace(hour=9, minute=0, second=0)
                elapsed_mins = max(0, (now - start_time).total_seconds() / 60)
                earned = elapsed_mins * rpm
                
                placeholder.metric(
                    label="Current Daily Investment", 
                    value=f"₹{earned:.4f}", 
                    delta=f"{rpm:.5f} per min"
                )
                time.sleep(1) # Updates every second
        else:
            st.info("Meter starts ticking once Manager approves your login.")

# --- TAB 2: ADMIN APPROVALS ---
if role == "Admin":
    with tab2:
        st.header("Pending Approvals")
        for i, entry in enumerate(st.session_state.db["attendance"]):
            if entry["status"] == "Pending":
                st.write(f"User: {entry['id']} | Time: {entry['time']} | Loc: {entry['loc']}")
                if st.button(f"Approve {entry['id']}", key=i):
                    st.session_state.db["attendance"][i]["status"] = "Approved"
                    st.rerun()

# --- TAB 3: MARKETPLACE & RATINGS ---
with tab3:
    st.header("Service Marketplace")
    for eid, data in st.session_state.db["employees"].items():
        with st.expander(f"{data['name']} - Rating: {'⭐'*int(data['rating'])}"):
            st.write(f"Available for {data['hours']} hour shifts.")
            if st.button(f"Request Service from {data['name']}"):
                st.success("Request sent to Employee calendar!")

import streamlit as st
import pandas as pd

# Dummy data for demonstration
def get_user_data():
    return pd.DataFrame({
        "Email": ["user1@test.com", "user2@test.com", "organizer1@test.com"],
        "Role": ["User", "User", "Organizer"]
    })

def admin_main():
    st.header("Admin Dashboard")
    st.subheader("User Management")

    users_df = get_user_data()
    st.dataframe(users_df)

    st.subheader("Assign Seminar Organizer")
    user_to_promote = st.selectbox("Select User to make Organizer", users_df[users_df['Role'] == 'User']['Email'])
    if st.button("Promote to Organizer"):
        # In a real app, you would update the user's role in the database
        st.success(f"{user_to_promote} has been promoted to Organizer.")
    
    st.subheader("Add WhatsApp Link to Seminar")
    seminar_name = st.text_input("Seminar Name for WhatsApp Link")
    whatsapp_link = st.text_input("WhatsApp Group Link")
    if st.button("Add WhatsApp Link"):
        # In a real app, you'd save this to your seminar data
        st.success(f"WhatsApp link added for {seminar_name}.")

import streamlit as st
import bcrypt
import pymysql as sql
from streamlit_option_menu import option_menu

# Database connection
def connection():
    return sql.connect(
        host='localhost',
        user='root',
        password='secret',
        database='attendance_system'
    )

# Function to add a new user (Signup)
def add_user(username, password):
    conn = connection()
    cur = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_pw.decode('utf-8')))
        conn.commit()
        conn.close()
        return True
    except sql.IntegrityError:
        conn.close()
        return False

# Function to authenticate a user (Login)
def authenticate_user(username, password):
    conn = connection()
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cur.fetchone()
    conn.close()
    if result:
        return bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8'))
    return False

# Function to check if a username already exists
def username_exists(username):
    conn = connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    result = cur.fetchone()
    conn.close()
    return bool(result)

# Pages
def signup_page():
    st.subheader("Create a New Account")
    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Signup"):
        if password == confirm_password:
            if username_exists(username):
                st.warning("Username already exists. Please choose a different username.")
            else:
                if add_user(username, password):
                    st.success("Account created successfully!")
                    # Redirect to login page
                    if st.button("Go to Login"):
                        st.session_state.page = "login"
                else:
                    st.error("Error creating account. Please try again later.")
        else:
            st.error("Passwords do not match!")

def login_page():
    st.subheader("Login to Your Account")
    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        if authenticate_user(username, password):
            st.success(f"Welcome, {username}!")
            # Button to redirect to an external web URL
            dashboard_url = "https://example.com/dashboard"  # Replace with your desired URL
            st.markdown(
                f'<a href="{dashboard_url}" target="_blank"><button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-align:center;">Go to Dashboard</button></a>',
                unsafe_allow_html=True,
            )
        else:
            st.error("Invalid username or password. Please try again.")


def dashboard_page():
    st.subheader("Dashboard")
    st.write(f"Welcome to the Student Attendance Management System, {st.session_state.username}!")
    if st.button("Logout"):
        # Redirect back to login page
        st.session_state.page = "login"

# Main function
def main():
    st.title("Student Attendance Management System")

    # Initialize session state for page navigation
    if "page" not in st.session_state:
        st.session_state.page = "login"

    # Handle navigation
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "signup":
        signup_page()
    elif st.session_state.page == "dashboard":
        dashboard_page()

    # Sidebar navigation with option menu
    selected = option_menu(
        menu_title=None,  # Hide the menu title
        options=["Login", "Signup"],  # Menu options
        icons=["box-arrow-in-right", "person-plus"],  # Icon names
        menu_icon="menu-button",  # Icon for the menu
        default_index=0 if st.session_state.page == "login" else 1,  # Default index
        orientation="horizontal",  # Horizontal menu
    )

    # Update the session state based on the menu selection
    if selected == "Login":
        st.session_state.page = "login"
    elif selected == "Signup":
        st.session_state.page = "signup"

if __name__ == "__main__":
    main()

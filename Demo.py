import streamlit as st
import pandas as pd


def main():
    st.title("Student Attendance Management System")

    # Section: College Information
    st.subheader("College Information")
    with st.form("college_info_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            country = st.selectbox("Country", ["India", "USA", "UK"])
            board = st.selectbox("Board", ["CBSE", "ICSE", "State Board"])
            class_name = st.selectbox("Class Name", ["10", "11", "12"])
        with col2:
            city = st.selectbox("City", ["Nagpur", "Mumbai", "Pune"])
            medium = st.selectbox("Medium", ["English", "Hindi"])
            section_name = st.selectbox("Section Name", ["A", "B", "C"])
        with col3:
            college_name = st.text_input("College Name", "CPS")
            academic_year = st.selectbox("Academic Year", ["2022-2023", "2023-2024", "2024-2025"])
            staff_name = st.text_input("Staff Name", "Raka Raks")

        # Date Input
        date = st.date_input("Date")

        # Submit Search
        search_button = st.form_submit_button("Search")

    # Placeholder for table (Simulate search result)
    if search_button:
        st.success("Search results loaded successfully.")
        # Mock data
        data = {
            "Sr No": [1, 2],
            "Enrollment": ["201500012", "201500013"],
            "First Name": ["Jawwad", "Ahnaf"],
            "Last Name": ["Ali", "Khan"],
            "Attendance": [True, False],
            "Comment": ["Present", "Absent"]
        }
        df = pd.DataFrame(data)

        # Display table with editing options
        st.subheader("Attendance Table")
        edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    # Save Button
    st.subheader("")
    if st.button("Save"):
        st.success("Attendance records saved successfully!")


if __name__ == "__main__":
    main()

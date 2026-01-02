from st_aggrid import AgGrid
import pymysql as sql
import streamlit as st
import pandas as pd

def mysqlconnect():
    # Connect to the MySQL database
    conn = sql.connect(
        host='localhost',
        user='root',
        password="secret",
        db='attendance_system',
    )
    return conn

def fetch_data():
    conn = mysqlconnect()
    query = "SELECT * FROM students;"
    try:
        # Fetch data from the MySQL table
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        conn.close()
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()  # Return empty DataFrame in case of error

def main():
    st.title("Student Records in Interactive Grid")

    # Fetch data from the database
    data = fetch_data()

    if not data.empty:
        st.subheader("Interactive Grid View")
        # Display the data using AgGrid
        AgGrid(
            data,
            editable=False,
            sortable=True,
            filter=True,
            resizable=True,
            fit_columns_on_grid_load=True,
            theme="streamlit"  # Other themes: "streamlit", "light", "dark"
        )
    else:
        st.warning("No data available in the table!")

if __name__ == "__main__":
    main()

# import pymysql
#
#
# def mysqlconnect():
#     # To connect MySQL database
#     conn = pymysql.connect(
#         host='localhost',
#         user='root',
#         password="secret",
#         db='attendance_system',
#     )
#
#     cur = conn.cursor()
#     cur.execute("select @@version")
#     cur.execute("SHOW DATABASES")
#     cur.execute("SHOW TABLES")
#     cur.execute("SELECT * FROM USERS")
#     output = cur.fetchall()
#     print(output)
#
#     # To close the connection
#     conn.close()
#
#
# # Driver Code
# if __name__ == "__main__":
#     mysqlconnect()








# def main():
#     st.title("Student Records")
#
#     # Fetch and display the data
#     st.subheader("Students Table")
#     data = get_students()
#     if not data.empty:
#         st.dataframe(data)
#     else:
#         st.warning("No data available in the table!")




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

def display_grid(data):
    st.subheader("Students Grid Layout")
    for index, row in data.iterrows():
        cols = st.columns(4)  # Adjust number of columns in the grid
        cols[0].write(f"ID : {row[0]}")
        cols[1].write(f"Name : {row[1]}")
        cols[2].write(f"Gender : {row[2]}")
        cols[3].write(f"Department : {row[3]}")
        # cols[0].write(f"ID: {row['']}")
        # cols[1].write(f"Name: {row['name']}")
        # cols[2].write(f"Gender: {row['gender']}")
        # cols[3].write(f"Department: {row['department']}")

def main():
    st.title("Student Records in Grid")

    # Fetch and display the data
    data = fetch_data()
    if not data.empty:
        display_grid(data)
    else:
        st.warning("No data available in the table!")

if __name__ == "__main__":
    main()

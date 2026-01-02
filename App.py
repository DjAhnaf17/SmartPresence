import openpyxl
import pandas as pd
import base64
import datetime
from datetime import datetime
from flask import Flask, render_template, redirect, request, jsonify, flash, session, url_for
from flask import send_file
import pymysql as sql
from functools import wraps
import os
import time
ATTENDANCE_FOLDER = 'Attendance Records'
if not os.path.exists(ATTENDANCE_FOLDER):
    os.makedirs(ATTENDANCE_FOLDER)
    
# Set the templates folder
template = 'template/'
app = Flask(__name__, template_folder=template)
app.secret_key = 'secret'

# Database connection function
def get_db_connection():
    try:
        connection = sql.connect(
            host='localhost',
            user='root',
            password='secret',  # Replace with your DB password
            database='attendance_system'
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return None

# Login Required Decorator
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:  # Check if user is logged in
                flash('You need to log in first.', 'warning')
                return redirect(url_for('login'))
            if role and session.get('role') != role:  # Check role if specified
                flash('Unauthorized access!', 'danger')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Route: Home Page
@app.route('/')
def home():
    return render_template('mainIndex.html')




# Login Page for all users
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  # 'student', 'staff', 'admin'

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            if role == 'student':
                query = "SELECT * FROM student_login WHERE username = %s AND password = %s"
            elif role == 'staff':
                query = "SELECT * FROM staff_login WHERE username = %s AND password = %s"
            elif role == 'admin':
                query = "SELECT * FROM admin_login WHERE username = %s AND password = %s"
            else:
                flash('Invalid role selected!', 'danger')
                return redirect(url_for('login'))

            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            if user:
                session['username'] = user[0]
                session['role'] = role  # Store role in session
                flash(f'{role.capitalize()} login successful!', 'success')
                if role == 'student':
                    return redirect(url_for('student_dashboard'))
                elif role == 'staff':
                    return redirect(url_for('staff_dashboard'))
                elif role == 'admin':
                    return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid username or password!', 'danger')
        except Exception as e:
            print(f"Error: {e}")
            flash('An error occurred. Please try again later.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')


# Logout Route
@app.route('/logout')
@login_required()
def logout():
    session.clear()  # Clear session
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Student Dashboard
@app.route('/student_dashboard')
@login_required(role='student')
def student_dashboard():
    return render_template('student_dashboard.html', username=session['username'])

@app.route('/attendance_sheet')
@login_required(role='student')
def attendance_sheet():
    return render_template('attendance_sheet.html', username=session['username'])


# @app.route('/student_profile')
# @login_required(role='student')
# def student_profile():
#     if 'username' in session:  # Ensure 'username' is stored in the session during login
#         username = session['username']
#         conn = get_db_connection()
#         cursor = conn.cursor(sql.cursors.DictCursor)

#         try:
#             # Fetch student details from the Students table using the username
#             cursor.execute("SELECT * FROM students WHERE username = %s", (username,))
#             profile_data = cursor.fetchone()
            
#             if not profile_data:
#                 flash("Profile details not found!", "warning")
#                 return redirect(url_for('student_dashboard'))
            
#             return render_template('student_profile.html', profile_data=profile_data)
#         except Exception as e:
#             print(f"Error: {e}")
#             flash("An error occurred while fetching profile details.", "danger")
#             return redirect(url_for('student_dashboard'))
#         finally:
#             cursor.close()
#             conn.close()
#     else:
#         flash("Unauthorized access!", "danger")
#         return redirect(url_for('login'))



@app.route('/student_profile')
@login_required(role='student')
def student_profile():
    if 'username' in session:
        username = session['username']
        conn = get_db_connection()
        cursor = conn.cursor(sql.cursors.DictCursor)

        try:
            # Fetch student details including photo
            cursor.execute("SELECT roll, username, name, gender, department, class, address, mobileno, bloodgroup, TO_BASE64(photo) AS photo FROM Students WHERE username = %s", (username,))
            profile_data = cursor.fetchone()

            if not profile_data:
                flash("Profile not found!", "warning")
                return redirect(url_for('student_dashboard'))

            return render_template('student_profile.html', profile_data=profile_data)
        except Exception as e:
            print(f"Error: {e}")
            flash("An error occurred while fetching the profile.", "danger")
            return redirect(url_for('student_dashboard'))
        finally:
            cursor.close()
            conn.close()
    else:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))


@app.route('/theory_attendance')
@login_required(role='student')
def theory_attendance():
    return send_file('static/practical_attendance.pdf', as_attachment=False) 


@app.route('/practical_attendance')
def practical_attendance():
    return send_file('static/practical_attendance.pdf', as_attachment=False)

@app.route('/timetable')
def timetable():
    return send_file('static/Time Table.pdf', as_attachment=False)







# Staff Dashboard
@app.route('/staff_dashboard')
@login_required(role='staff')
def staff_dashboard():
    
    username = session['username']
    conn = None
    try:
        # Establish database connection
        conn = get_db_connection()
        with conn.cursor(sql.cursors.DictCursor) as cursor:
    
            query_staff = """
                SELECT s.class, s.department, s.subject, s.photo
                FROM staffs AS s
                WHERE s.username = %s
            """        
            photo_data = None
            
            cursor.execute(query_staff, (username,))
            staff = cursor.fetchone()
            if not staff:
                flash("Staff details not found.", "danger")
                return redirect('/staff_dashboard')
            
            if staff and staff.get('photo'):
                photo_data = base64.b64encode(staff['photo']).decode('utf-8')
            
            
            staff_class = staff['class']
            staff_department = staff['department']
            staff_subject = staff['subject']
        return render_template(
            'staff_dashboard.html',
            username=username,
            staff_photo = photo_data,
            staff_dept = staff_department,
            staff_class=staff_class,
            staff_subject=staff_subject,
        )
    except Exception as e:
        print(f"Error: {e}")  # Log for debugging
        flash("An error occurred while processing your request.", "danger")
        return redirect('/staff_dashboard')

    finally:
        if conn:
            conn.close()
        
        
    return render_template('staff_dashboard.html', username=session['username'])

def get_attendance_filename():
    # Get the current date in YYYY-MM-DD format
    today_date = datetime.today().strftime('%Y-%m-%d')
    return os.path.join(ATTENDANCE_FOLDER, f'attendance_{today_date}.csv')


import pywhatkit as kit


@app.route('/attendance_mark', methods=['GET', 'POST'])
@login_required(role='staff')
def attendance_mark():
    username = session.get('username')
    if not username:
        flash("You need to log in first.", "danger")
        return redirect('/login')


    conn = get_db_connection()
    try:
        with conn.cursor(sql.cursors.DictCursor) as cursor:
            # Fetch staff details
            cursor.execute("""
                SELECT name,class, department, subject, photo FROM staffs WHERE username = %s
            """, (username,))
            staff = cursor.fetchone()
            if not staff:
                flash("Staff details not found.", "danger")
                return redirect('/staff_dashboard')

            staff_name,staff_class, staff_department, staff_subject = staff['name'],staff['class'], staff['department'], staff['subject']
            staff_photo = base64.b64encode(staff['photo']).decode('utf-8') if staff.get('photo') else None

            # Fetch students from the class
            cursor.execute("""
                SELECT roll, name, mobileno FROM Students WHERE class = %s AND department = %s
            """, (staff_class, staff_department))
            students = cursor.fetchall()

        if request.method == 'POST':
            hour = request.form['hour']
            current_date = datetime.now().strftime('%Y-%m-%d')
            attendance_data = []
            absentees = []

            for student in students:
                roll = student['roll']
                status = request.form.get(f'attendance_{roll}', 'Absent')
                attendance_data.append((roll, student['name'], hour, status, current_date))

                if status == 'Absent':
                    absentees.append((student['mobileno'], student['name']))

            # Save attendance to database
            with conn.cursor() as cursor:
                cursor.executemany("""
                    INSERT INTO student_attendance (student_id, student_name, hour, status, attendance_date)
                    VALUES (%s, %s, %s, %s, %s)
                """, attendance_data)
                conn.commit()

            # Send WhatsApp messages to absentees only
            for mobile, name in absentees:
                message = f"Dear {name},\nYou were marked absent for {staff_subject} class on {current_date}, Hour {hour}. Please catch up on the missed content."
                kit.sendwhatmsg_instantly(mobile, message)
                time.sleep(5)  # Delay to avoid API restrictions

            flash("Attendance marked successfully!", "success")
            return redirect('/attendance_mark')

        return render_template(
            'attendance_mark.html',
            username=username,
            students=students,
            staff_name = staff_name,
            staff_photo=staff_photo,
            staff_class=staff_class,
            staff_subject=staff_subject
        )

    except Exception as e:
        print(f"Error: {e}")
        flash("An error occurred while processing your request.", "danger")
        return redirect('/staff_dashboard')

    finally:
        conn.close()


# Staff Students List Route

@app.route('/staff_students_list')
@login_required(role='staff')
def staff_students_list():
    if 'username' in session:
        username = session['username']  # Get username from session
        conn = get_db_connection()
        cursor = conn.cursor(sql.cursors.DictCursor)

        try:
            # Fetch staff details
            cursor.execute("""
                SELECT name, class, department, subject, photo 
                FROM staffs 
                WHERE username = %s
            """, (username,))
            staff = cursor.fetchone()

            if not staff:
                flash("Staff details not found!", "warning")
                return redirect(url_for('staff_dashboard'))

            # Extract staff details
            staff_name = staff['name']
            staff_class = staff['class']
            staff_department = staff['department']
            staff_subject = staff['subject']
            staff_photo = base64.b64encode(staff['photo']).decode('utf-8') if staff.get('photo') else None

            # Fetch all students in the staff's class and department
            cursor.execute("""
                SELECT roll, name, username, gender, department, class, address, mobileno, bloodgroup, photo 
                FROM Students 
                WHERE class = %s AND department = %s
            """, (staff_class, staff_department))
            students = cursor.fetchall()

            # Convert student photos to base64
            for student in students:
                if student.get('photo'):
                    student['photo'] = base64.b64encode(student['photo']).decode('utf-8')

            # Render the template with all required data
            return render_template(
                'staff_students_list.html',
                username=username,
                students=students,
                staff_name=staff_name,
                staff_photo=staff_photo,
                staff_class=staff_class,
                staff_subject=staff_subject
            )

        except Exception as e:
            print(f"Error: {e}")
            flash("An error occurred while processing your request.", "danger")
            return redirect(url_for('staff_dashboard'))

        finally:
            cursor.close()
            conn.close()
    else:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))



@app.route('/student_details/<int:roll>')
@login_required(role='staff')
def student_details(roll):
    if 'username' in session:
        username = session['username']  # Get username from session
        conn = get_db_connection()
        cursor = conn.cursor(sql.cursors.DictCursor)

        try:
            # Fetch student details including photo
            cursor.execute("""
                SELECT roll, username, name, gender, department, class, address, mobileno, bloodgroup, photo 
                FROM Students 
                WHERE roll = %s
            """, (roll,))
            student = cursor.fetchone()

            if not student:
                flash("Student details not found!", "warning")
                return redirect(url_for('staff_students_list'))

            # Convert photo to base64
            if student.get('photo'):
                student['photo'] = base64.b64encode(student['photo']).decode('utf-8')

            # Render the template with student details
            return render_template(
                'student_details.html',
                username=username,
                student=student
            )

        except Exception as e:
            print(f"Error: {e}")
            flash("An error occurred while fetching the student details.", "danger")
            return redirect(url_for('staff_students_list'))

        finally:
            cursor.close()
            conn.close()
    else:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))



@app.route('/staff_profile')
@login_required(role='staff')
def staff_profile():
    if 'username' in session:
        username = session['username']
        conn = get_db_connection()
        cursor = conn.cursor(sql.cursors.DictCursor)

        try:
            # Fetch student details including photo
            cursor.execute("SELECT id,name,username, email, subject, code , department, class, role, mobileno , TO_BASE64(photo) AS photo FROM staffs WHERE username = %s", (username,))
            profile_data = cursor.fetchone()

            if not profile_data:
                flash("Profile not found!", "warning")
                return redirect(url_for('staff_dashboard'))

            return render_template('staff_profile.html', profile_data=profile_data)
        except Exception as e:
            print(f"Error: {e}")
            flash("An error occurred while fetching the profile.", "danger")
            return redirect(url_for('staff_dashboard'))
        finally:
            cursor.close()
            conn.close()
    else:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))

# Admin Dashboard
@app.route('/admin_dashboard')
@login_required(role='admin')
def admin_dashboard():
    return render_template('admin_dashboard.html', username=session['username'])

# Student Registration
@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query = "INSERT INTO student_login (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, email, password))
            conn.commit()
            flash('Student registered successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error: {e}")
            flash('An error occurred while registering. Please try again.', 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('register_student.html')

# Staff Registration
@app.route('/register_staff', methods=['GET', 'POST'])
def register_staff():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query = "INSERT INTO staff_login (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, email, password))
            conn.commit()
            flash('Staff registered successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error: {e}")
            flash('An error occurred while registering. Please try again.', 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('register_staff.html')

# Admin Registration
@app.route('/register_admin', methods=['GET', 'POST'])
@login_required(role='admin')  # Only admin can register another admin
def register_admin():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:


            query = "INSERT INTO admin_login (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, email, password))
            conn.commit()
            flash('Admin registered successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            print(f"Error: {e}")
            flash('An error occurred while registering. Please try again.', 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('register_admin.html')

# Run the application
if __name__ == '__main__':
    app.run(debug=True,host= '0.0.0.0')


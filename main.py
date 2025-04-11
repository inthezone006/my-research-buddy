# Database Design (name: research_buddy)
# accounts (Holds all accounts) - unique_index[username, password], index[id]
# (PK, INT) id
# (NOT NULL, UNIQUE, VARCHAR(35)) username
# (NOT NULL, VARCHAR(35)) password
# (NOT NULL, VARCHAR(35)) first
# (NOT NULL, VARCHAR(35)) last
# (NOT NULL, VARCHAR(35)) email 
# (VARCHAR(35)) resume
# (VARCHAR(35)) linkedin
# (NOT NULL, FK departments_id REFERENCES departments.id, INT) department_id
# (NOT NULL, CONSTRAINT CHK_STATUS CHECK (status='admin' OR status='professor' OR status='student'), VARCHAR(9)) status
#
# admin (Has master control over accounts, projects, and departments) - 
# (PK, FK admin_id REFERENCES accounts.id, INT) id
# 
# professors (Puts up projects) - index[id]
# (PK, FK professor_id REFERENCES accounts.id, INT) id
# (VARCHAR(35)) website
# (NOT NULL, CONSTRAINT CHK_STATUS CHECK (status='assistant' OR status='associate' OR status='full'), VARCHAR(9)) status
#
# students (Signs up for projects) - index[id]
# (PK, FK student_id REFERENCES accounts.id, INT) id
# (NOT NULL, CONSTRAINT CHK_STATUS CHECK (status='undergraduate' OR status='graduate'), VARCHAR(13)) status
# 
# departments (Holds all departments/majors) - index[id]
# (PK, INT) id
# (NOT NULL, UNIQUE, VARCHAR(35)) name
# 
# projects (Holds all projects) - index[id]
# (PK, INT) id
# (NOT NULL, UNIQUE, VARCHAR(35)) title
# (NOT NULL, VARCHAR(35)) description
# (NOT NULL, FK projects_department_id REFERENCES departments.id, INT) department_id
# (NOT NULL, VARCHAR(35)) link
# (NOT NULL, FK projects_professor_id REFERENCES professors.id, INT) professor_id
# (NOT NULL, CONSTRAINT CHK_STATUS CHECK (status='open' OR status='closed' OR status='paused'), VARCHAR(9)) status
# 
# projects_students (Holds all projects that a student is part of) - 
# (PK, FK projectsrel_student_id REFERENCES students.id, INT) student_id
# (PK, FK projectsrel_project_id REFERENCES projects.id, INT) project_id
# 
# status_codes - index[id]
# (PK, INT) id
# (NOT NULL, VARCHAR(35)) account
# (NOT NULL, INT) code
#
#
# TODO: User interface must populate data from the database dynamically (e.g., cannot just hardcode the data) 
# and must show in demo
# TODO: Use valid indices (with queries and must be meaningful with valid justification) and create index report
# TODO: Discussion of transactions, concurrent access to data, and choice of isolation levels
# TODO: Requirement 1: An interface that allows users to add, edit, and delete data in one main table (edit account)
# TODO: Requirement 2: A report interface that allows a user (admin) to select which data to 
# display in report (admin: report all users, professors: report all projects)

from flask import Flask, request, redirect, url_for, session
import mysql.connector
import json

with open('config.json') as config_file:
    db_config = json.load(config_file)

cnx = mysql.connector.connect(**db_config)
cursor = cnx.cursor()

app = Flask(__name__)
app.config.from_pyfile('config.py')

@app.route("/")
def main():
    return redirect(url_for('home'))

@app.route("/home")
def home():
    if 'id' in session:
        return redirect(url_for('dashboard'))
    
    else:
        return f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'> \
        <title>Research Buddy</title><main><h1>Home</h1><button onclick=\"window.location.href='/signin';\"> \
        Sign In</button> <button onclick=\"window.location.href='/signup';\">Create Account</button> \
        </main><footer>Research Buddy v1.0a</footer>"
    
@app.route("/signin", methods=['GET', 'POST'])    
def signin():
    if request.method == 'GET':
        return f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'><title>Sign In</title> \
        <main><div class='content-container'><h1>Sign In</h1><form method='POST'> Username: \
        <input type='text' maxlength='35' name='username' required><br><br>Password: \
        <input type='password' maxlength='35' name='password' required> \
        <br><br><div class='content-buttons'> \
        <button type='button' class='back-button' onclick=\"window.location.href='/home';\">Back</button> \
        <button type='submit'>Sign In</button></div></form></div></main><footer>Research Buddy v1.0a</footer>"
    
    elif request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        cursor.execute("CALL GetAccountByCredentials(%s, %s)", (username, password))
        response = cursor.fetchone()
        while cursor.nextset():
            pass

        if not response:
            return "<script>window.alert('Invalid username or password! Please try again.');" \
            "window.location.href = '/signin';</script>"
    
        session['id'] = response[0]
        session['username'] = response[1]
        session['password'] = response[2]
        session['first'] = response[3]
        session['last'] = response[4]
        session['email'] = response[5]
        session['resume'] = response[6]
        session['linkedin'] = response[7]
        session['department_id'] = response[8]
        session['status'] = response[9]


        return redirect(url_for('dashboard'))
    

@app.route("/signup", methods=['GET', 'POST'])    
def signup():
    if request.method == "GET":
        cursor.execute("CALL GetAllDepartmentNames()")
        responses = cursor.fetchall()

        while cursor.nextset(): 
            pass

        html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'><title>Sign Up</title>" \
        "<main><div class='content-container'><h1>Sign Up</h1><p>Fields marked with an asterisk (*) are required.</p>" \
        "<p>All fields have a character limit of 35.</p><form method='POST' onsubmit='return handleCodePrompt();'>" \
        "*Username: <input type='text' name='username' maxlength='35'><br><br>*Password: " \
        "<input type='password' name='password' maxlength='35' required>" \
        "<br><br>*Confirm password: <input type='password' name='password2' maxlength='35' required>" \
        "<br><br>*First name: <input type='text' name='first' maxlength='35' required>" \
        "<br><br>*Last name: <input type='text' name='last' maxlength='35' required>" \
        "<br><br>*Email: <input type='text' name='email' maxlength='35' required>" \
        "<br><br>Resume: <input type='text' maxlength='35' name='resume'>" \
        "<br><br>LinkedIn: <input type='text' maxlength='35' name='linkedin'>" \
        "<br><br>*Department: <select name='dpt' id='dpt' required>"

        for row in responses:
            html += f"<option value='{row[0]}'>{row[0]}</option>"

        html += f"</select><br><br>Account Type: <select name='account_type' id='account_type'>" \
        "<option value='admin'>Admin</option>" \
        "<option value='student'>Student</option><option value='professor'>Professor</option></select>" \
        "<br><br><div id='professor_fields' class='hidden'>Website: <input type='text' name='website' maxlength='35'>" \
        "<br><br>*Status: <select name='pstatus' id='pstatus'><option value='assistant'>Assistant</option>" \
        "<option value='associate'>Associate</option><option value='full'>Full</option></select></div>" \
        "<div id='student_fields' class='hidden'>*Status: <select name='sstatus' id='sstatus'>" \
        "<option value='undergraduate'>Undergraduate</option><option value='graduate'>Graduate</option></select>" \
        "</div><input type='hidden' name='secret_code' id='secret_code' value=''><div class='content-buttons'>" \
        "<button type='button' class='back-button' onclick=\"window.location.href='/home';\">Back</button> " \
        "<button type='submit'>Sign Up</button></div></form></div></main><footer>Research Buddy v1.0a</footer>" \
        "<script>document.getElementById('account_type').addEventListener('change', function(){" \
        "var type = this.value;var professorFields = document.getElementById('professor_fields');" \
        "var studentFields = document.getElementById('student_fields');if(type === 'professor'){" \
        "professorFields.classList.remove('hidden');studentFields.classList.add('hidden');} " \
        "else if (type === 'student') {studentFields.classList.remove('hidden');" \
        "professorFields.classList.add('hidden');} else {professorFields.classList.add('hidden');" \
        "studentFields.classList.add('hidden');}});function handleCodePrompt() {{var code = prompt('" \
        "Please enter the status code for this account');if(code !== null && code.trim() !== '') {{" \
        "document.getElementById('secret_code').value = code;return true;}} return false;}}</script>"

        return html
    
    elif request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        first = request.form.get('first')
        last = request.form.get('last')
        email = request.form.get('email')
        resume = request.form.get('resume')
        linkedin = request.form.get('linkedin')
        department = request.form.get('dpt')
        account_type = request.form.get('account_type')

        if password != password2:
            return "<script>window.alert('Passwords do not match! Please try again.');" \
            "window.location.href = '/signup';</script>"
        
        if '@' not in email or '.' not in email:
            return "<script>window.alert('Invalid email! Please try again.');" \
            "window.location.href = '/signup';</script>"
        
        secret_code = int(request.form.get('secret_code', ''))
        query = "SELECT code FROM status_codes WHERE account = %s"
        cursor.execute(query, (account_type,))
        response = cursor.fetchone()[0]
        if secret_code != response:
            return "<script>window.alert('Invalid code! Please try again.');" \
            "window.location.href = '/signup';</script>"
        
        cursor.execute("SELECT id FROM departments WHERE name = %s", (department,))
        dept_id = cursor.fetchone()[0]
        
        insert_account = "INSERT INTO accounts (username, password, first, last, email, resume, linkedin, " \
        "department_id, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        cursor.execute(insert_account, (username, password, first, last, email, resume, linkedin, dept_id, 
                                        account_type))
        cnx.commit()

        new_id = cursor.lastrowid
        
        if account_type == "admin":
            cursor.execute("INSERT INTO admin (id) VALUES (%s)", (new_id,))
            cnx.commit()
        elif account_type == "professor":
            website = request.form.get('website')
            pstatus = request.form.get('pstatus')
            cursor.execute("INSERT INTO professors (id, website, status) VALUES (%s, %s, %s)", (new_id, website, pstatus))
            cnx.commit()
        elif account_type == "student":
            sstatus = request.form.get('sstatus')
            cursor.execute("INSERT INTO students (id, status) VALUES (%s, %s)", (new_id, sstatus))
            cnx.commit()

        return "<script>window.alert('Account created successfully!');window.location.href = '/home';</script>"

@app.route("/dashboard")    
def dashboard():
    if 'id' in session:
        status_buttons = ""
        if session['status'] == 'admin':
            status_buttons = "<div class='flex-container'><div class='flex-item'><fieldset class='fieldset-style'>" \
            "<legend>View:</legend><button class='btn-view' onclick=\"window.location.href='/accounts';\">" \
            "Accounts Report</button><br><br>" \
            "<button class='btn-view' onclick=\"window.location.href='/departments';\">" \
            "Departments Report</button><br><br>" \
            "<button class='btn-view' onclick=\"window.location.href='/projects';\">" \
            "Projects Report</button><br><br" \
            "><button class='btn-view' onclick=\"window.location.href='/status-codes';\">Status Codes Report</button>" \
            "<br><br></fieldset></div><div class='flex-item'><fieldset class='fieldset-style'>" \
            "<legend>Edit:</legend><button class='btn-edit' onclick=\"window.location.href='/edit/departments';\">" \
            "Departments</button><br><br><button class='btn-edit' onclick=\"window.location.href='/edit/projects';\">" \
            "Projects</button><br><br>" \
            "<button class='btn-edit' onclick=\"window.location.href='/edit/status-codes';\">Status Codes</button>" \
            "<br><br></fieldset></div><div class='flex-item'><fieldset class='fieldset-style'><legend>Account:" \
            "</legend><button class='btn-account' onclick=\"window.location.href='/edit';\">Account Settings</button>" \
            "<br><br><button class='back-button' onclick=\"window.location.href='/logout';\">Sign Out</button>" \
            "</fieldset></div></div><br><br>"

        elif session['status'] == 'professor':
            status_buttons = "<div class='flex-container'><div class='flex-item'>" \
            "<fieldset class='fieldset-style custom-fieldset'><legend>View:</legend>" \
            "<button class='btn-view' onclick=\"window.location.href='/projects';\">Projects Report</button><br><br> " \
            "<button class='btn-view' onclick=\"window.location.href='/profile';\">Profile Report</button> " \
            "</fieldset></div><div class='flex-item'><fieldset class='fieldset-style custom-fieldset'>" \
            "<legend>Edit:</legend><button class='btn-edit' onclick=\"window.location.href='/edit/projects';\">" \
            "Owned Projects</button><br><br>" \
            "<button class='btn-edit' onclick=\"window.location.href='/new/projects';\">Create New Project</button>" \
            "</fieldset></div><div class='flex-item'><fieldset class='fieldset-style custom-fieldset'><legend>" \
            "Account:</legend><button class='btn-account' onclick=\"window.location.href='/edit';\">" \
            "Account Settings</button><br><br><button class='back-button' onclick=\"window.location.href='/logout';\">" \
            "Sign Out</button></fieldset></div></div><br><br>"
        
        elif session['status'] == 'student':
            status_buttons = "<div class='flex-container'><div class='flex-item'>" \
            "<fieldset class='fieldset-style custom-fieldset'><legend>View:</legend>" \
            "<button class='btn-view' onclick=\"window.location.href='/projects';\">Projects Report</button><br><br> " \
            "<button class='btn-view' onclick=\"window.location.href='/profile';\">Profile Report</button> " \
            "</fieldset></div><div class='flex-item'><fieldset class='fieldset-style custom-fieldset'>" \
            "<legend>Edit:</legend><button class='btn-edit' onclick=\"window.location.href='/edit/projects';\">" \
            "Current Projects</button><br><br>" \
            "<button class='btn-edit' onclick=\"window.location.href='/new/projects';\">Join New Project</button>" \
            "</fieldset></div><div class='flex-item'><fieldset class='fieldset-style custom-fieldset'>" \
            "<legend>Account:</legend><button class='btn-account' onclick=\"window.location.href='/edit';\">" \
            "Account Settings</button><br><br>" \
            "<button class='back-button' onclick=\"window.location.href='/logout';\">Sign Out</button>" \
            "</fieldset></div></div><br><br>"

        return f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'><title>Dashboard</title> \
        <main><h1>Dashboard</h1><p>Welcome, {session['first']} {session['last']}!</p> {status_buttons} </main> \
        <footer>Account Status: {session['status'].capitalize()}</footer>"
    
    else:
        return redirect(url_for('home'))

@app.route("/profile", methods=['GET', 'POST'])
def view_profile():
    if session['status'] == 'student' or session['status'] == 'professor':
        if request.method == "GET":
            html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'> \
            <title>Profile Report</title><body><main><div class='viewer-container'><h1>Profile Report</h1> \
            <p>Use Ctrl + Click on Windows (or ⌘ + Click on Mac) to select multiple options.</p> \
            <form method='POST'><select name='scode' id='scode' multiple><option value='a.username'>Username \
            </option><option value='a.password'>Password</option> \
            <option value='a.first'>First Name</option><option value='a.last'>Last Name</option> \
            <option value='a.email'>Email</option><option value='a.resume'>Resume</option> \
            <option value='a.linkedin'>LinkedIn</option><option value='d.name'>Department</option> \
            <option value='a.status'>Account Status</option>"

            if session['status'] == 'professor':
                html += "<option value='p.website'>Website</option><option value='p.status'>Professor Status</option>"
            
            elif session['status'] == 'student':
                html += "<option value='s.status'>Student Status</option>"

            html += f"</select><div class='content-buttons'><form method='POST'> \
            <br><button type='button' class='back-button' onclick=\"window.location.href='/home';\"> \
            Back</button><br><button type='submit'>Show Selected</button><br> \
            </form></div></div></main><footer>Account Status: {session['status'].capitalize()}</footer> \
            </body>"

            return html
        
        elif request.method == "POST":
            selected_accounts = request.form.getlist('scode')
            
            html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'>\
            <title>Profile Report</title><body><main><div class='viewer-container'><h1>Profile Report</h1>"
            
            if selected_accounts:
                col_map = {
                    "a.username": "Username",
                    "a.password": "Password",
                    "a.first": "First Name",
                    "a.last": "Last Name",
                    "a.email": "Email",
                    "a.resume": "Resume",
                    "a.linkedin": "LinkedIn",
                    "d.name": "Department",
                    "a.status": "Account Status",
                    "p.website": "Website",
                    "p.status": "Professor Status",
                    "s.status": "Student Status"
                }

                placeholders = ', '.join(selected_accounts)
                query = f"SELECT a.id, {placeholders} FROM accounts a JOIN departments d ON a.department_id" \
                "= d.id LEFT JOIN professors p ON a.id = p.id AND a.status = 'professor' LEFT JOIN students s ON" \
                " a.id = s.id AND a.status = 'student' WHERE a.id = %s"

                cursor.execute(query, (session['id'], ))
                response = cursor.fetchone()
                print(response)

                html += f"<div class='row-heading'>ID: {response[0]}</div>"

                for row in selected_accounts:
                    if col_map[row] == "Account Status" or col_map[row] == "Professor Status" or col_map[row] == "Student Status":
                        html += f"<div class='content-field'><span class='viewer-label'>{col_map[row]}:</span> \
                        <span>{response[selected_accounts.index(row) + 1].capitalize()}</span></div>"
                    else:
                        html += f"<div class='content-field'><span class='viewer-label'>{col_map[row]}:</span> \
                        <span>{response[selected_accounts.index(row) + 1]}</span></div>"

            else:
                html += "<p>No codes selected.</p>"
                
            html += f"<div class='content-buttons'> \
            <button type='button' class='back-button' onclick=\"window.location.href='/profile';\">Back \
            </button></div></div></main><footer>Account Status: {session['status'].capitalize()}</footer></body>"
            
            return html
    
    else:
        if 'id' in session:
            return "<script>window.alert('You are not authorized to view this page.');" \
            "window.location.href = '/dashboard';</script>"

        else:
            return redirect(url_for('home'))

@app.route("/accounts", methods=['GET', 'POST'])
def view_accounts():
    if session['status'] == 'admin':
        cursor.execute("CALL GetEmails()")
        response = cursor.fetchall()

        while cursor.nextset(): 
            pass

        if request.method == "GET":
            html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'> \
            <title>Accounts Report</title><body><main><div class='viewer-container'><h1>Accounts Report</h1> \
            <p>Use Ctrl + Click on Windows (or ⌘ + Click on Mac) to select multiple options.</p> \
            <form method='POST'><select name='scode' id='scode' multiple>"
            
            for row in response:
                html += f"<option value='{row[0]}'>{row[0]}</option>"

            html += f"</select><div class='content-buttons'><form method='POST'> \
            <br><button type='button' class='back-button' onclick=\"window.location.href='/home';\"> \
            Back</button><br><button type='submit'>Show Selected</button><br> \
            </form></div></div></main><footer>Account Status: {session['status'].capitalize()}</footer> \
            </body>"

            return html
        
        elif request.method == "POST":
            selected_accounts = request.form.getlist('scode')
            
            html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'>\
            <title>Accounts Report</title><body><main><div class='viewer-container'><h1>Accounts Report</h1>"
            
            if selected_accounts:
                placeholders = ','.join(['%s'] * len(selected_accounts))
                query = f"SELECT * FROM accounts a LEFT JOIN departments d ON a.department_id = d.id \
                LEFT JOIN professors p ON a.id = p.id LEFT JOIN students s ON a.id = s.id \
                WHERE email IN ({placeholders})"
                cursor.execute(query, tuple(selected_accounts))
                response = cursor.fetchall()

                for row in response:
                    html += f"<div class='row-heading'>ID: {row[0]}</div> \
                    <div class='content-field'><span class='viewer-label'>Username:</span> \
                    <span>{row[1]}</span></div> \
                    <div class='content-field'><span class='viewer-label'>Password:</span><span>{row[2]}</span></div> \
                    <div class='content-field'><span class='viewer-label'>First:</span><span>{row[3]}</span></div> \
                    <div class='content-field'><span class='viewer-label'>Last:</span><span>{row[4]}</span></div> \
                    <div class='content-field'><span class='viewer-label'>Email:</span><span>{row[5]}</span></div> \
                    <div class='content-field'><span class='viewer-label'>Resume:</span><span>{row[6]}</span></div> \
                    <div class='content-field'><span class='viewer-label'>LinkedIn:</span><span>{row[7]}</span></div> \
                    <div class='content-field'><span class='viewer-label'>Status:</span><span>{row[9].capitalize()} \
                    </span></div><div class='content-field'><span class='viewer-label'>Department:</span> \
                    <span>{row[11]}</span></div>"

                    if row[9] == 'professor':
                        html += f"<div class='content-field'><span class='viewer-label'>Website:</span> \
                        <span>{row[13]}</span></div><div class='content-field'><span class='viewer-label'> \
                        Professor Status:</span><span>{row[14].capitalize()}</span></div>"
                    
                    elif row[9] == 'student':
                        html += f"<div class='content-field'><span class='viewer-label'>Student Status:</span> \
                        <span>{row[16].capitalize()}</span></div>"

            else:
                html += "<p>No codes selected.</p>"
                
            html += f"<div class='content-buttons'> \
            <button type='button' class='back-button' onclick=\"window.location.href='/accounts';\">Back \
            </button></div></div></main><footer>Account Status: {session['status'].capitalize()}</footer></body>"
            
            return html
            
    else:
        if 'id' in session:
            return "<script>window.alert('You are not authorized to view this page.');" \
            "window.location.href = '/dashboard';</script>"

        else:
            return redirect(url_for('home'))
        
@app.route("/departments", methods=['GET', 'POST'])
def view_departments():
    if session['status'] == 'admin':
        cursor.execute("CALL GetAllDepartmentNames()")
        response = cursor.fetchall()

        while cursor.nextset(): 
            pass

        if request.method == "GET":
            html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'> \
            <title>Departments Report</title><body><main><div class='viewer-container'><h1>Departments Report</h1> \
            <p>Use Ctrl + Click on Windows (or ⌘ + Click on Mac) to select multiple options.</p> \
            <form method='POST'><select name='scode' id='scode' multiple>"
            
            for row in response:
                html += f"<option value='{row[0]}'>{row[0]}</option>"

            html += f"</select><div class='content-buttons'><form method='POST'> \
            <br><button type='button' class='back-button' onclick=\"window.location.href='/dashboard';\"> \
            Back</button><br><button type='submit'>Show Selected</button><br> \
            </form></div></div></main><footer>Account Status: {session['status'].capitalize()}</footer> \
            </body>"

            return html
        
        elif request.method == "POST":
            selected_accounts = request.form.getlist('scode')
            
            html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'>\
            <title>Departments Report</title><body><main><div class='viewer-container'><h1>Departments Report</h1>"
            
            if selected_accounts:
                placeholders = ','.join(['%s'] * len(selected_accounts))
                query = f"SELECT * FROM departments WHERE name IN ({placeholders}) ORDER BY id ASC"
                cursor.execute(query, tuple(selected_accounts))
                response = cursor.fetchall()

                for row in response:
                    print(row)
                    html += f"<div class='row-heading'>ID: {row[0]}</div> \
                    <div class='content-field'><span class='viewer-label'>Name:</span> \
                    <span>{row[1]}</span></div>"

            else:
                html += "<p>No codes selected.</p>"
                
            html += f"<div class='content-buttons'> \
            <button type='button' class='back-button' onclick=\"window.location.href='/departments';\">Back \
            </button></div></div></main><footer>Account Status: {session['status'].capitalize()}</footer></body>"
            
            return html
    
    else:
        if 'id' in session:
            return "<script>window.alert('You are not authorized to view this page.');" \
            "window.location.href = '/dashboard';</script>"

        else:
            return redirect(url_for('home'))

@app.route("/projects", methods=['GET', 'POST'])
def view_projects():
    if 'id' in session:
        if session['status'] == 'admin':
            query = "SELECT * FROM projects"
            cursor.execute(query)
            response = cursor.fetchall()

            if request.method == "GET":
                html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'> \
                <title>Projects Report</title><body><main><div class='viewer-container'><h1>Projects Report</h1> \
                <p>Use Ctrl + Click on Windows (or ⌘ + Click on Mac) to select multiple options.</p> \
                <form method='POST'><select name='scode' id='scode' multiple>"
                
                for row in response:
                    html += f"<option value='{row[1]}'>{row[1]}</option>"

                html += f"</select><div class='content-buttons'><form method='POST'> \
                <br><button type='button' class='back-button' onclick=\"window.location.href='/home';\"> \
                Back</button><br><button type='submit'>Show Selected</button><br> \
                </form></div></div></main><footer>Account Status: {session['status'].capitalize()} \
                </footer></body>"

                return html
                
            elif request.method == "POST":
                selected_accounts = request.form.getlist('scode')
                
                html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'>\
                <title>Projects Report</title><body><main><div class='viewer-container'><h1>Projects Report</h1>"
                
                if selected_accounts:
                    placeholders = ','.join(['%s'] * len(selected_accounts))
                    query = f"SELECT p.*, a.first, a.last, d.name FROM projects p \
                    JOIN departments d ON p.department_id = d.id JOIN accounts a ON \
                    p.professor_id = a.id WHERE title IN ({placeholders})"

                    cursor.execute(query, tuple(selected_accounts))
                    response = cursor.fetchall()

                    for row in response:
                        print(row)
                        html += f"<div class='row-heading'>ID: {row[0]}</div> \
                        <div class='content-field'><span class='viewer-label'>Title:</span> \
                        <span>{row[1]}</span></div><div class='content-field'><span class='viewer-label'> \
                        Description:</span><span>{row[2]}</span></div><div class='content-field'> \
                        <span class='viewer-label'> \
                        Link:</span><span>{row[4]}</span></div><div class='content-field'> \
                        <span class='viewer-label'> \
                        Status:</span><span>{row[6].capitalize()}</span></div><div class='content-field'> \
                        <span class='viewer-label'> \
                        Department:</span><span>{row[9]}</span></div><div class='content-field'> \
                        <span class='viewer-label'> \
                        Professor:</span><span>{row[7]} {row[8]}</span></div>"

                else:
                    html += "<p>No codes selected.</p>"
                    
                html += f"<div class='content-buttons'> \
                <button type='button' class='back-button' onclick=\"window.location.href='/projects';\">Back \
                </button></div></div></main><footer>Account Status: {session['status'].capitalize()}</footer></body>"
                
                return html
    
        elif session['status'] == 'professor':
            query = "SELECT p.id, p.title, p.description, d.name, p.link, a.first, a.last, p.status FROM projects " \
            "p LEFT JOIN departments d ON p.department_id = d.id LEFT JOIN accounts a " \
            "ON p.professor_id = a.id WHERE a.id = %s ORDER BY p.id ASC"
            
            cursor.execute(query, (session['id'], ))
            response = cursor.fetchall()

            if request.method == "GET":
                html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'> \
                <title>Projects Report</title><body><main><div class='viewer-container'><h1>Projects Report</h1> \
                <p>Use Ctrl + Click on Windows (or ⌘ + Click on Mac) to select multiple options.</p> \
                <form method='POST'><select name='scode' id='scode' multiple>"
                
                for row in response:
                    html += f"<option value='{row[1]}'>{row[1]}</option>"

                html += f"</select><div class='content-buttons'><form method='POST'> \
                <br><button type='button' class='back-button' onclick=\"window.location.href='/home';\"> \
                Back</button><br><button type='submit'>Show Selected</button><br> \
                </form></div></div></main><footer>Account Status: {session['status'].capitalize()} \
                </footer></body>"

                return html
            
            elif request.method == "POST":
                selected_accounts = request.form.getlist('scode')
                
                html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'>\
                <title>Projects Report</title><body><main><div class='viewer-container'><h1>Projects Report</h1>"
                
                if selected_accounts:
                    placeholders = ','.join(['%s'] * len(selected_accounts))
                    query = f"SELECT p.*, a.first, a.last, d.name FROM projects p \
                    JOIN departments d ON p.department_id = d.id JOIN accounts a ON \
                    p.professor_id = a.id WHERE title IN ({placeholders})"

                    cursor.execute(query, tuple(selected_accounts))
                    response = cursor.fetchall()

                    for row in response:
                        print(row)
                        html += f"<div class='row-heading'>ID: {row[0]}</div> \
                        <div class='content-field'><span class='viewer-label'>Title:</span> \
                        <span>{row[1]}</span></div><div class='content-field'><span class='viewer-label'> \
                        Description:</span><span>{row[2]}</span></div><div class='content-field'> \
                        <span class='viewer-label'> \
                        Link:</span><span>{row[4]}</span></div><div class='content-field'> \
                        <span class='viewer-label'> \
                        Status:</span><span>{row[6].capitalize()}</span></div><div class='content-field'> \
                        <span class='viewer-label'> \
                        Department:</span><span>{row[9]}</span></div><div class='content-field'> \
                        <span class='viewer-label'> \
                        Professor:</span><span>{row[7]} {row[8]}</span></div>"

                else:
                    html += "<p>No codes selected.</p>"
                    
                html += f"<div class='content-buttons'> \
                <button type='button' class='back-button' onclick=\"window.location.href='/projects';\">Back \
                </button></div></div></main><footer>Account Status: {session['status'].capitalize()}</footer></body>"
                
                return html
                
        elif session['status'] == 'student':
            query = f"SELECT p.title FROM projects p JOIN projects_students \
            ps ON p.id = ps.project_id JOIN departments d ON p.department_id = d.id JOIN accounts a ON \
            p.professor_id = a.id WHERE ps.student_id = %s"

            cursor.execute(query, (session['id'], ))
            response = cursor.fetchall()

            if request.method == "GET":
                html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'> \
                <title>Projects Report</title><body><main><div class='viewer-container'><h1>Projects Report</h1> \
                <p>Use Ctrl + Click on Windows (or ⌘ + Click on Mac) to select multiple options.</p> \
                <form method='POST'><select name='scode' id='scode' multiple>"
                
                for row in response:
                    html += f"<option value='{row[0]}'>{row[0]}</option>"

                html += f"</select><div class='content-buttons'><form method='POST'> \
                <br><button type='button' class='back-button' onclick=\"window.location.href='/home';\"> \
                Back</button><br><button type='submit'>Show Selected</button><br> \
                </form></div></div></main><footer>Account Status: {session['status'].capitalize()} \
                </footer></body>"

                return html

            elif request.method == "POST":
                selected_accounts = request.form.getlist('scode')
                
                html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'>\
                <title>Projects Report</title><body><main><div class='viewer-container'><h1>Projects Report</h1>"
                
                if selected_accounts:
                    placeholders = ','.join(['%s'] * len(selected_accounts))
                    
                    query = f"SELECT p.*, a.first, a.last, d.name FROM projects p \
                    JOIN departments d ON p.department_id = d.id JOIN accounts a ON \
                    p.professor_id = a.id WHERE title IN ({placeholders})"

                    cursor.execute(query, tuple(selected_accounts))
                    response = cursor.fetchall()

                    for row in response:
                        print(row)
                        html += f"<div class='row-heading'>ID: {row[0]}</div> \
                        <div class='content-field'><span class='viewer-label'>Title:</span> \
                        <span>{row[1]}</span></div><div class='content-field'><span class='viewer-label'> \
                        Description:</span><span>{row[2]}</span></div><div class='content-field'> \
                        <span class='viewer-label'> \
                        Link:</span><span>{row[4]}</span></div><div class='content-field'> \
                        <span class='viewer-label'> \
                        Status:</span><span>{row[6].capitalize()}</span></div><div class='content-field'> \
                        <span class='viewer-label'> \
                        Department:</span><span>{row[9]}</span></div><div class='content-field'> \
                        <span class='viewer-label'> \
                        Professor:</span><span>{row[7]} {row[8]}</span></div>"

                else:
                    html += "<p>No codes selected.</p>"
                    
                html += f"<div class='content-buttons'> \
                <button type='button' class='back-button' onclick=\"window.location.href='/projects';\">Back \
                </button></div></div></main><footer>Account Status: {session['status'].capitalize()}</footer></body>"
                
                return html
        
    else:
        return redirect(url_for('home'))

@app.route("/status-codes", methods=['GET', 'POST'])
def view_status_codes():
    if session['status'] == 'admin':
        query = "SELECT * FROM status_codes"
        cursor.execute(query)
        response = cursor.fetchall()

        if request.method == "GET":
            html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'> \
            <title>Status Codes Report</title><body><main><div class='viewer-container'><h1>Status Codes Report</h1> \
            <p>Use Ctrl + Click on Windows (or ⌘ + Click on Mac) to select multiple options.</p> \
            <form method='POST'><select name='scode' id='scode' multiple>"
            
            for row in response:
                html += f"<option value='{row[1]}'>{row[1].capitalize()}</option>"

            html += f"</select><div class='content-buttons'><form method='POST'> \
            <br><button type='button' class='back-button' onclick=\"window.location.href='/home';\"> \
            Back</button><br><button type='submit'>Show Selected</button><br> \
            </form></div></div></main><footer>Account Status: {session['status'].capitalize()}</footer> \
            </body>"

            return html
        
        elif request.method == "POST":
            selected_accounts = request.form.getlist('scode')
            
            html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'>\
            <title>Status Codes Report</title><body><main><div class='viewer-container'><h1>Status Codes Report</h1>"
            
            if selected_accounts:
                placeholders = ','.join(['%s'] * len(selected_accounts))
                query = f"SELECT * FROM status_codes WHERE account IN ({placeholders})"
                cursor.execute(query, tuple(selected_accounts))
                response = cursor.fetchall()

                for row in response:
                    print(row)
                    html += f"<div class='row-heading'>ID: {row[0]}</div> \
                    <div class='content-field'><span class='viewer-label'>Account Type:</span> \
                    <span>{row[1].capitalize()}</span></div> \
                    <div class='content-field'><span class='viewer-label'>Code:</span><span>{row[2]}</span></div>"

            else:
                html += "<p>No codes selected.</p>"
                
            html += f"<div class='content-buttons'> \
            <button type='button' class='back-button' onclick=\"window.location.href='/status-codes';\">Back \
            </button></div></div></main><footer>Account Status: {session['status'].capitalize()}</footer></body>"
            
            return html
        
    else:
        if 'id' in session:
            return "<script>window.alert('You are not authorized to view this page.');" \
            "window.location.href = '/dashboard';</script>"

        else:
            return redirect(url_for('home'))

@app.route("/edit", methods=['GET', 'POST'])
def edit_profile():
    if request.method == "GET":
        html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'> \
        <title>Account Settings</title><body><main><div class='content-container'><h1>Account Settings</h1> \
        <form method='POST' onsubmit='return handlePrompt();'><label for='ssetting'>Account Setting to Change:</label> \
        <select name='ssetting' id='ssetting'><option value='username'>Username</option><option value='password'> \
        Password</option><option value='first'>First Name</option><option value='last'>Last Name</option> \
        <option value='email'>Email</option><option value='resume'>Resume</option><option value='linkedin'> \
        LinkedIn</option><option value='department'>Department ID</option>"
        
        if session['status'] == 'professor':
            html += "<option value='professor_website'>Professor Website</option> \
            <option value='professor_status'>Professor Status</option>"
        
        elif session['status'] == 'student':
            html += "<option value='student_status'>Student Status</option>"
        
        html += f"</select><input type='hidden' name='new_value' id='new_value' value=''><br><br> \
        <div class='content-buttons'><button type='button' class='back-button' onclick=\"window.location.href='/home';\">Back</button> \
        <button type='button' class='btn-account' onclick='window.location.href='/delete/account/{session['id']}'> \
        Delete Account</button><button type='submit'>Change Setting</button> \
        </div></form></main><footer>Account Status: {session['status'].capitalize()}</footer><script> \
        function handlePrompt() {{ var newValue = prompt('Enter new value (limit: 35 characters): '); \
        if (newValue !== null && newValue.trim() !== '') {{ document.getElementById('new_value').value = newValue; \
        return true; }} return false; }};</script></body>"
        
        return html
    
    elif request.method == "POST":
        setting_type = request.form.get('ssetting')
        new_value = request.form.get('new_value')

        if len(new_value) > 35 or len(new_value) == 0:
            return f"<script>alert('Status code must be between 0-35 characters.'); window.location.href='/edit'; \
            </script>"
        
        if (setting_type == 'student_status'):
            if new_value not in ['undergraduate', 'graduate']:
                return f"<script>alert('Student status must either be undergraduate or graduate.'); \
                window.location.href='/edit';</script>"

            query = f"UPDATE students SET status = %s WHERE id = %s"

        elif (setting_type == 'professor_website'):
            query = f"UPDATE professors SET website = %s WHERE id = %s"

        elif (setting_type == 'professor_status'):
            if new_value not in ['assistant', 'associate', 'full']:
                return f"<script>alert('Professor status must be assistant, associate, or full.'); \
                window.location.href='/edit';</script>"
            
            else:
                query = f"UPDATE professors SET status = %s WHERE id = %s"

        else:
            query = f"UPDATE accounts SET {setting_type} = %s WHERE id = %s"
        
        cursor.execute(query, (new_value, session['id'], ))
        cnx.commit()

        return "<script>alert('Successfully updated!'); window.location.href='/edit';</script>"
    
@app.route("/edit/departments", methods=['GET', 'POST'])
def edit_departments():
    if session['status'] == 'admin':
        cursor.execute("CALL GetAllDepartmentNames()")
        response = cursor.fetchall()

        while cursor.nextset():
            pass

        if request.method == "GET":
            html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'> \
            <title>Edit Departments</title><body><main><div class='content-container'><h1>Edit Departments</h1> \
            <form method='POST' onsubmit='return handlePrompt();'><label for='sname'>Department to Change:</label> \
            <select name='sname' id='sname'>"

            for row in response:
                html += f"<option value='{row[0]}'>{row[0]}</option>"
            
            html += f"<input type='hidden' name='newName' id='newName' value=''><br><br></select> \
            <div class='content-buttons'> \
            <button type='button' class='back-button' onclick=\"window.location.href='/home';\">Back</button> \
            <button type='button' class='btn-account' onclick=\"window.location.href='/new/departments';\"> \
            Add New Department</button><button type='submit'>Change Department</button></div></form></main><footer> \
            Account Status: {session['status'].capitalize()}</footer><script> \
            function handlePrompt() {{ var new_name = prompt('Enter new department name (max. 35 characters): '); \
            if (new_name !== null && new_name.trim() !== '') {{ document.getElementById('newName').value = new_name; \
            return true; }} return false; }};</script></body>"

            return html
        
        elif request.method == "POST":
            old_name = request.form.get('sname')
            new_name = request.form.get('newName')
            if not new_name or len(new_name) > 35:
                return "<script>alert('Status code must be between 0-35 characters.'); " \
                "window.location.href='/edit/status-codes';</script>"
            query = f"UPDATE departments SET name = %s WHERE name = %s;"
            cursor.execute(query, (new_name, old_name))
            cnx.commit()
            return "<script>alert('Successfully updated!'); window.location.href='/edit/departments';</script>"
        
    else:
        if 'id' in session:
            return "<script>window.alert('You are not authorized to view this page.');" \
            "window.location.href = '/dashboard';</script>"

        else:
            return redirect(url_for('home')) 
    
@app.route("/edit/projects", methods=['GET', 'POST'])
def edit_projects():
    if session['status'] == 'admin':
        cursor.execute("CALL GetProjectTitles()")
        response = cursor.fetchall()

        while cursor.nextset():
            pass

        if request.method == "GET":
            html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'> \
            <title>Edit Projects</title><body><main><div class='content-container'><h1>Edit Projects</h1> \
            <form method='POST' onsubmit='return handlePrompt();'><label for='sname'>Project to Change:</label> \
            <select name='sname' id='sname'>"            
            
            for row in response:
                html += f"<option value='{row[0]}'>{row[0]}</option>"
            
            html += f"<input type='hidden' name='newValue' id='newValue' value=''><br><br></select> \
            <label for='sdetail'>Project Detail</label><select name='sdetail' id='sdetail'><option value='title'> \
            Title</option><option value='description'>Description</option><option value='link'>Link</option> \
            <option value='status'>Status</option></select><div class='content-buttons'> \
            <button type='button' class='back-button' onclick=\"window.location.href='/home';\">Back</button> \
            <button type='submit'>Change Project</button></div></form></main><footer> \
            Account Status: {session['status'].capitalize()}</footer><script> \
            function handlePrompt() {{ var new_value = prompt('Enter new value (max. 35 characters): '); \
            if (new_value !== null && new_value.trim() !== '') {{ document.getElementById('newValue').value=new_value; \
            return true; }} return false; }};</script></body>"

            return html
        
        elif request.method == "POST":
            sdetail = request.form.get('sdetail')
            new_value = request.form.get('newValue')
            old_name = request.form.get('sname')

            if not new_value or len(new_value) > 35:
                return "<script>alert('Setting must be between 0-35 characters.'); " \
                "window.location.href='/edit/projects';</script>"
            
            query = f"UPDATE projects SET {sdetail} = %s WHERE title = %s;"
            cursor.execute(query, (new_value, old_name))
            cnx.commit()
            return "<script>alert('Successfully updated!'); window.location.href='/edit/projects';</script>"
        
    elif session['status'] == 'professor':
        if request.method == "GET":
            query = "SELECT title FROM projects WHERE professor_id = %s"
            cursor.execute(query, (session['id'], ))
            response = cursor.fetchall()

            html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'> \
            <title>Edit Projects</title><body><main><div class='content-container'><h1>Edit Projects</h1> \
            <form method='POST' onsubmit='return handlePrompt();'><label for='sname'>Project to Change:</label> \
            <select name='sname' id='sname'>"            
            
            for row in response:
                html += f"<option value='{row[0]}'>{row[0]}</option>"
            
            html += f"<input type='hidden' name='newValue' id='newValue' value=''><br><br></select> \
            <label for='sdetail'>Project Detail</label><select name='sdetail' id='sdetail'><option value='title'> \
            Title</option><option value='description'>Description</option><option value='link'>Link</option> \
            <option value='status'>Status</option></select><div class='content-buttons'> \
            <button type='button' class='back-button' onclick=\"window.location.href='/home';\">Back</button> \
            <button type='submit'>Change Project</button></div></form></main><footer> \
            Account Status: {session['status'].capitalize()}</footer><script> \
            function handlePrompt() {{ var new_value = prompt('Enter new value (max. 35 characters): '); \
            if (new_value !== null && new_value.trim() !== '') {{ document.getElementById('newValue').value=new_value; \
            return true; }} return false; }};</script></body>"

            return html
        
        elif request.method == "POST":
            sdetail = request.form.get('sdetail')
            new_value = request.form.get('newValue')
            old_name = request.form.get('sname')

            if not new_value or len(new_value) > 35:
                return "<script>alert('Setting must be between 0-35 characters.'); " \
                "window.location.href='/edit/projects';</script>"
            
            query = f"UPDATE projects SET {sdetail} = %s WHERE name = %s;"
            cursor.execute(query, (new_value, old_name))
            cnx.commit()
            return "<script>alert('Successfully updated!'); window.location.href='/edit/projects';</script>"

    else:
        query = "SELECT p.title FROM projects p JOIN projects_students ps ON p.id = ps.project_id " \
        "WHERE ps.student_id = %s;"
        cursor.execute(query, (session['id'], ))
        response = cursor.fetchall()

        if request.method == "GET":
            html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'> \
            <title>Edit Projects</title><body><main><div class='content-container'><h1>Edit Projects</h1> \
            <form method='POST' onsubmit='return handlePrompt();'><label for='sname'>Project to Change:</label> \
            <select name='sname' id='sname'>"

            for row in response:
                html += f"<option value='{row[0]}'>{row[0]}</option>"
            
            html += f"<br><br></select> \
            <div class='content-buttons'> \
            <button type='button' class='back-button' onclick=\"window.location.href='/home';\">Back</button> \
            <button type='submit'>Leave Project</button></div></form></main><footer> \
            Account Status: {session['status'].capitalize()}</footer></body>"

            return html
        
        elif request.method == "POST":
            pname = request.form.get('sname')
            query = f"SELECT id FROM projects WHERE title = %s;"
            cursor.execute(query, (pname, ))
            response = cursor.fetchone()
            response = response[0]

            query = f"DELETE FROM projects_students WHERE student_id = %s AND project_id = %s;"
            cursor.execute(query, (session['id'], response))
            cnx.commit()
            return "<script>alert('Successfully left!'); window.location.href='/edit/projects';</script>"

@app.route("/edit/status-codes", methods=['GET', 'POST'])
def edit_status_codes():
    if session['status'] == 'admin':
        if request.method == "GET":
            return f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'> \
            <title>Edit Status Codes</title><body><main><div class='content-container'><h1>Edit Status Codes</h1> \
            <form method='POST' onsubmit='return handlePrompt();'><label for='scode'>Status Code to Change:</label> \
            <select name='scode' id='scode'><option value='admin'>Admin</option><option value='student'> \
            Student</option><option value='professor'>Professor</option></select> \
            <input type='hidden' name='new_code' id='new_code' value=''><br><br><div class='content-buttons'> \
            <button type='button' class='back-button' onclick=\"window.location.href='/home';\">Back</button> \
            <button type='submit'>Change Status Code</button></div></form></main><footer> \
            Account Status: {session['status'].capitalize()}</footer><script> \
            function handlePrompt() {{ var newCode = prompt('Enter new status code (4 digit numbers only): '); \
            if (newCode !== null && newCode.trim() !== '') {{ document.getElementById('new_code').value = newCode; \
            return true; }} return false; }};</script></body>"
        
        elif request.method == "POST":
            status_code_type = request.form.get('scode')
            new_code = request.form.get('new_code')
            if not new_code or not new_code.isdigit() or len(new_code) != 4:
                return "<script>alert('Status code must be a 4-digit number.'); " \
                "window.location.href='/edit/status-codes';</script>"
            query = f"UPDATE status_codes SET {status_code_type} = %s WHERE id = 1"
            cursor.execute(query, (new_code, ))
            cnx.commit()
            return "<script>alert('Successfully updated!'); window.location.href='/edit/status-codes';</script>"
        
    else:
        if 'id' in session:
            return "<script>window.alert('You are not authorized to view this page.');" \
            "window.location.href = '/dashboard';</script>"

        else:
            return redirect(url_for('home'))
        
@app.route("/new/projects", methods=['GET', 'POST'])
def new_projects():
    if session['status'] == 'professor':
        if request.method == "GET":
            cursor.execute("CALL GetAllDepartmentNames")
            responses = cursor.fetchall()

            while cursor.nextset():
                pass

            html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'><title>New Project</title>" \
            "<main><div class='content-container'><h1>New Project</h1><p>Fields marked with an asterisk (*) are required." \
            "</p><p>All fields have a character limit of 35.</p><form method='POST'>" \
            "*Title: <input type='text' name='title' maxlength='35'><br><br>*Description: " \
            "<input type='text' name='description' maxlength='35' required>" \
            "<br><br>*Link: <input type='text' name='link' maxlength='35' required>" \
            "<br><br>*Department: <select name='dpt' id='dpt' required>"

            for row in responses:
                html += f"<option value='{row[0]}'>{row[0]}</option>"

            html += f"</select><br><br>*Status: <select name='status_type' id='status_type'>" \
            "<option value='open'>Open</option>" \
            "<option value='closed'>Closed</option><option value='paused'>Paused</option></select>" \
            "<div class='content-buttons'>" \
            "<button type='button' class='back-button' onclick=\"window.location.href='/home';\">Back</button> " \
            "<button type='submit'>Create Project</button></div></form></div></main><footer>Research Buddy v1.0a" \
            "</footer>"

            return html
        
        elif request.method == "POST":
            title = request.form.get('title')
            description = request.form.get('description')
            department = request.form.get('dpt')
            link = request.form.get('link')
            status = request.form.get('status_type')
            
            cursor.execute("SELECT id FROM departments WHERE name = %s", (department,))
            dept_id = cursor.fetchone()[0]
            
            insert_account = "INSERT INTO projects (title, description, department_id, link, professor_id, status)" \
            "VALUES (%s, %s, %s, %s, %s, %s);"

            cursor.execute(insert_account, (title, description, dept_id, link, session['id'], status))
            cnx.commit()

            return "<script>window.alert('Project created successfully!');window.location.href = '/dashboard';</script>"
        
    elif session['status'] == 'student':
        query = "SELECT p.title FROM projects p WHERE p.department_id = %s AND p.id NOT IN (SELECT project_id " \
        "FROM projects_students WHERE student_id = %s);"

        cursor.execute(query, (session['department_id'], session['id']))
        response = cursor.fetchall()

        if request.method == "GET":
            html = f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'> \
            <title>New Project</title><body><main><div class='content-container'><h1>New Project</h1> \
            <form method='POST' onsubmit='return handlePrompt();'><label for='sname'>Project to Join:</label> \
            <select name='sname' id='sname'>"

            for row in response:
                html += f"<option value='{row[0]}'>{row[0]}</option>"
            
            html += f"<br><br></select> \
            <div class='content-buttons'> \
            <button type='button' class='back-button' onclick=\"window.location.href='/home';\">Back</button> \
            <button type='submit'>Join Project</button></div></form></main><footer> \
            Account Status: {session['status'].capitalize()}</footer></body>"

            return html
        
        elif request.method == "POST":
            pname = request.form.get('sname')
            query = f"SELECT id FROM projects WHERE title = %s;"
            cursor.execute(query, (pname, ))
            response = cursor.fetchone()
            response = response[0]

            query = f"INSERT INTO projects_students (student_id, project_id) VALUES (%s, %s);"
            cursor.execute(query, (session['id'], response))
            cnx.commit()
            return "<script>alert('Successfully joined!'); window.location.href='/dashboard';</script>"
        
    else:
        if 'id' in session:
            return "<script>window.alert('You are not authorized to view this page.');" \
            "window.location.href = '/dashboard';</script>"

        else:
            return redirect(url_for('home'))

@app.route("/new/departments", methods=['GET', 'POST'])
def new_departments():
    if session['status'] == 'admin':
        if request.method == "GET":

            return f"<link rel='stylesheet' href='{url_for('static', filename='styles.css')}'><title>New Department \
            </title><main><div class='content-container'><h1>New Department</h1><p> \
            Fields marked with an asterisk (*) are required.</p><p>All fields have a character limit of 35.</p> \
            <form method='POST'>*Name: <input type='text' name='name' maxlength='35'><br><br> \
            <div class='content-buttons'> \
            <button type='button' class='back-button' onclick=\"window.location.href='/home';\">Back</button> \
            <button type='submit'>Create Department</button></div></form></div></main><footer>Research Buddy v1.0a \
            </footer>"
        
        elif request.method == "POST":
            title = request.form.get('name')
            
            insert_department = "INSERT INTO departments (name) VALUES (%s)" \

            cursor.execute(insert_department, (title, ))
            cnx.commit()

            return "<script>window.alert('Department created successfully!');window.location.href = '/dashboard'; \
                </script>"
        
    else:
        if 'id' in session:
            return "<script>window.alert('You are not authorized to view this page.');" \
            "window.location.href = '/dashboard';</script>"

        else:
            return redirect(url_for('home'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route("/delete/account/<int:account_id>")
def delete_account(account_id):
    if 'id' in session:
        if account_id == session['id']:
            cursor.execute("CALL DeleteAccount(%s)", (account_id,))
            cnx.commit()
            session.clear()
            return "<script>alert('Successfully deleted account!'); window.location.href='/home';</script>"

        else:
            return "<script>alert('You cannot delete another account!'); window.location.href='/dashboard';</script>"
        
    else:
        return redirect(url_for('home'))

if __name__=="__main__":
    app.run(debug=True)
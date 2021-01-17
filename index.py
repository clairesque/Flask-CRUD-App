# Importing elements from flask
from flask import Flask, render_template, redirect, request, url_for, session
import sqlite3 as s
import sys
app = Flask(__name__, static_folder='static')  
# Super secret key
app.secret_key = "super secret key"
# Database file
DB_FILE = 'mydb.db'    	
# Connecting to the database	
connection = s.connect(DB_FILE, check_same_thread=False)

# Page route for index
@app.route('/')
def index():
        try:
                return render_template('index.html')
        except:
                return render_template('error.html', msg=sys.exc_info()[1])

# Page route for reviews
@app.route('/reviews')
def reviews():
        try:
                return render_template('reviews.html')
        except:
                return render_template('error.html', msg=sys.exc_info()[1])

# Inserting values from the contact form into table
def _cinsert(name, email, message):
	params = {'name':name, 'email':email, 'message':message}
	connection = s.connect(DB_FILE)
	cursor = connection.cursor()  
	cursor.execute("insert into contact VALUES (:name, :email, :message)",params)
	connection.commit()
	cursor.close()

# Reloading page after values have been inserted into the table
@app.route('/contact', methods=['POST', 'GET'])
def contact():
        try:
                if request.method == 'POST':
                        _cinsert(request.form['name'], request.form['email'], request.form['message'])
                        return render_template('contact.html', msg="Your message has been sent!")
                else:
                        return render_template('contact.html')
        except:
                return render_template('error.html', msg=sys.exc_info()[1])

# Inserting values into guestbook table
def _ginsert(name, phone, address):
	
	params = {'name':name, 'phone':phone, 'address':address}
	connection = s.connect(DB_FILE)
	cursor = connection.cursor()  
	cursor.execute("insert into addressbook (name,phone,address) VALUES (:name, :phone, :address)",params)
	connection.commit()
	cursor.close()

# Error page 
@app.route('/error')
def error():
         return render_template('error.html')

# Routing for addressbook page
@app.route('/addressbook', methods=['POST', 'GET'])
def addressbook():
        try:
                connection = s.connect(DB_FILE)
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM addressbook")
                rv = cursor.fetchall()
                connection.commit()
                cursor.close()
                return render_template("addressbook.html", entries=rv)
        except:
                return render_template('error.html', msg=sys.exc_info()[2])
                
                
# Reloads page after inserting values into the table
@app.route('/gsign', methods=['POST'])
def gsign():
	
	_ginsert(request.form['name'], request.form['phone'], request.form['address'])
	return redirect(url_for('addressbook'))



# Logging in code
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        query = "select * from accounts where username = '" + request.form['username']
        query = query + "' and password = '" + request.form['password'] + "';"
        
        cur = connection.execute(query)
        rv = cur.fetchall()
        
        cur.close()
        if len(rv) == 1:
            session['username'] = request.form['username']
            
            session['logged in'] = True

            return render_template('login.html', msg="Welcome back, ")
        else:
            return render_template('login.html', msg="Check your login details and try again.")
    else:
        return render_template('login.html')

# Profile page that has the name of the user signed in
@app.route('/account')
def account():
    if session['logged in'] == True:
        connection = s.connect(DB_FILE)
        cursor = connection.cursor()
        query = "SELECT * FROM accounts WHERE username = '"+ session['username'] + "';"
        cursor = connection.execute(query)
        profile = cursor.fetchone()
        cursor.close()
        return render_template('account.html',profile=profile)
    else:
        return redirect('/login')

# Creates a new user in the accounts table
def _insertuser(username, email, password):
    params = {'username': username, 'email': email, 'password': password}
    cursor = connection.cursor()
    cursor.execute("insert into accounts(username, email, password) values (:username, :email, :password)"
                   , params)
    connection.commit()

# Routing for registering page
@app.route('/register',  methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        _insertuser(request.form['username'], request.form['email'], request.form['password'])
        return render_template('register.html', msg="You have successfully signed up. Please login.")
    else:
        return render_template('register.html')

# Logout function
@app.route('/logout')
def logout():
        session.pop('logged in', None)
        session.pop('username', None)
        return redirect('/')

# Inserting values and reloading page for the 5 different review pages
def _insert1(username, comment):
	
	params = {'username':username, 'comment':comment}
	connection = s.connect(DB_FILE)
	cursor = connection.cursor()  
	cursor.execute("insert into reviews1 VALUES (:username, :comment)",params)
	connection.commit()
	cursor.close()
    
@app.route('/sign1', methods=['POST'])
def sign1():
        _insert1(session['username'], request.form['comment'])
        return redirect(url_for('review1'))
    
@app.route('/review1', methods=['POST', 'GET'])
def review1():
        try:
                connection = s.connect(DB_FILE)
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM reviews1")
                rv = cursor.fetchall()
                connection.commit()
                cursor.close()
                return render_template('review1.html',entries=rv)
        except:
                return render_template('error.html', msg=sys.exc_info()[1])


# Deletes values from the table
@app.route('/delete', methods=['POST', 'GET'])
def delete():
        try:
                id = request.args.get("id")
                connection = s.connect(DB_FILE)
                cursor = connection.cursor()
                cursor.execute("DELETE from addressbook where id ="+id)
                rv = cursor.fetchall()
                connection.commit()
                cursor.close()
                return render_template('delete.html',entries=rv)
        except:
                return render_template('error.html', msg=sys.exc_info()[1])

if __name__ == '__main__':
        app.run()
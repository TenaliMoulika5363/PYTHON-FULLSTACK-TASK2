from flask import Flask,render_template,request,flash,redirect,session
from werkzeug.security import generate_password_hash,check_password_hash

import sqlite3

app=Flask(__name__)

app.secret_key="mysecretkey"

def get_db_connection():
    conn=sqlite3.connect("database.db")

    conn.row_factory=sqlite3.Row

    return conn


@app.route("/register", methods=["GET","POST"])
def register():

    error=None
    success=False

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        existing_user=cursor.fetchone()

        if existing_user:
            error="Username already exists"
        else:
            hashed_password=generate_password_hash(password)
        
            cursor.execute(
                "INSERT INTO users(username,password) VALUES (?,?)",
                (username,hashed_password)
            )

            conn.commit()

            success=True

        conn.close()

    return render_template("register.html",error=error,
                           success=success)



@app.route("/login",methods=["GET","POST"])
def login():

    error=None

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        conn=get_db_connection()
        cursor=conn.cursor()

        cursor.execute(
            "SELECT *FROM users WHERE username=?",
            (username,)
        )

        user=cursor.fetchone()

        conn.close()

        if user and check_password_hash(user["password"],password):

            session["username"]=username

            return redirect("/dashboard")

        else:

            error= "Invalid Username or Password"

    return render_template("login.html",error=error)

@app.route("/dashboard")
def dashboard():

    if "username" in session:
        return render_template("dashboard.html"
                        ,username=session["username"])
    else:
        return redirect("/login")
    
@app.route("/logout")
def logout():
    session.clear()

    return redirect("/login")

if __name__=="__main__":
    app.run(debug=True)


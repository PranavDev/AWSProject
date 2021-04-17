# Project01: ENTS649B-AWS-Netflix
# Author: Pranav H. Deo
# Date: 04/15/21
# Version: v1.1

# Code Description:
# Compute: Amazon EC2
# Database: RDS, MySQL
# Storage: Amazon S3
# Type: Flask Web Application

##############################################################

import yaml
import boto3
import pymysql
from flask import *
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

##############################################################
# --------------------- FLASK-APP -------------------------- #
app = Flask(__name__)
app.config.from_mapping(SECREY_KEY='dev')
app.secret_key = 'Phd240997#'
'''
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'pranavhdev@gmail.com'
app.config['MAIL_PASSWORD'] = 'veijfjuwcdfxomlr'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
'''
##############################################################
# --------------------- AMAZON-S3 -------------------------- #
BUCKET_NAME = 'netflix-aws-bucket'
# --------------------- LAMP-MySQL ------------------------- #
# db = yaml.load(open('db.yaml'))
# app.config['MYSQL_HOST'] = db['mysql_host']
# app.config['MYSQL_USER'] = db['mysql_user']
# app.config['MYSQL_PASSWORD'] = db['mysql_password']
# app.config['MYSQL_DB'] = db['mysql_db']
# mysql = MySQL(app)
# --------------------- AWS-RDS ------------------------- #
DB = yaml.load(open('db.yaml'))
conn = pymysql.connect(host=DB['mysql_host'],
                       user=DB['mysql_user'],
                       password=DB['mysql_password'],
                       database=DB['mysql_db'],
                       port=int(DB['mysql_port']))
##############################################################


@app.route('/')
@app.route('/HomePage')
def HomePage():
    session.pop('user_email', None)
    return render_template('HomePage.html')


@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        session.pop('user_email', None)
        user_email = request.form['email']
        user_password = request.form['password']
        cur = conn.cursor()
        cur.execute('SELECT * FROM information_schema.tables WHERE table_name = "Netflix_Users"')
        if cur.fetchone() is None:
            create_table = "create table Netflix_Users (username varchar(100),email varchar(100),password varchar(100))"
            cur.execute(create_table)
            conn.commit()
            cur.close()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Netflix_Users WHERE email = % s AND password = % s;', (user_email, user_password))
        if cursor.fetchone() is not None:
            session['user_email'] = user_email
            # Send_Email(user_email, 'Login')
            cursor.close()
            return render_template('UserHome.html')
        else:
            cursor.close()
            return render_template('Register.html')
    else:
        return render_template('Login.html')


@app.route('/Register', methods=['GET', 'POST'])
def Register():
    if request.method == 'POST':
        user_name = request.form['username']
        user_em = request.form['email']
        user_pass = request.form['password']
        profile_img = request.files['file']
        filename = secure_filename(profile_img.filename)
        profile_img.save('./Downloads/' + filename)
        cur = conn.cursor()
        cur.execute('SELECT * FROM information_schema.tables WHERE table_name = "Netflix_Users"')
        if cur.fetchone() is None:
            create_table = "create table Netflix_Users (username varchar(100),email varchar(100),password varchar(100))"
            cur.execute(create_table)
            conn.commit()
            cur.close()
        cur = conn.cursor()
        cur.execute("INSERT INTO Netflix_Users(username, email, password) VALUES (%s, %s, %s)",
                    (user_name, user_em, user_pass))
        conn.commit()
        cur.close()
        s3_client = boto3.client('s3')
        s3_client.upload_file(Bucket=BUCKET_NAME, Filename='./Downloads/' + filename,
                              Key='Profile_Image_Uploads/' + user_em.partition('@')[0] + '.jpg')
        # Send_Email(user_em, 'Register')
        return render_template('Login.html')
    else:
        return render_template('Register.html')


@app.route('/NetflixPlans')
def NetflixPlans():
    return render_template('NetflixPlans.html')


@app.route('/NetflixMovies')
def NetflixMovies():
    if 'user_email' in session:
        return render_template('NetflixMovies.html')
    else:
        return render_template('Login.html')


@app.route('/NetflixShows')
def NetflixShows():
    if 'user_email' in session:
        return render_template('NetflixShows.html')
    else:
        return render_template('Login.html')


@app.route('/UserHome')
def UserHome():
    if 'user_email' in session:
        return render_template('UserHome.html')
    else:
        return render_template('Login.html')


@app.route('/Logout')
def Logout():
    session.pop('user_email', None)
    return render_template('HomePage.html')


@app.route('/MyAccount')
def MyAccount():
    if 'user_email' in session:
        return render_template('MyAccount.html')
    else:
        return render_template('Login.html')


@app.route('/UpdateAccount', methods=['GET', 'POST'])
def UpdateAccount():
    if 'user_email' in session:
        if request.method == 'POST':
            email = request.form['email']
            cur = conn.cursor()
            cur.execute("SELECT username, password FROM Netflix_Users WHERE email LIKE (%s)", (email,))
            result = cur.fetchall()
            if result is not None:
                cur.close()
                return render_template('EditAccount.html')
            else:
                cur.close()
                return render_template('MyAccount.html')
        else:
            return render_template('UpdateAccount.html')
    else:
        return render_template('Login.html')


@app.route('/EditAccount', methods=['GET', 'POST'])
def EditAccount():
    if 'user_email' in session:
        if request.method == 'POST':
            user_email = session['user_email']
            user_nm = request.form['username']
            user_em = request.form['email']
            user_pass = request.form['password']
            cur = conn.cursor()
            cur.execute("UPDATE Netflix_Users SET username=%s, email=%s, password=%s WHERE email=%s",
                        (user_nm, user_em, user_pass, user_email))
            conn.commit()
            cur.close()
            session['user_email'] = user_em
            # Send_Email(user_em, 'Update')
            return render_template('MyAccount.html')
        else:
            return render_template('EditAccount.html')
    else:
        return render_template('Login.html')


@app.route('/ShowAccountDetails', methods=['GET', 'POST'])
def ShowAccountDetails():
    if 'user_email' in session:
        if request.method == 'GET':
            cur = conn.cursor()
            user_em = session['user_email']
            cur.execute("SELECT * FROM Netflix_Users WHERE email LIKE (%s)", (user_em,))
            result = cur.fetchall()
            em_id = result[0][1]
            fileObj = 'https://netflix-aws-bucket.s3.amazonaws.com/Profile_Image_Uploads/'+em_id.partition('@')[0]+'.jpg'
            cur.close()
            return render_template('ShowAccountDetails.html', usern=result[0][0],
                                   email=result[0][1], password=result[0][2], img=fileObj)
    else:
        return render_template('Login.html')


@app.route('/DeleteAccValidate', methods=['GET', 'POST'])
def DeleteAccValidate():
    if 'user_email' in session:
        if request.method == 'POST':
            user_em = request.form['email']
            cur = conn.cursor()
            cur.execute("SELECT username, password FROM Netflix_Users WHERE email LIKE (%s)", (user_em,))
            result = cur.fetchall()
            if result is not None:
                cur.close()
                return render_template('DeleteMyAccount.html')
            else:
                cur.close()
                return render_template('MyAccount.html')
        else:
            return render_template('DeleteAccValidate.html')
    else:
        return render_template('Login.html')


@app.route('/DeleteMyAccount', methods=['GET', 'POST'])
def DeleteMyAccount():
    if 'user_email' in session:
        if request.method == 'POST':
            user_em = request.form['email']
            user_pass = request.form['password']
            cur = conn.cursor()
            cur.execute("DELETE from Netflix_Users WHERE email=%s AND password=%s", (user_em, user_pass))
            s3_client = boto3.resource('s3')
            obj = s3_client.Object(BUCKET_NAME, 'Profile_Image_Uploads/' + user_em.partition('@')[0] + '.jpg')
            obj.delete()
            conn.commit()
            cur.close()
            session.pop('user_email', None)
            # Send_Email(user_em, 'Delete')
            return render_template('Register.html')
        else:
            return render_template('DeleteMyAccount.html')
    else:
        return render_template('Login.html')


def Send_Email(recipient_email, action):
    if action is 'Login':
        msg = Message(subject="LogIn Info: Your Netflix Account",
                      sender="pranavhdev@gmail.com", recipients=[str(recipient_email)])
        msg.body = "Account Login"
        msg.html = ('<h1>Dear User,</h1><br>'
                    '<h3>You Just Logged Into Your Netflix Account?</h3>'
                    '<h3>If This Was Not You, Please Contact Us & Secure Your Account!</h3>'
                    '<h3>Enjoy the Unlimited Catalogue...</h3></br></br></br>'
                    '<h4>@ Netflix - Cares</h4>')
        mail.send(msg)
    elif action is 'Register':
        msg = Message(subject="Register Info: Your Netflix Account",
                      sender="pranavhdev@gmail.com", recipients=[str(recipient_email)])
        msg.body = "Account Registered"
        msg.html = ('<h1>Dear User,</h1><br>'
                    '<h3>Your Netflix Account Is Registered And Active.</h3>'
                    '<h3>Netflix Brings You A Wide Catalogue Of Movies And Shows... ENJOY!</h3>'
                    '<h3>We Hope To Bring In Good Content..</h3></br></br></br>'
                    '<h4>@ Netflix - Cares</h4>')
        mail.send(msg)
    elif action is 'Update':
        msg = Message(subject="Update Info: Your Netflix Account",
                      sender="pranavhdev@gmail.com", recipients=[str(recipient_email)])
        msg.body = "Account Updated"
        msg.html = ('<h1>Dear User,</h1><br>'
                    '<h3>Your Netflix Account Has Been Updated.</h3>'
                    '<h3>If This Was Not You, Please Contact Us!</h3>'
                    '<h3>Account Update Was Successful..</h3></br></br></br>'
                    '<h4>@ Netflix - Cares</h4>')
        mail.send(msg)
    elif action is 'Delete':
        msg = Message(subject="Delete Info: Your Netflix Account",
                      sender="pranavhdev@gmail.com", recipients=[str(recipient_email)])
        msg.body = "Account Deleted"
        msg.html = ('<h1>Dear User,</h1><br>'
                    '<h3>Your Netflix Account Is Deleted.</h3>'
                    '<h3>If This Was Not You, Please Contact Us!</h3>'
                    '<h3>We Are Sorry To See You Go..</h3></br></br></br>'
                    '<h4>@ Netflix - Cares</h4>')
        mail.send(msg)
    else:
        print('\n\n> Wrong Code...\n\n')


if __name__ == '__main__':
    app.run()

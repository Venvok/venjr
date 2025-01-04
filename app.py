from flask import Flask, render_template,request
import json,time,string,random, smtplib
from threading import Thread
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

def send_email(receiver_email, user,code):
    sender_email = "evenmeshack17@gmail.com"
    password = "cswu jmhg namk diva"

    server = smtplib.SMTP('smtp.gmail.com' ,587)
    server.starttls()
    server.login(sender_email,password)

    msg = MIMEMultipart()
    msg['Subject'] = "PASSWORD RESET CODES"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    body = f'''
            <html>   
    <body style="text-align: center; padding: 50; margin: 30;  background-color: rgb(52, 46, 46); width: 60%;">
        <h2 style="color: rgb(209, 139, 48);">PASSWORD RESET CODE</h2>
        <p style="color: aqua;"> Hi {user}, Use the following code to reset the forgotten password of   your account<p>
            <p style="color: tomato; font-weight: bold; font-size: 45px; margin-top: -10px;"> {code} </p>
                <p style="color: rgb(171, 165, 171); margin-top: -10px;"> 2025 All Rights Reserved</p>
                <p style="color: #dde812; margin-top: -10px;">Venvok  Service</p>
    </body>    
    </html>  
    '''
    msg.attach(MIMEText(body,'html'))
    server.send_message(msg)
    server.quit()


def gen_code():
    code = [random.choice(string.digits) for _ in range(6)]
    code = "".join(code)
    return code

def load_json(filename):
    with open(filename, "r") as f:
        return json.load(f)
    
def save_json(data,filename):
    with open(filename, "w") as f:
        json.dump(data,f,indent=4)

@app.route('/')
def home():
    return render_template('index.html', message='')

@app.after_request
def add_header(response):
    response.cache_control.no_store = True  # Prevent caching
    response.cache_control.no_cache = True  # Ensure always fresh
    response.headers['Pragma'] = 'no-cache'  # For older browsers
    response.headers['Expires'] = '0'       # Expire immediately
    return response
    
@app.route('/login', methods=['POST'])
def form():
    username = request.form['username']
    password = request.form['password']
    students = load_json('students.json')

    if username != None and password != None:
        if username in students:
            passw = students[username][0].get('password')
            if passw == password:
                time.sleep(2)
                return render_template('home.html', user=username)
            else:
                time.sleep(1)
                return render_template('index.html', message='You have entered Wrong Password')
        else:
            time.sleep(1)
            return  render_template('index.html', message='Account set not found')   
    else:
        home()    

@app.route('/create_account' , methods=['GET'])
def create_account_page():
    time.sleep(2)
    return render_template('create_account.html')

@app.route('/forgot_password' , methods=['GET'])
def forgot_password_page():
    time.sleep(1)
    return render_template('forgot_password.html')

@app.route('/forgot', methods=['POST'])
def forgot_password():
    username = request.form['username']
    students = load_json('students.json')
    
    if username != None:
        if username in students:
            code = gen_code()
            em = students[username][1].get('email')
            two = em[:2]
            last = em[13:]
            full = two + "*******" + last
            email_service = Thread(target=send_email, args=(em,username,code))
            email_service.start()

            codes = load_json('reset_codes.json')
            codes[username] = [
                {'reset_code': code}
            ]
            save_json(codes,'reset_codes.json')
            time.sleep(5)
            return render_template('password_reset.html', email=full , username=username)
        else:
            return render_template('forgot_password.html', message='Sorry this Account is not available')
    else:
        home()    

@app.route('/code_verify' , methods=['POST'])
def verify_code():
    email = request.form['email']
    pin = request.form['pin']   
    username = request.form['username']
    reset_code = load_json('reset_codes.json')
    original_pin = reset_code[username][0].get('reset_code') 

    try:
        if username in reset_code:
            pass
        else:
            home()
    except KeyError:
        home()    

    if email and pin and username:
        if original_pin == pin:
            del reset_code[username]
            save_json(reset_code,'reset_codes.json')
            time.sleep(2)
            return render_template('new_password.html', username = username)
        else:
            time.sleep(2)
            return render_template('password_reset.html', message='INCORRECT PIN' , email=email, username=username)
    else:
        home()    

@app.route('/password_resetter', methods=['POST'])  
def password_resetter():
    password1 = request.form['password1']
    password2 = request.form['password2']
    username = request.form['username']

    if password1 != None and password2 != None and username != None: 
        if password1 != password2:
            time.sleep(0.5)
            return render_template('new_password.html', message='The passwords entered does not match' , username=username)
        else:
            student = load_json('students.json')
            #old_password = student[username][0].get('password')
            student[username][0]['password'] = password2
            save_json(student,'students.json')
            return render_template('password_changed.html')
    else:
        home()    


@app.route('/create', methods=['POST'])
def create_account():
    username = request.form['username'].strip().lower()
    password = request.form['password'].strip()
    email = request.form['email'].strip().lower()

    students = load_json('students.json')

    if username in students:
        time.sleep(1)
        return render_template('create_account.html', message='Username already taken please use another username')
    else:
        for student in students.values():
            if student[1].get('email') == email:
                return render_template('create_account.html', message='Email already registered please use another EMAIL')
            else:    
                students[username] = [
                    {"password": password},
                    {'email': email}
                ]
                save_json(students,'students.json')
                time.sleep(1)
                return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
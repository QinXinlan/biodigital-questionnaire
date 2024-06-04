# -*- coding: utf-8 -*-
"""
Created on Thu May 30 20:59:32 2024

@author: QinXinlanEva
"""

import logging, random, sys
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Configure logging
# logging.basicConfig(filename='applog.log', level=logging.INFO, format='%(asctime)s - %(message)s')

app = Flask(__name__)
app.secret_key = '\xa4H %\xf6\x05=\xbc\xbb\xd2\xeb\xc9|\xed\xe2\xf7a\xd0n\\k\x93\xecc'

# Configuring the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Generate image names from 001.png to 600.png
image_names = [f"{i:03}.png" for i in range(1, 10)] # 601)] # 
options = [i for i in range(0,5)]
# create a seed
seed_value = random.randrange(sys.maxsize)
# print(seed_value)

# Now, Seed the random number generator
random.seed(seed_value)
# Shuffle the image names to randomize their order
random.shuffle(image_names)
# print(image_names)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

# Create database tables
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return redirect(url_for('login'))
    # return redirect(url_for('question', qnum=0))
    # return render_template('question.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        action = request.form.get('action')
        user = User.query.filter_by(username=username).first()
        
        
        if user and not action:
            # Username already exists
            error = "Username already exists. Is that you?<br>用户名已存在。是你吗？"
            return render_template('login.html', error=error, username=username)
        elif action == 'yes':
            session['username'] = username
            return redirect(url_for('question', qnum=0))
        elif action == 'no':
            return redirect(url_for('login'))
        else:
            # New user
            new_user = User(username=username)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect(url_for('question', qnum=0))
        # flash('Username not found. Please register.')
        return redirect(url_for('register'))
    return render_template('login.html')


@app.route('/<int:qnum>', methods=['GET', 'POST'])
def question(qnum):
    total = len(image_names)  # Ensure total is always defined
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':        
        if 'pause' in request.form:
            # return redirect(url_for('pause'))
            return render_template('pause.html', qnum=qnum, total=total)
        answer = request.form.get('answer')
        if answer is None:
            error = "Please select an answer<br>请选择一个答案"
            return render_template('question.html', qnum=qnum, image_name=image_names[qnum], options=options, error=error, total=total)
        
        # Record the time and username when the "Next" button is clicked
        if 'responses' not in session:
            session['responses'] = []
        session['responses'].append({
            'question': image_names[qnum],
            'answer': answer,
            'time': datetime.now().isoformat(),
            'username': session['username'],
            'seed': seed_value
        })
        
        log_responses()
        # Process the answer (store it, etc.)
        if qnum + 1 < total:
            return redirect(url_for('question', qnum=qnum + 1))
        else:
            return redirect(url_for('thanks'))
    
    return render_template('question.html', qnum=qnum, image_name=image_names[qnum], options=options, error=None, total=total)


@app.route('/pause')
def pause():
    # Retrieve the current question number from the URL parameters
    qnum = request.args.get('qnum')
    print("Paused at qnum:", qnum)  
    # Store the current question number in the session
    session['paused_at'] = qnum
    return render_template('pause.html', qnum=qnum)

@app.route('/resume')
def resume():    
    # Check if there is a paused_at value in the session
    # if 'paused_at' in session:
    # Retrieve the stored question number from the session
    qnum = request.args.get('qnum') # session.get('paused_at')
    print("Paused at qnum:", qnum)  # Print qnum for debugging
    if qnum is not None:
        return redirect(url_for('question', qnum=qnum))
    # If there is no paused_at value in the session, redirect to the index
    # return redirect(url_for('index'))

def log_responses():
    log_file = 'responses.log'
    with open(log_file, 'a') as f:
        for response in session.get('responses', []):
            f.write(f"{response['time']} - {response['seed']} - {response['username']} - {response['question']} - {response['answer']}\n")
    session.pop('responses', None)  # Clear the session responses


@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

# if __name__ == '__main__':
#     app.run(debug=True)

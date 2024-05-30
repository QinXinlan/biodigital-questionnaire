# -*- coding: utf-8 -*-
"""
Created on Thu May 30 13:37:17 2024

@author: QinXinlanEva
"""

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('questionnaire.html')

@app.route('/submit', methods=['POST'])
def submit():
    answers = request.form.to_dict()
    # Here you can process the answers, e.g., save to a database or file
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return "Thank you for completing the questionnaire!"

if __name__ == '__main__':
    app.run(debug=True)
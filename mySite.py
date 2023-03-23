# import the necessary packages
from flask import Flask, render_template, redirect, url_for, request,session,Response
from werkzeug import secure_filename
from supportFile import *
import os
import cv2
import pandas as pd
from textclassification import predictDepression,speech_text
import utils
import sqlite3
from datetime import datetime
import json
import pandas as pd
from datetime import datetime
from autocorrect import Speller

#initialize veriable
interest=''
problem=''
text_dep = 0
speech_dep = 0
name = ''
num = ''

spell = Speller(lang='en')

#create an instance of flask
app = Flask(__name__)

app.secret_key = '1234'            #set a secret key for app
app.config["CACHE_TYPE"] = "null"         
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

#define landing page route from home.html
@app.route('/', methods=['GET', 'POST'])
def landing():
	return render_template('home.html')

#define home page route
@app.route('/home', methods=['GET', 'POST'])
def home():
	return render_template('home.html')
#define input page route
'''
@app.route('/input', methods=['GET', 'POST'])
def input():
	if request.method == 'POST':
		if request.form['sub']=='Submit':
			num = request.form['num']
			users = {'Name':request.form['name'],'Email':request.form['email'],'Contact':request.form['num']}
			df = pd.DataFrame(users,index=[0])
			df.to_csv('users.csv',mode='a',header=False)

			sec = {'num':num}
			df = pd.DataFrame(sec,index=[0])
			df.to_csv('secrets.csv')

			return redirect(url_for('video'))

	return render_template('input.html')
'''
@app.route('/input', methods=['GET', 'POST'])
def input():
	
	if request.method == 'POST':
		if request.form['sub']=='Submit':
			num = request.form['num']
			
			users = {'Name':request.form['name'],'Email':request.form['email'],'Contact':request.form['num']}
			df = pd.DataFrame(users,index=[0])
			df.to_csv('users.csv',mode='a',header=False)

			sec = {'num':num}
			df = pd.DataFrame(sec,index=[0])
			df.to_csv('secrets.csv')

			name = request.form['name']
			num = request.form['num']
			email = request.form['email']
			password = request.form['password']
			age = request.form['age']
			gender = request.form['gender']

			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")			
			con = sqlite3.connect('mydatabase.db')
			cursorObj = con.cursor()
			cursorObj.execute("CREATE TABLE IF NOT EXISTS Users (Date text,Name text,Contact text,Email text,password text,age text,gender text)")
			cursorObj.execute("INSERT INTO Users VALUES(?,?,?,?,?,?,?)",(dt_string,name,num,email,password,age,gender))
			con.commit()

			return redirect(url_for('login'))

	return render_template('input.html')

#define login page route
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	global video
	global name
	if request.method == 'POST':
		name = request.form['name']
		password = request.form['password']
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT Name from Users WHERE Name='{name}' AND password = '{password}';")

	
		if(cursorObj.fetchone()):
			return redirect(url_for('home1'))
		else:
			error = "Invalid Credentials Please try again..!!!"
	return render_template('login.html',error=error)

@app.route('/home1', methods=['GET', 'POST'])
def home1():
	return render_template('home1.html')

@app.route('/video', methods=['GET', 'POST'])
def video():
	return render_template('video.html')

@app.route('/video_stream')
def video_stream():
	 return Response(get_frame(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/textmining',methods=['GET', 'POST'])
def textmining():
	global text_dep
	if request.method == 'POST':
		username = request.form["name"]
		email = request.form["email"]
		num = request.form["num"]
		symptoms = request.form["symptoms"]
		print(username)
		print(email)
		print(symptoms)

		# define punctuation
		punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''

		my_str = symptoms

		# To take input from the user
		# my_str = input("Enter a string: ")

		# remove punctuation from the string
		no_punct = ""
		for char in my_str:
			if char not in punctuations:
				no_punct = no_punct + char
		
		symptoms = no_punct
   
		
		utils.export("data/"+username+"-symptoms.txt", symptoms, "w")
		result = predictDepression(username)
		if(result.split(':')[0] == 'Depression Detected'):
			text_dep = 1

		return render_template('textmining.html',name=username,num = num,email=email,symptoms=symptoms,result=result)			    
	return render_template('textmining.html')

@app.route('/voice',methods=['GET','POST'])
def voice():
	global speech_dep
	if request.method == 'POST':
		if request.form['sub'] == 'Speak':
			username = request.form["name"]
			email = request.form["email"]
			num = request.form["num"]
			symptoms = speech_text()
			print(username)
			print(email)
			print(symptoms)

			# define punctuation
			punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''

			my_str = symptoms

			# To take input from the user
			# my_str = input("Enter a string: ")

			# remove punctuation from the string
			no_punct = ""
			for char in my_str:
				if char not in punctuations:
					no_punct = no_punct + char
			
			symptoms = no_punct
		
			utils.export("data/"+username+"-symptoms.txt", symptoms, "w")
			result = predictDepression(username)
			if(result.split(':')[0] == 'Depression Detected'):
				speech_dep = 1
			return render_template('voice.html',name=username,num = num,email=email,symptoms=symptoms,result=result)
	return render_template('voice.html')

@app.route('/result', methods=['GET', 'POST'])
def final_result():
	global text_dep
	global speech_dep
	
	depression = "Video Depression = "+str(vid_dep) + "," + "Text Mining Depression = "+str(text_dep)+","+"Speech Depression = "+str(speech_dep)
	score = ((vid_dep+speech_dep+text_dep)/3)*100
	return render_template('result.html',depression=depression,score=score)

@app.route('/bot', methods=['GET', 'POST'])
def bot():
	state = 0
	global name
	global num
	
	if request.method == 'POST':
		if request.form['sub']=='Submit':
			state = 1
			name = request.form['name']
			num = request.form['num']
			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

			con = sqlite3.connect('mydatabase.db')
			cursorObj = con.cursor()
			cursorObj.execute("CREATE TABLE IF NOT EXISTS botUsers (Date text,Name text,Contact text)")
			cursorObj.execute("INSERT INTO botUsers VALUES(?,?,?)",(dt_string,name,num))
			con.commit()

		if request.form['sub']=='Rate':
			rating = request.form['rate']
			suggestion = request.form['suggestions']
			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

			con = sqlite3.connect('mydatabase.db')
			cursorObj = con.cursor()
			cursorObj.execute("CREATE TABLE IF NOT EXISTS Feedback (Date text,Name text,Contact text,Ratings text,Feedback text)")
			cursorObj.execute("INSERT INTO Feedback VALUES(?,?,?,?,?)",(dt_string,name,num,rating,suggestion))
			con.commit()
			return redirect(url_for('home'))


	#print(state)
	return render_template('bot.html',state = json.dumps(state))


@app.route("/get")
def get_bot_response():
	global interest
	global problem
	user_response = spell(request.args.get('msg'))
	user_response=user_response.lower()
	botResponse = ''
	print(interest,problem)
	if ('bye' not in user_response):
		if any([x in user_response for x in ['thank you','thanks','thanx','ty']]):
			flag=False
			#print("CollegeBot: You are welcome..")
			botResponse = "You are welcome.."
		elif any([x in user_response for x in['financial','health','relationship','Emptiness','Friendshhip issues','career issues']]):
			botResponse = 'Okay, what is your interest? 1. Video 2. Book 3. Quotes 4. Medicine 5.doctor 6.movies 7.songs'
			problem = user_response
		elif any([x in user_response for x in['video','book','quotes','medicine','doctor','movies','songs']]):
			interest = user_response
			if('financial'in problem):
				if('video' in interest):
					botResponse = 'video link: https://youtu.be/JWjb7WoL9WA'
				elif('book' in interest):
					botResponse = 'Book: Rich dad poor dad'
				elif('quotes' in interest):
					botResponse = 'Rich people believe ‘I create my life.’ Poor people believe ‘Life happens to me.'
				elif('Medicine' in interest):
					botResponse = 'Suggested Medicine: Tab xyz'
				else:
					botResponse = 'plz let me know your problem first'
			elif('health' in problem):
				if('video' in interest):
					botResponse = 'video link: https://youtu.be/9-8UN0cPCmQ'
				elif('book' in interest):
					botResponse = 'You are what you eat'
				elif('quotes' in interest):
					botResponse = 'He who has health has hope and he who has hope has everything.'
				elif('Medicine' in interest):
					botResponse = 'Suggested Medicine: Tab xyz'
				else:
					botResponse = 'plz let me know your problem first'	
			elif('relationship' in problem):
				if('video' in interest):
					botResponse = 'video link: https://youtu.be/0uLLuodEFhE'
				elif('book' in interest):
					botResponse = 'Book: Emotion and Relationship'
				elif('quotes' in interest):
					botResponse = 'Every man I meet wants to protect me'
				elif('medicine' in interest):
					botResponse = 'Suggested Medicine: Tab xyz'	
				else:
					botResponse = 'plz let me know your problem first'			
		else:
			if(greeting(user_response)!=None):
				#print("CollgeBot: "+greeting(user_response))
				botResponse = greeting(user_response)
			else:
				#print("CollgeBot: ",end="")
				#print(response(user_response))
				#botResponse = response(user_response)
				#sent_tokens.remove(user_response)
				botResponse = 'I am sorry! I dont understand you'
				
	else:
		flag=False
		#print("CollgeBot: Bye! take care..")
		botResponse = "Bye! take care.."

	#return str(english_bot.get_response(user_response))
	return botResponse

# No caching at all for API endpoints.
@app.after_request
def add_header(response):
	# response.cache_control.no_store = True
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '-1'
	return response


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, threaded=True)

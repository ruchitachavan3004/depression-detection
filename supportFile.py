# adds image processing capabilities
from PIL import Image 
import cv2
import time
from keras.preprocessing import image
import numpy as np
import os
from twilio.rest import Client
import pandas as pd
import io
import random


# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = "AC9d8c7a356e5d0617693282f12c9319a3"
auth_token = "fc6f8d57cd9412e8856b4009a9171ceb"
client = Client(account_sid, auth_token)

count = 0
vid_dep = 0
#--------------------------------Sentiment Analysis Part-----------------------------------------
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

#cap = cv2.VideoCapture(0)
#-----------------------------
#face expression recognizer initialization
from keras.models import model_from_json
model = model_from_json(open("facial_expression_model_structure.json", "r").read())
model.load_weights('facial_expression_model_weights.h5') #load weights
#model._make_predict_function()

emotions = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')

def get_frame():
	global count
	df = pd.read_csv('secrets.csv')
	sec = df.to_dict('list')
	num = sec['num'][0]

	camera_port=0
	camera=cv2.VideoCapture(camera_port) #this makes a web cam object
	time.sleep(2)

	while True:
		ret, img = camera.read()
		print(img.shape)
		
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		
		faces = face_cascade.detectMultiScale(gray, 1.3, 5)

		#print(faces) #locations of detected faces
		
		for (x,y,w,h) in faces:
			
			cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2) #draw rectangle to main image
			
			detected_face = img[int(y):int(y+h), int(x):int(x+w)] #crop detected face
			
			detected_face = cv2.cvtColor(detected_face, cv2.COLOR_BGR2GRAY) #transform to gray scale
			detected_face = cv2.resize(detected_face, (48, 48)) #resize to 48x48
			
			img_pixels = image.img_to_array(detected_face)
			img_pixels = np.expand_dims(img_pixels, axis = 0)
			
			img_pixels /= 255 #pixels are in scale of [0, 255]. normalize all pixels in scale of [0, 1]
			
			predictions = model.predict(img_pixels) #store probabilities of 7 expressions
			
			#find max indexed array 0: angry, 1:disgust, 2:fear, 3:happy, 4:sad, 5:surprise, 6:neutral
			max_index = np.argmax(predictions[0])
			
			emotion = emotions[max_index]

			if(emotion == 'sad'):
					count = count+1
					print(count)
			
			if(count > 15):
				#write emotion text above rectangle
				count = 0
				vid_dep = 1
				cv2.putText(img, " Depression Detected", (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
				message = client.messages \
				.create(
					 body = "https://www.youtube.com/watch?v=2UtwSI7lgkQ",
					 from_='+14696544981',
					 to="+91"+str(num)
				 )

			else:
				cv2.putText(img, emotion + ":" + str(predictions[0][max_index]), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

		imgencode=cv2.imencode('.jpg',img)[1]
		stringData=imgencode.tostring()
		yield (b'--frame\r\n'
			b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')

	del(camera)


# Keyword Matching
GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]

def greeting(sentence):
    """If user's input is a greeting, return a greeting response"""
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

# Generating response
def response(user_response):
    robo_response=''
    sent_tokens.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)

    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    print(idx)
    
    req_tfidf = flat[-2]
    if(req_tfidf==0):
        robo_response=robo_response+"I am sorry! I don't understand you\nPlease ask regarding\n1.Courses\n2.Admission\n3.Fees\netc"
        # Append-adds at last
        file1 = open("unanswered.txt", "a")  # append mode
        file1.write(user_response+"\n\n")
        file1.close()
        return robo_response
    else:
        #robo_response = robo_response+sent_tokens[idx]
        #robo_response = robo_response+data_list[idx]
        if(idx>12):
            idx = idx -1
        if(idx>50):
            idx=idx-1
        if(idx>69):
            idx=idx-1
        robo_response = robo_response+db_df._get_value(idx, 'Answer')
        return robo_response


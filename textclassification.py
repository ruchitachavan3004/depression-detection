import utils                            #existing block of code can be used
import nltk                             #helps to use nlp with 
import speech_recognition as sr

# Initialize the recognizer
r = sr.Recognizer()

def predictDepression(username):
    data = utils.getTrainData()

    def get_words_in_tweets(tweets):	
        all_words = []
        for (words, sentiment) in tweets:
            all_words.extend(words)
        return all_words

    def get_word_features(wordlist):		
    
        wordlist = nltk.FreqDist(wordlist)
        word_features = wordlist.keys()
        return word_features

    word_features = get_word_features(get_words_in_tweets(data))		
    


    def extract_features(document):		
        document_words = set(document)
        features = {}
        for word in word_features:
            #features[word.decode("utf8")] = (word in document_words)
            features[word] = (word in document_words)
        #print(features)
        return features

    allsetlength = len(data)
    print(allsetlength)		
    #training_set = nltk.classify.apply_features(extract_features, data[:allsetlength/10*8])		
    training_set = nltk.classify.apply_features(extract_features, data)
    #test_set = data[allsetlength/10*8:]		
    test_set = data[88:]		
    classifier = nltk.NaiveBayesClassifier.train(training_set)			
    
    def classify(symptoms):
        return(classifier.classify(extract_features(symptoms.split())))
        
            
        
    f = open("data/"+ username+"-symptoms.txt", "r")	
    f = [line for line in f if line.strip() != ""]	
    tot=0
    pos=0
    neg=0
    for symptom in f:
        tot = tot + 1
        result = classify(symptom)
        if(result == "Depression Detected"):
            neg = neg + 1
        print(result)

    pos = tot - neg
    if(neg > pos):
        result = "Depression Detected: " + str((neg/tot)*100) + "%"

        '''
        message = client.messages \
                                .create(
                                        body = "https://www.youtube.com/watch?v=2UtwSI7lgkQ",
                                        from_='+14696544981',
                                        to="+91"+str(num)
                                    )
        '''
    else:
        result = "No Depression Detected"
    return result


def speech_text():	
	
	# Exception handling to handle
	# exceptions at the runtime
	try:
		
		# use the microphone as source for input.
		with sr.Microphone() as source2:
			
			# wait for a second to let the recognizer
			# adjust the energy threshold based on
			# the surrounding noise level
			r.adjust_for_ambient_noise(source2, duration=0.2)
			
			#listens for the user's input
			audio2 = r.listen(source2)
			
			# Using ggogle to recognize audio
			MyText = r.recognize_google(audio2)
			MyText = MyText.lower()

			
			return(MyText)
			
	except sr.RequestError as e:
		return("Could not request results; {0}".format(e))
		
	except sr.UnknownValueError:
		return("unknown error occured")
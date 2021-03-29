# libraries
import random
import numpy as np
import pickle
import json
from flask import Flask, render_template, request
from flask_ngrok import run_with_ngrok
import nltk
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
import csv
lemmatizer = WordNetLemmatizer()


# chat initialization
model = load_model("chatbot_model.h5")
intents = json.loads(open("intents.json").read())
words = pickle.load(open("words.pkl", "rb"))
classes = pickle.load(open("classes.pkl", "rb"))

# Scenario initialization
first_request = []
first_choice_list = ""
first_choice_count = ""
all_list = ""
all_list_count = ""


app = Flask(__name__)
run_with_ngrok(app)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get", methods=["POST"])
def chatbot_response():
    print("---enters chatbot_response()")
    global first_request
    msg = request.form["msg"]
    if msg.startswith('my name is'):
        name = msg[11:]
        # tokenize the pattern
        msg = clean_up_sentence(msg)
        ints = predict_class(msg, model)
        res1 = getResponse(ints, intents)
        res = res1.replace("{n}",name)
    elif msg.startswith('hi my name is'):
        name = msg[14:]
        # tokenize the pattern
        msg = clean_up_sentence(msg)
        ints = predict_class(msg, model)
        res1 = getResponse(ints, intents)
        res = res1.replace("{n}",name)
    elif msg.startswith('i am'):
        name = msg[5:]
        # tokenize the pattern
        msg = clean_up_sentence(msg)
        ints = predict_class(msg, model)
        res1 = getResponse(ints, intents)
        res = res1.replace("{n}",name)
    # if continue from previous conversation
    elif msg.lower() == 'y':
        if first_request:
            print("---continue from previous conversation - y")
            res = f"Found {first_choice_count} students \n " + first_choice_list
    elif msg.lower() == 'n':
        if first_request:
            print("---continue from previous conversation - n")
            res = f"Found {all_list_count} students \n " + all_list
    else:
        # tokenize the pattern
        msg = clean_up_sentence(msg)
        # save pattern to global for next use (if needed)
        first_request = msg
        # predict and get response
        ints = predict_class(msg, model)
        res = getResponse(ints, intents)

    # search student 'function' from json file
    if res == "search_student":
        # res = "searching student..."
        # print("searching student...")
        res = read_csv(msg)

    # print("---return:", res)
    return res


# reading csv file
def read_csv(sentence):
    print("---enters read_csv(sentence)", sentence)
    global first_choice_list
    global first_choice_count
    global all_list
    global all_list_count
    condition_course = ""
    condition_recommend = "not recommended"
    # finding the condition
    for w in sentence:
        if w == 'c85':
            condition_course = 'c85'
        if w == 'c80':
            condition_course = 'c80'
        if w == 'c36':
            condition_course = 'c36'
        if w == 'c35':
            condition_course = 'c35'
        if w == 'c43':
            condition_course = 'c43'
        if w == 'c54':
            condition_course = 'c54'
        if w == 'recommended':
            condition_recommend = 'recommended'
    print(f'Condition Course: {condition_course}\nCondition Recommended: {condition_recommend}')
    # finding result from file
    result = ""
    if condition_course != "":
        with open('finalfinal.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            result_count = 0
            top_20 = 0
            first_choice_count = 0
            choice1 = ""
            choice2 = ""
            choice3 = ""
            for row in csv_reader:
                # print(f"row in csv_reader: {row['UID']}, {row['Choice']}, {row['Course Code']}, {row['Recommended']}, {row['predict_recommend']}")
                line_count += 1
                if line_count == 1:
                    print(f'Column names are {", ".join(row)}')
                if condition_course.upper() == row['Course Code'].upper():
                    if condition_recommend == 'recommended':
                        if row['predict_recommend'] == '1':
                            top_20 += 1
                            if row['Choice'] == '3':
                                if choice3 == "":
                                    choice3 += (row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " + row['Course Code'] + " Recommended: " + row['Recommended'] + " Predict Recommended: " + row['predict_recommend'])
                                else:
                                    choice3 += (" \n " + row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " + row['Course Code'] + " Recommended: " + row['Recommended'] + " Predict Recommended: " + row['predict_recommend'] + " ")
                            if row['Choice'] == '2':
                                if choice2 == "":
                                    choice2 += (row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " + row['Course Code'] + " Recommended: " + row['Recommended'] + " Predict Recommended: " + row['predict_recommend'])
                                else:
                                    choice2 += (" \n " + row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " + row['Course Code'] + " Recommended: " + row['Recommended'] + " Predict Recommended: " + row['predict_recommend'] + " ")
                            if row['Choice'] == '1':
                                if choice1 == "":
                                    choice1 += (row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " + row['Course Code'] + " Recommended: " + row['Recommended'] + " Predict Recommended: " + row['predict_recommend'])
                                else:
                                    choice1 += (" \n " + row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " + row['Course Code'] + " Recommended: " + row['Recommended'] + " Predict Recommended: " + row['predict_recommend'] + " ")
                                first_choice_count += 1
                            result_count += 1
                    elif condition_recommend == "not recommended":
                        top_20 += 1
                        if row['Choice'] == '3':
                            if choice3 == "":
                                # choice3 += (row['UID'][:-2].upper()+" Choice: "+row['Choice'] + " Applied: " + row['Course Code'] + " Recommended: " + row['predict_recommend'])
                                choice3 += (row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " + row['Course Code'] + " Recommended: " + row['Recommended'] + " Predict Recommended: " + row['predict_recommend'])
                            else:
                                choice3 += (" \n "+row['UID'].upper()+" Choice: "+row['Choice'] + " Applied: " + row['Course Code'] + " Recommended: " + row['Recommended'] + " Predict Recommended: " + row['predict_recommend'] +" ")
                        if row['Choice'] == '2':
                            if choice2 == "":
                                choice2 += (row['UID'].upper()+" Choice: "+row['Choice'] + " Applied: " + row['Course Code'] + " Recommended: " + row['Recommended'] + " Predict Recommended: " + row['predict_recommend'])
                            else:
                                choice2 += (" \n "+row['UID'].upper()+" Choice: "+row['Choice'] + " Applied: " + row['Course Code'] + " Recommended: " + row['Recommended'] + " Predict Recommended: " + row['predict_recommend'] +" ")
                        if row['Choice'] == '1':
                            if choice1 == "":
                                choice1 += (row['UID'].upper()+" Choice: "+row['Choice'] + " Applied: " + row['Course Code'] + " Recommended: " + row['Recommended'] + " Predict Recommended: " + row['predict_recommend'])
                            else:
                                choice1 += (" \n "+row['UID'].upper()+" Choice: "+row['Choice'] + " Applied: " + row['Course Code'] + " Recommended: " + row['Recommended'] + " Predict Recommended: " + row['predict_recommend'] +" ")
                            first_choice_count += 1
                        result_count += 1
            result = choice1 + "\n " + choice2 + "\n " + choice3

            # if too many results
            if top_20 > 20:
                first_choice_list = choice1
                all_list = result
                all_list_count = result_count
                result = \
                    f"The list is too long ({result_count} students),\n" \
                    f" would you like to look for students \n who applied 1st choice?(Y/N)"

            # print(f"---result: {result}")
            print(f"---all_list : \n{all_list}")
            print(f'Processed top {top_20} in total.')
            print(f'Processed {first_choice_count} first choices in total.')
            print(f'Processed {result_count} results in total.')
            print(f'Processed {line_count} lines in total.')

    return result


# chat functionalities
def clean_up_sentence(sentence):
    print("---enters clean_up_sentence(sentence)", sentence)
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    print("---return:", sentence_words)
    result_check_sentence = check_sentence(sentence_words)
    return result_check_sentence


def check_sentence(sentence):
    print("---enter check_sentence(sentence)", sentence)
    for i, w in enumerate(sentence):
        print("---i, w in sentence:", i, w)
        if w == 'dit':
        # Information Technology
            sentence[i] = 'c85'
        if w == 'dcs':
        # Infocomm & Security
            sentence[i] = 'c80'
        if w == 'cip':
        # Common ICT Program
            sentence[i] = 'c36'
        if w == 'dbft':
        # Business & Financial Technology
            sentence[i] = 'c35'
        if w == 'dba':
        # Business Intelligence & Analytics (New Professional Competency Model)
            sentence[i] = 'c43'
        if w == 'dsf':
        # Cybersecurity & Digital Forensics
            sentence[i] = 'c54'
    print("---return sentence:", sentence)
    return sentence


# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=True):
    print("---enters bow(sentence,words,show_details=True)", sentence,words)
    # # tokenize the pattern
    # sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0] * len(words)
    # print("---bag: ", bag)
    for s in sentence:
        # print("---s in sentence_words: ", s)
        for i, w in enumerate(words):
            # print("---i, w in enumerate(words): ", i, w)
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                # print("---bag: ", bag)
                print("found in bag: %s" % w)
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)


def predict_class(sentence, model):
    print("---enters predict_class(sentence,model) ", sentence,model)
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(ints, intents_json):
    print("---enters getResponse(ints,intents_json)", ints, intents_json)
    result = ""
    tag = ints[0]["intent"]
    list_of_intents = intents_json["intents"]
    for i in list_of_intents:
        if i["tag"] == tag:
            result = random.choice(i["responses"])
            break

    return result


if __name__ == "__main__":
    app.run()
# libraries
import random
import numpy as np
import pickle
import json
from flask import Flask, render_template, request
# from flask_ngrok import run_with_ngrok
import nltk
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
import csv
lemmatizer = WordNetLemmatizer()


# chat initialization
model = load_model("chatbot_model.h5")
# model = load_model("chatbot_modelTopic.h5")
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
# run_with_ngrok(app)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get", methods=["POST"])
def chatbot_response():
    print("---enters chatbot_response()")
    global first_request
    msg = request.form["msg"]
    res = ''
    condition_topic = ''
    condition_course = ''
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
            res = f"There are {first_choice_count} {condition_course} students {condition_topic}\n " + first_choice_list + "\n\n Anything else I can help you now?"
            first_request = ""
    elif msg.lower() == 'n':
        if first_request:
            print("---continue from previous conversation - n")
            res = f"Found {all_list_count} {condition_course} students {condition_topic}\n " + all_list + "\n\n Anything else I can help you now?"
            first_request = ""
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
        res_done, res, condition_topic, condition_course, condition_recommend = read_csv(msg)
        if res_done == 'yes':
            res += "\n\n Anything else I can help you now?"

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
    condition_topic = ""
    for w in sentence:
        # finding the condition_course
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
        # find condition_recommend
        if w == 'recommended':
            condition_recommend = 'recommended'
        # find condition_topic
        if w == 'topic_1':
            condition_topic = ["5", "7", "9", "10", "14", "17", "19"]
        if w == 'topic_2':
            condition_topic = ["2", "8", "12", "14", "16"]
        if w == 'topic_3':
            condition_topic = ["0", "1", "3", "4", "13"]
        if w == 'topic_4':
            condition_topic = ["6", "11", "15", "18"]

    print(f'Condition Course: {condition_course}'
          f'\nCondition Recommended: {condition_recommend}'
          f'\nCondition Topic: {condition_topic}')
    # finding result from file
    # result = "Please provide a course (dit, dba, dbft, dsf, dcs, cip)"
    # if condition_course != "":
    with open('finalfinal.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        result_count = 0
        top_20 = 0
        first_choice_count = 0
        result_complete = 'yes'
        choice1 = ""
        choice2 = ""
        choice3 = ""
        for row in csv_reader:
            # print(f"row in csv_reader: {row['UID']}, {row['Choice']}, {row['Course Code']}, {row['Recommended']}, {row['predict_recommend']}")
            line_count += 1
            if line_count == 1:
                print(f'Column names are {", ".join(row)}')
            # condition_topic check
            if condition_topic != "":
                for topic in condition_topic:
                    if topic == row['predictedTopic']:
                        # condition_course check
                        if condition_course.upper() == row['Course Code'].upper():
                            # condition_recommend check
                            if condition_recommend == 'recommended':
                                if row['predict_recommend'] == '1':
                                    top_20 += 1
                                    if row['Choice'] == '3':
                                        if choice3 == "":
                                            choice3 += (row['UID'].upper() + " Choice: " + row[
                                                'Choice'] + " Applied: " + row[
                                                            'Course Code'] + " Predict Recommended: " + row[
                                                            'predict_recommend'] + " Predict Topic: " + row[
                                                        'predictedTopic'])
                                        else:
                                            choice3 += (" \n " + row['UID'].upper() + " Choice: " + row[
                                                'Choice'] + " Applied: " + row[
                                                            'Course Code'] + " Predict Recommended: " + row[
                                                            'predict_recommend'] + " Predict Topic: " + row[
                                                        'predictedTopic'] + " ")
                                    if row['Choice'] == '2':
                                        if choice2 == "":
                                            choice2 += (row['UID'].upper() + " Choice: " + row[
                                                'Choice'] + " Applied: " + row[
                                                            'Course Code'] + " Predict Recommended: " + row[
                                                            'predict_recommend'] + " Predict Topic: " + row[
                                                        'predictedTopic'])
                                        else:
                                            choice2 += (" \n " + row['UID'].upper() + " Choice: " + row[
                                                'Choice'] + " Applied: " + row[
                                                            'Course Code'] + " Predict Recommended: " + row[
                                                            'predict_recommend'] + " Predict Topic: " + row[
                                                        'predictedTopic'] + " ")
                                    if row['Choice'] == '1':
                                        if choice1 == "":
                                            choice1 += (row['UID'].upper() + " Choice: " + row[
                                                'Choice'] + " Applied: " + row[
                                                            'Course Code'] + " Predict Recommended: " + row[
                                                            'predict_recommend'] + " Predict Topic: " + row[
                                                        'predictedTopic'])
                                        else:
                                            choice1 += (" \n " + row['UID'].upper() + " Choice: " + row[
                                                'Choice'] + " Applied: " + row[
                                                            'Course Code'] + " Predict Recommended: " + row[
                                                            'predict_recommend'] + " Predict Topic: " + row[
                                                        'predictedTopic'] + " ")
                                        first_choice_count += 1
                                    result_count += 1
                            elif condition_recommend == "not recommended":
                                top_20 += 1
                                if row['Choice'] == '3':
                                    if choice3 == "":
                                        # choice3 += (row['UID'][:-2].upper()+" Choice: "+row['Choice'] + " Applied: " + row['Course Code'] + " Recommended: " + row['predict_recommend'])
                                        choice3 += (row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " +
                                                    row['Course Code'] + " Predict_Topic: " + row[
                                                        'predictedTopic'])
                                    else:
                                        choice3 += (" \n " + row['UID'].upper() + " Choice: " + row[
                                            'Choice'] + " Applied: " + row['Course Code'] + " Predict_Topic: " +
                                                    row['predictedTopic'] + " ")
                                if row['Choice'] == '2':
                                    if choice2 == "":
                                        choice2 += (row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " +
                                                    row['Course Code'] + " Predict_Topic: " + row[
                                                        'predictedTopic'])
                                    else:
                                        choice2 += (" \n " + row['UID'].upper() + " Choice: " + row[
                                            'Choice'] + " Applied: " + row['Course Code'] + " Predict_Topic: " +
                                                    row['predictedTopic'] + " ")
                                if row['Choice'] == '1':
                                    if choice1 == "":
                                        choice1 += (row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " +
                                                    row['Course Code'] + " Predict_Topic: " + row[
                                                        'predictedTopic'])
                                    else:
                                        choice1 += (" \n " + row['UID'].upper() + " Choice: " + row[
                                            'Choice'] + " Applied: " + row['Course Code'] + " Predict_Topic: " +
                                                    row['predictedTopic'] + " ")
                                    first_choice_count += 1
                                result_count += 1
            else:
                # condition_course check
                if condition_course.upper() == row['Course Code'].upper():
                    # condition_recommend check
                    if condition_recommend == 'recommended':
                        if row['predict_recommend'] == '1':
                            top_20 += 1
                            if row['Choice'] == '3':
                                if choice3 == "":
                                    choice3 += (row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " + row['Course Code'] + " Predict Recommended: " + row['predict_recommend'])
                                else:
                                    choice3 += (" \n " + row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " + row['Course Code'] + " Predict Recommended: " + row['predict_recommend'] + " ")
                            if row['Choice'] == '2':
                                if choice2 == "":
                                    choice2 += (row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " + row['Course Code'] + " Predict Recommended: " + row['predict_recommend'])
                                else:
                                    choice2 += (" \n " + row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " + row['Course Code'] + " Predict Recommended: " + row['predict_recommend'] + " ")
                            if row['Choice'] == '1':
                                if choice1 == "":
                                    choice1 += (row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " + row['Course Code'] + " Predict Recommended: " + row['predict_recommend'])
                                else:
                                    choice1 += (" \n " + row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " + row['Course Code'] + " Predict Recommended: " + row['predict_recommend'] + " ")
                                first_choice_count += 1
                            result_count += 1
                    elif condition_recommend == "not recommended":
                        top_20 += 1
                        if row['Choice'] == '3':
                            if choice3 == "":
                                # choice3 += (row['UID'][:-2].upper()+" Choice: "+row['Choice'] + " Applied: " + row['Course Code'] + " Recommended: " + row['predict_recommend'])
                                choice3 += (row['UID'].upper() + " Choice: " + row['Choice'] + " Applied: " + row['Course Code'] + " Predict Recommended: " + row['predict_recommend'])
                            else:
                                choice3 += (" \n "+row['UID'].upper()+" Choice: "+row['Choice'] + " Applied: " + row['Course Code'] + " Predict Recommended: " + row['predict_recommend'] +" ")
                        if row['Choice'] == '2':
                            if choice2 == "":
                                choice2 += (row['UID'].upper()+" Choice: "+row['Choice'] + " Applied: " + row['Course Code'] + " Predict Recommended: " + row['predict_recommend'])
                            else:
                                choice2 += (" \n "+row['UID'].upper()+" Choice: "+row['Choice'] + " Applied: " + row['Course Code'] + " Predict Recommended: " + row['predict_recommend'] +" ")
                        if row['Choice'] == '1':
                            if choice1 == "":
                                choice1 += (row['UID'].upper()+" Choice: "+row['Choice'] + " Applied: " + row['Course Code'] + " Predict Recommended: " + row['predict_recommend'])
                            else:
                                choice1 += (" \n "+row['UID'].upper()+" Choice: "+row['Choice'] + " Applied: " + row['Course Code'] + " Predict Recommended: " + row['predict_recommend'] +" ")
                            first_choice_count += 1
                        result_count += 1
        result = choice1 + "\n " + choice2 + "\n " + choice3

        # if too many results
        if top_20 > 20:
            first_choice_list = choice1
            all_list = result
            all_list_count = result_count
            result_complete = 'no'
            result = \
                f"The list is too long ({result_count} {condition_course} students)," \
                f" would you like to look for students who applied 1st choice?(Y/N)"

        # print(f"---result: {result}")
        # print(f"---all_list : \n{all_list}")
        print(f'Processed top {top_20} in total.')
        print(f'Processed {first_choice_count} first choices in total.')
        print(f'Processed {result_count} results in total.')
        print(f'Processed {line_count} lines in total.')
        print(f'Request Completed? {result_complete}')

    return result_complete, result, condition_topic, condition_course, condition_recommend


# add to result


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
        # sentence = ['some', 'words', 'here']
        print("---i, w in sentence:", i, w)
        # setting condition_course if any
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
        '''
        setting condition_topic
        '''
        for s in [
            # data
            "data", "information", "datum", "data_point",
            # coding
            "cryptography", "coding", "secret_writing", "steganography",
            "code", "code", "encipher", "cipher", "cypher", "encrypt", "inscribe",
            "write_in_code", "gull", "dupe", "slang", "befool", "cod", "fool",
            "put_on", "take_in", "put_one_over", "put_one_across", "tease", "razz",
            "rag", "cod", "tantalize", "tantalise", "bait", "taunt", "twit", "rally", "ride",
            # programming
            "scheduling", "programming", "programing", "programming", "programing",
            "computer_programming", "computer_programing", "program", "programme", "program", "programme",
            # python
            "python", "python", "Python"
        ]:
            if w == s:
                sentence[i] = 'topic_1'

        for s in [
            # achievement
            "accomplishment", "achievement"
        ]:
            if w == s:
                sentence[i] = 'topic_2'

        for s in [
            # participation
            "engagement", "participation", "involvement", "involution", "participation", "involvement"
        ]:
            if w == s:
                sentence[i] = 'topic_3'

        for s in [
            # business
            "business", "concern", "business_concern", "business_organization",
            "business_organisation", "commercial_enterprise", "business_enterprise",
            "business", "occupation", "business", "job", "line_of_work", "line",
            "business", "business", "business", "business", "business_sector", "clientele",
            "patronage", "business", "business", "stage_business", "byplay",
            # certificates
            "certificate", "certification", "credential", "credentials",
            "security", "certificate", "certificate", "certificate",
            # challenges
            "challenge", "challenge", "challenge", "challenge",
            "challenge", "challenge", "dispute", "gainsay", "challenge",
            "challenge", "challenge", "take_exception",
            # cca
            # values
            "values", "value", "value", "value", "economic_value", "value",
            "value", "time_value", "note_value", "value", "value", "prize", "value",
            "treasure", "appreciate", "respect", "esteem", "value", "prize", "prise",
            "measure", "evaluate", "valuate", "assess", "appraise", "value", "rate", "value"
        ]:
            if w == s:
                sentence[i] = 'topic_4'


    print("---return sentence:", sentence)
    return sentence


# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=True):
    print("---enters bow(sentence,words,show_details=True)", sentence)
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
    # print(f"---p: {p}")
    res = model.predict(np.array([p]))[0]
    # print(f"---res: {res}")
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    print(f"---results: {results}")
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    print(f"---return_list: {return_list}")
    return return_list


def getResponse(ints, intents_json):
    print("---enters getResponse(ints,intents_json)", ints)
    result = ""
    tag = ints[0]["intent"]
    list_of_intents = intents_json["intents"]
    for i in list_of_intents:
        if i["tag"] == tag:
            result = random.choice(i["responses"])
            break

    return result


# class ChatBotEae:
#     def __init__(self, sentence):
#         self.sentence = sentence
#
#     def convert_to_course_code(self, sentence):
#         pass
#
#     def












if __name__ == "__main__":
    app.run()

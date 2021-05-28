# libraries
import random
import string
import numpy as np
import pickle
import json
from flask import Flask, render_template, request
# from flask_ngrok import run_with_ngrok
import nltk
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
import csv
from tabulate import tabulate
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
first_choice_count = 0
all_list = ""
all_list_count = ""
gcondition_course = ["", 0]
gcondition_topic = ["", 0]
gcondition_recommended = ["", 0]
gcondition_mentioned = ""
gcontext = ""
compare_one = ''
compare_two = ''
compare_thr = ''
compare_fou = ''
compare_fiv = ''
compare_six = ''

app = Flask(__name__)
# run_with_ngrok(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get", methods=["POST"])
def chatbot_response():
    print("---enters chatbot_response()")
    global first_request
    global gcondition_course
    global gcondition_topic
    global gcondition_recommended
    global gcondition_mentioned
    global gcontext
    print(f"first_request - {first_request}")
    res = ''
    condition_recommend = ''
    condition_course = ''
    msgtopic = ''
    if request.form["msg"] == " ":
        if request.form["continue"] == " " and first_request == "":
            print("Empty")
            msg = ''
            gcontext = ''
        else:
            print("continue first_request(1)")
            first_request = request.form["continue"]
            msgtopic = request.form["topic"]
            gcontext = 'continue'
            print("msg - ", first_request)
    else:
        print("start first_request(1)")
        gcondition_course = ["", 0]
        gcondition_topic = ["", 0]
        gcondition_recommended = ["", 0]
        gcondition_mentioned = ""
        gcontext = 'start'
        first_request = []
        msg = request.form["msg"]
    # msg = request.form["msg"]

    # if continue from previous conversation
    if first_request:
        print("continue first_request(2)")
        # tokenize the pattern
        first_request, condition_course, condition_recommend, condition_mentioned = clean_up_sentence(first_request)
        if gcondition_mentioned != 'none':
            #  remove (who mentioned )
            condition_mentioned = gcondition_mentioned[14:]
        if msgtopic == "topic_1" or msgtopic == "topic_2" or msgtopic == "topic_3" or msgtopic == "topic_4":
            res = msgtopic
        else:
            # predict and get response
            ints = predict_class(first_request, model)
            res = getResponse(ints, intents)
        print(f"first_request - {first_request}, gcontext - {gcontext}, res - {res}")
    else:
        print("start first_request(2)")
        # save pattern to global for next use (if needed)
        first_request = msg
        # tokenize the pattern
        msg, condition_course, condition_recommend, condition_mentioned = clean_up_sentence(msg)
        # predict and get response
        ints = predict_class(msg, model)
        res = getResponse(ints, intents)

    if res == "topic_1" \
            or res == "topic_2" \
            or res == "topic_3" \
            or res == "topic_4" \
            or res == "search_student" \
            or condition_mentioned != 'no':
        res_done, res = read_csv(res, condition_course, condition_recommend, condition_mentioned)
        if gcontext == 'continue':
            if first_request[-1].lower() == 'yes':
                print("---continue first_request(2)(choice)(yes)")
                res = "There are {0}{1}{2}{3}students applied 1st choice {4}<br>" \
                          .format(str(first_choice_count) + " ",
                                  str(gcondition_recommended[0]) + " ",
                                  str(gcondition_topic[0]) + " ",
                                  str(gcondition_course[0]) + " ",
                                  str(gcondition_mentioned) + " ") \
                          .replace('none ', '') + first_choice_list
            else:
                # default no
                print("---continue first_request(2)(choice)(no)")
                res = "There are {0}{1}{2}{3}students{4}<br>" \
                          .format(str(all_list_count) + " ",
                                  str(gcondition_recommended[0]) + " ",
                                  str(gcondition_topic[0]) + " ",
                                  str(gcondition_course[0]) + " ",
                                  str(gcondition_mentioned) + " ") \
                          .replace('none ', '') + all_list
            res += "<br><br>Anything else I can help you now?"
            gcondition_course = ["", 0]
            gcondition_topic = ["", 0]
            gcondition_recommended = ["", 0]
            gcontext = ''
            first_request = []
        elif res_done == 'yes':
            res = "There are {0}{1}{2}{3}students{4}<br>"\
                      .format(str(all_list_count) + " ",
                              str(gcondition_recommended[0]) + " ",
                              str(gcondition_topic[0]) + " ",
                              str(gcondition_course[0]) + " ",
                              str(gcondition_mentioned) + " ") \
                      .replace('none', '') + str(res)
            res += "<br><br>Anything else I can help you now?"
            gcondition_course = ["", 0]
            gcondition_topic = ["", 0]
            gcondition_recommended = ["", 0]
            gcontext = ''
            first_request = []
    elif res == '':
        res += "Sorry, i didnt catch that, could you repeat?"
    else:
        res += "<br><br>Anything else I can help you now?"

    # print("---return:", res)
    return res


# setting condition_topic
def set_condition_topic(condition_topic):
    if condition_topic == 'topic_1':
        condition_topics = ["5", "7", "9", "10", "14", "17", "19"]
        condition_name = 'IT Skills'
    elif condition_topic == 'topic_2':
        condition_topics = ["2", "8", "12", "14", "16"]
        condition_name = 'Achievements'
    elif condition_topic == 'topic_3':
        condition_topics = ["0", "1", "3", "4", "13"]
        condition_name = 'Participation'
    elif condition_topic == 'topic_4':
        condition_topics = ["6", "11", "15", "18"]
        condition_name = 'Others'
    # elif condition_topic == 'search_student':
    else:
        condition_topics = 'no'
        condition_name = 'no'

    for i in ["5", "7", "9", "10", "14", "17", "19"]:
        if i == str(condition_topic):
            condition_name = 'IT Skills'
    for i in ["2", "8", "12", "14", "16"]:
        if i == str(condition_topic):
            condition_name = 'Achievements'
    for i in ["0", "1", "3", "4", "13"]:
        if i == str(condition_topic):
            condition_name = 'Participation'
    for i in ["6", "11", "15", "18"]:
        if i == str(condition_topic):
            condition_name = 'Others'
    return condition_topics, condition_name


# adding to choice1,2,3
def add_to_choice(row, course, recommend, topic, topic_name, choice3, choice2, choice1):
    # print("---enter add_to_choice: course recommend topic:", course, recommend, topic)
    global first_choice_count
    start_sentence = ["UID", "Choice"]

    row_to_be_added = [row['UID'][0:-2].upper().ljust(9), row['Choice']]
    if course == 'nil':
        row_to_be_added += [row['Course Code']]
        start_sentence += ["Applied"]
    if recommend == 'not recommended':
        # row_to_be_added += [row['predict_recommend']]
        if row['predict_recommend'] == '1':
            predict_recommend = 'Yes'
        else:
            predict_recommend = 'No'
        row_to_be_added += [predict_recommend]
        start_sentence += ["Recommended"]
    if topic == 'no':
        topic, topic_name = set_condition_topic(row['predictedTopic'])
        row_to_be_added += [topic_name]
        start_sentence += ["Topic"]
    if row['Final_Writeup'] == '':
        row_to_be_added += ["nil"]
        start_sentence += ["Writeup"]
    else:
        row_to_be_added += [row['Final_Writeup']]
        start_sentence += ["Writeup"]

    if row['Choice'] == '3':
        choice3 += [row_to_be_added]
    if row['Choice'] == '2':
        choice2 += [row_to_be_added]
    if row['Choice'] == '1':
        choice1 += [row_to_be_added]
        first_choice_count += 1

    return first_choice_count, choice3, choice2, choice1, start_sentence


# reading csv file
def read_csv(condition_topic, condition_course, condition_recommend, condition_mentioned):
    print("---enters read_csv(topic, course, recommend, mentioned)",
          condition_topic, condition_course, condition_recommend, condition_mentioned)
    global first_choice_list
    global first_choice_count
    global all_list
    global all_list_count
    global gcondition_course
    global gcondition_recommended
    global gcondition_topic
    global gcondition_mentioned
    global gcontext

    condition_topic, condition_name = set_condition_topic(condition_topic)

    print(f'Condition Course: {condition_course}'
          f'\nCondition Recommended: {condition_recommend}'
          f'\nCondition Topic: {condition_name} | {condition_topic}'
          f'\nCondition Mentioned: {condition_mentioned}')
    choice1 = []
    choice2 = []
    choice3 = []
    start_sentence = []
    with open('finalfinalsortedPredProd.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        result_count = 0
        top_20 = 0
        first_choice_count = 0
        for row in csv_reader:
            line_count += 1
            if line_count == 1:
                print(f'Column names are {", ".join(row)}')
            # condition_mentioned check
            if condition_mentioned != 'no':
                if condition_mentioned.lower() in row['Final_Writeup'].lower():
                    # print("mentioned is in Final_Writeup - condition_mentioned, row", condition_mentioned, row)
                    # condition_topic check
                    if condition_topic != 'no':
                        for topic in condition_topic:
                            # row[6]
                            if topic == row['predictedTopic']:
                                # condition_course check
                                if condition_course != 'nil':
                                    # row[3]
                                    if condition_course.upper() == row['Course Code'].upper():
                                        # condition_recommend check
                                        if condition_recommend == 'recommended':
                                            # row[5]
                                            if row['predict_recommend'] == '1':
                                                top_20 += 1
                                                first_choice_count, choice3, choice2, choice1, start_sentence \
                                                    = add_to_choice(row,
                                                                    condition_course,
                                                                    condition_recommend,
                                                                    condition_topic,
                                                                    condition_name,
                                                                    choice3,
                                                                    choice2,
                                                                    choice1)
                                                result_count += 1
                                        elif condition_recommend == "not recommended":
                                            top_20 += 1
                                            first_choice_count, choice3, choice2, choice1, start_sentence \
                                                = add_to_choice(row,
                                                                condition_course,
                                                                condition_recommend,
                                                                condition_topic,
                                                                condition_name,
                                                                choice3,
                                                                choice2,
                                                                choice1)
                                            result_count += 1
                                elif condition_course == 'nil':
                                    # condition_recommend check
                                    if condition_recommend == 'recommended':
                                        if row['predict_recommend'] == '1':
                                            top_20 += 1
                                            first_choice_count, choice3, choice2, choice1, start_sentence \
                                                = add_to_choice(row,
                                                                condition_course,
                                                                condition_recommend,
                                                                condition_topic,
                                                                condition_name,
                                                                choice3,
                                                                choice2,
                                                                choice1)
                                            result_count += 1
                                    elif condition_recommend == "not recommended":
                                        top_20 += 1
                                        first_choice_count, choice3, choice2, choice1, start_sentence \
                                            = add_to_choice(row,
                                                            condition_course,
                                                            condition_recommend,
                                                            condition_topic,
                                                            condition_name,
                                                            choice3,
                                                            choice2,
                                                            choice1)
                                        result_count += 1
                    else:
                        # condition_course check
                        if condition_course != 'nil':
                            if condition_course.upper() == row['Course Code'].upper():
                                # condition_recommend check
                                if condition_recommend == 'recommended':
                                    if row['predict_recommend'] == '1':
                                        top_20 += 1
                                        first_choice_count, choice3, choice2, choice1, start_sentence \
                                            = add_to_choice(row,
                                                            condition_course,
                                                            condition_recommend,
                                                            condition_topic,
                                                            condition_name,
                                                            choice3,
                                                            choice2,
                                                            choice1)
                                        result_count += 1
                                elif condition_recommend == "not recommended":
                                    top_20 += 1
                                    first_choice_count, choice3, choice2, choice1, start_sentence \
                                        = add_to_choice(row,
                                                        condition_course,
                                                        condition_recommend,
                                                        condition_topic,
                                                        condition_name,
                                                        choice3,
                                                        choice2,
                                                        choice1)
                                    result_count += 1
                        elif condition_course == 'nil':
                            # condition_recommend check
                            if condition_recommend == 'recommended':
                                if row['predict_recommend'] == '1':
                                    top_20 += 1
                                    first_choice_count, choice3, choice2, choice1, start_sentence \
                                        = add_to_choice(row,
                                                        condition_course,
                                                        condition_recommend,
                                                        condition_topic,
                                                        condition_name,
                                                        choice3,
                                                        choice2,
                                                        choice1)
                                    result_count += 1
                            elif condition_recommend == "not recommended":
                                top_20 += 1
                                first_choice_count, choice3, choice2, choice1, start_sentence \
                                    = add_to_choice(row,
                                                    condition_course,
                                                    condition_recommend,
                                                    condition_topic,
                                                    condition_name,
                                                    choice3,
                                                    choice2,
                                                    choice1)
                                result_count += 1

            else:
                # condition_topic check
                if condition_topic != 'no':
                    for topic in condition_topic:
                        # row[6]
                        if topic == row['predictedTopic']:
                            # condition_course check
                            if condition_course != 'nil':
                                # row[3]
                                if condition_course.upper() == row['Course Code'].upper():
                                    # condition_recommend check
                                    if condition_recommend == 'recommended':
                                        # row[5]
                                        if row['predict_recommend'] == '1':
                                            top_20 += 1
                                            first_choice_count, choice3, choice2, choice1, start_sentence \
                                                = add_to_choice(row,
                                                                condition_course,
                                                                condition_recommend,
                                                                condition_topic,
                                                                condition_name,
                                                                choice3,
                                                                choice2,
                                                                choice1)
                                            result_count += 1
                                    elif condition_recommend == "not recommended":
                                        top_20 += 1
                                        first_choice_count, choice3, choice2, choice1, start_sentence \
                                            = add_to_choice(row,
                                                            condition_course,
                                                            condition_recommend,
                                                            condition_topic,
                                                            condition_name,
                                                            choice3,
                                                            choice2,
                                                            choice1)
                                        result_count += 1
                            elif condition_course == 'nil':
                                # condition_recommend check
                                if condition_recommend == 'recommended':
                                    if row['predict_recommend'] == '1':
                                        top_20 += 1
                                        first_choice_count, choice3, choice2, choice1, start_sentence \
                                            = add_to_choice(row,
                                                            condition_course,
                                                            condition_recommend,
                                                            condition_topic,
                                                            condition_name,
                                                            choice3,
                                                            choice2,
                                                            choice1)
                                        result_count += 1
                                elif condition_recommend == "not recommended":
                                    top_20 += 1
                                    first_choice_count, choice3, choice2, choice1, start_sentence \
                                        = add_to_choice(row,
                                                        condition_course,
                                                        condition_recommend,
                                                        condition_topic,
                                                        condition_name,
                                                        choice3,
                                                        choice2,
                                                        choice1)
                                    result_count += 1
                else:
                    # condition_course check
                    if condition_course != 'nil':
                        if condition_course.upper() == row['Course Code'].upper():
                            # condition_recommend check
                            if condition_recommend == 'recommended':
                                if row['predict_recommend'] == '1':
                                    top_20 += 1
                                    first_choice_count, choice3, choice2, choice1, start_sentence \
                                        = add_to_choice(row,
                                                        condition_course,
                                                        condition_recommend,
                                                        condition_topic,
                                                        condition_name,
                                                        choice3,
                                                        choice2,
                                                        choice1)
                                    result_count += 1
                            elif condition_recommend == "not recommended":
                                top_20 += 1
                                first_choice_count, choice3, choice2, choice1, start_sentence \
                                    = add_to_choice(row,
                                                    condition_course,
                                                    condition_recommend,
                                                    condition_topic,
                                                    condition_name,
                                                    choice3,
                                                    choice2,
                                                    choice1)
                                result_count += 1
                    elif condition_course == 'nil':
                        # condition_recommend check
                        if condition_recommend == 'recommended':
                            if row['predict_recommend'] == '1':
                                top_20 += 1
                                first_choice_count, choice3, choice2, choice1, start_sentence \
                                    = add_to_choice(row,
                                                    condition_course,
                                                    condition_recommend,
                                                    condition_topic,
                                                    condition_name,
                                                    choice3,
                                                    choice2,
                                                    choice1)
                                result_count += 1
                        elif condition_recommend == "not recommended":
                            top_20 += 1
                            first_choice_count, choice3, choice2, choice1, start_sentence \
                                = add_to_choice(row,
                                                condition_course,
                                                condition_recommend,
                                                condition_topic,
                                                condition_name,
                                                choice3,
                                                choice2,
                                                choice1)
                            result_count += 1

        result = choice1 + choice2 + choice3

        # modify text, to make it less chucky
        # print('Checking ------ choice1[0] - ', choice1[0])
        for i in range(len(result)):
            splitwords = result[i][-1].split(" ", 10)
            display_words = ' '.join(splitwords[0:10])
            # result[i][-1] = display_words+"..."
            text = result[i][-1].replace('"', '')
            text = text.replace("'", '')
            result[i][-1] = f"<a href=\'javascript:void(0)\' onclick=\'myDisplay(\"{text}\")\'>{display_words+'...'}</a>"
        # print('Checking ------ choice1[0] - ', choice1[0])

        # remember the conditions
        if condition_course == 'nil' or condition_mentioned == '':
            gcondition_course[0] = 'none'
        else:
            gcondition_course[0] = condition_course
        if condition_recommend == 'not recommended':
            gcondition_recommended[0] = 'none'
        else:
            gcondition_recommended[0] = condition_recommend
        if condition_topic == 'no' or condition_mentioned == '':
            gcondition_topic[0] = 'none'
        else:
            gcondition_topic[0] = condition_name
        if condition_mentioned == 'no' or condition_mentioned == '':
            gcondition_mentioned = 'none'
        else:
            gcondition_mentioned = " who mentioned" + condition_mentioned

        print(f'gobal conditions \n'
              f'--- gcondition_course   | {gcondition_course}\n'
              f'--- gcondition_recommend| {gcondition_recommended}\n'
              f'--- gcondition_topic    | {gcondition_topic}\n'
              f'--- gcondition_mentioned| {gcondition_mentioned}')
        # if too many results
        if top_20 > 20:
            first_choice_list = tabulate(choice1, headers=start_sentence, stralign="left")
            all_list = tabulate(result, headers=start_sentence, stralign="left")
            all_list_count = result_count
            result_complete = 'no'
            # filter--------------------
            result = \
                "The list is too long ({0}{1}{2}{3}students)." \
                    .format(str(result_count) + " ",
                            str(gcondition_recommended[0]) + " ",
                            str(gcondition_topic[0]) + " ",
                            str(gcondition_course[0]) + " ").replace('none ', '')
            if gcondition_recommended == ['none', 0]:
                gcondition_recommended[1] += 1
                result += "<br>This list can be further filtered by recommendation. (Select the options below)" \
                          "<br><input id=\"recommended\"   onclick=\"myFunction(\'recommended\', \'recommended\')\"   name=\"recommended\" type=\"radio\" value=\"Recommended Students\"/>" \
                          "<label for=\"recommended\">RECOMMENDED</label>" \
                          "<br><input id=\"norecommended\" onclick=\"myFunction(\'no\', \'recommended\')\"            name=\"recommended\" type=\"radio\" value=\"No Need To Filter Recommendation\" checked/>" \
                          "<label for=\"norecommended\">NO NEED</label>" \
                          "<br>"
            if gcondition_topic == ['none', 0]:
                gcondition_topic[1] += 1
                result += "<br>This list can be further filtered by topics. (Select the options below)" \
                          "<br><input onclick=\"myFunction(\'topic_1\', \'topic\')\" name=\"topic\" id=\"topic_1\" type=\"radio\" value=\"Students with IT Skills\"/>" \
                          "<label for=\"topic_1\">IT SKILLS - DATA, PYTHON, CODING, PROGRAMMING</label>" \
                          "<br><input onclick=\"myFunction(\'topic_2\', \'topic\')\" name=\"topic\" id=\"topic_2\" type=\"radio\" value=\"Students with Achievement\"/>" \
                          "<label for=\"topic_2\">ACHIEVEMENT</label>" \
                          "<br><input onclick=\"myFunction(\'topic_3\', \'topic\')\" name=\"topic\" id=\"topic_3\" type=\"radio\" value=\"Students with  Participation\"/>" \
                          "<label for=\"topic_3\">PARTICIPATION</label>" \
                          "<br><input onclick=\"myFunction(\'topic_4\', \'topic\')\" name=\"topic\" id=\"topic_4\" type=\"radio\" value=\"Other Students\"/>" \
                          "<label for=\"topic_4\">OTHERS - BUSINESS, CERTIFICATE, CCA, CHALLENGES</label>" \
                          "<br><input onclick=\"myFunction(\'no\', \'topic\')\"      name=\"topic\" id=\"notopic\" type=\"radio\" value=\"No Need To Filter Topic\" checked/>" \
                          "<label for=\"notopic\">NO NEED</label>" \
                          "<br>"
            if gcondition_course == ['none', 0]:
                gcondition_course[1] += 1
                result += "<br>This list can be further filtered by course. (Select the options below)" \
                          "<br><input onclick=\"myFunction(\'dbft\', \'course\')\"  name=\"course\" id=\"dbft\"     type=\"radio\" value=\"Students in Diploma of Business & Financial Technology\"/>" \
                          "<label for=\"dbft\">Business & Financial Technology</label>" \
                          "<br><input onclick=\"myFunction(\'cip\', \'course\')\"   name=\"course\" id=\"cip\"      type=\"radio\" value=\"Students in Diploma of Common ICT Program\">" \
                          "<label for=\"cip\">Common ICT Program</label>" \
                          "<br><input onclick=\"myFunction(\'dba\', \'course\')\"   name=\"course\" id=\"dba\"      type=\"radio\" value=\"Students in Diploma of Business Intelligence & Analytics\"/>" \
                          "<label for=\"dba\">Business Intelligence & Analytics</label>" \
                          "<br><input onclick=\"myFunction(\'dsf\', \'course\')\"   name=\"course\" id=\"dsf\"      type=\"radio\" value=\"Students in Diploma of Cybersecurity & Digital Forensics\">" \
                          "<label for=\"dsf\">Cybersecurity & Digital Forensics</label>" \
                          "<br><input onclick=\"myFunction(\'dcs\', \'course\')\"   name=\"course\" id=\"dcs\"      type=\"radio\" value=\"Students in Diploma of Infocomm & Security\"/>" \
                          "<label for=\"dcs\">Infocomm & Security</label>" \
                          "<br><input onclick=\"myFunction(\'dit\', \'course\')\"   name=\"course\" id=\"dit\"      type=\"radio\" value=\"Students in Diploma of Information Technology\"/>" \
                          "<label for=\"dit\">Information Technology</label>" \
                          "<br><input onclick=\"myFunction(\'no\', \'course\')\"    name=\"course\" id=\"nocourse\" type=\"radio\" value=\"No Need To Filter Course\" checked/>" \
                          "<label for=\"nocourse\">NO NEED</label>" \
                          "<br>"

            result += "<br>Would you like to look for students who applied 1st choice? (Select the options below)" \
                      "<br><input onclick=\"myFunction(\'yes\', \'choice\')\" id=\"yeschoice\" name=\"choice\" type=\"radio\" value=\"Yes\"/>" \
                      "<label for=\"yeschoice\">YES</label>" \
                      "<br><input onclick=\"myFunction(\'no\', \'choice\')\"  id=\"nochoice\"  name=\"choice\" type=\"radio\" value=\"No\" checked/>" \
                      "<label for=\"nochoice\">NO NEED</label>" \
                      "<br><input id=\"butclick\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\" value=\"FILTER\"/><br>"
            result += f"<input id=\"firstrequest\" type=\"text\" value=\"{first_request}\" hidden>"
        else:
            all_list_count = result_count
            first_choice_list = tabulate(choice1, headers=start_sentence, stralign="left")
            result = tabulate(result, headers=start_sentence, tablefmt="grid", stralign="left")
            result_complete = 'yes'

        print(f'Processed top {top_20} in total.')
        print(f'Processed {first_choice_count} first choices in total.')
        print(f'Processed {result_count} results in total.')
        print(f'Processed {line_count} lines in total.')
        print(f'Request Completed? {result_complete}')
        print(f'first_request - {first_request}')

    return result_complete, result


# chat functionalities
def clean_up_sentence(sentence):
    print("---enters clean_up_sentence(sentence)", sentence)
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    print("---return:", sentence_words)
    result_check_sentence, condition_course, condition_recommend, condition_mentioned = check_sentence(sentence_words)
    return result_check_sentence, condition_course, condition_recommend, condition_mentioned


# Check sentence for conditions
def check_sentence(sentence):
    condition_course = 'nil'
    condition_recommend = 'not recommended'
    condition_mentioned = 'no'
    print("---enter check_sentence(sentence)", sentence)
    for i, w in enumerate(sentence):
        # sentence = ['some', 'words', 'here']
        print("---i, w in sentence:", i, w)
        # setting condition_course if any
        # Information Technology
        if w == 'dit' or w == 'c85':
            sentence[i] = 'c85'
            condition_course = 'c85'
        # Infocomm & Security
        if w == 'dcs' or w == 'c80':
            sentence[i] = 'c80'
            condition_course = 'c80'
        # Common ICT Program
        if w == 'cip' or w == 'c36':
            sentence[i] = 'c36'
            condition_course = 'c36'
        # Business & Financial Technology
        if w == 'dbft' or w == 'c35':
            sentence[i] = 'c35'
            condition_course = 'c35'
        # Business Intelligence & Analytics (New Professional Competency Model)
        if w == 'dba' or w == 'c43':
            sentence[i] = 'c43'
            condition_course = 'c43'
        # Cybersecurity & Digital Forensics
        if w == 'dsf' or w == 'c54':
            sentence[i] = 'c54'
            condition_course = 'c54'
        '''
        setting condition_recommend
        '''
        if w == 'recommend' or w == 'recommended':
            condition_recommend = 'recommended'
        '''
        setting condition_mentioned
        '''
        if w == 'mentioned' or w == 'mention':
            condition_mentioned = ' '+sentence[i+1]
            sentence[i] = 'wrote'
            sentence[i+1] = ''

    print("---return sentence:", sentence, condition_course, condition_recommend, condition_mentioned)
    return sentence, condition_course, condition_recommend, condition_mentioned


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















if __name__ == "__main__":
    app.run()

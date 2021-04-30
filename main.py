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
gcontext = ""
compare_one = []
compare_two = []

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
    global gcontext
    print(f"first_request - {first_request}")
    # initialize request
    # if first_request:
    #     msg = first_request
    # else:
    #     msg = request.form["msg"]
    if request.form["msg"] == " ":
        if request.form["continue"] == " ":
            print("Empty")
            msg = ''
        else:
            print("continue first_request(1)")
            msg = request.form["continue"]
            print("msg - ", msg)
    else:
        print("start first_request(1)")
        gcondition_course = ["", 0]
        gcondition_topic = ["", 0]
        gcondition_recommended = ["", 0]
        first_request = []
        msg = request.form["msg"]
    # msg = request.form["msg"]
    res = ''
    condition_recommend = ''
    condition_course = ''
    # if continue from previous conversation
    if first_request:
        print("continue first_request(2)")
        # save pattern to global for next use (if needed)
        first_request = ' '.join(first_request) + " " + msg
        # tokenize the pattern
        first_request, condition_course, condition_recommend = clean_up_sentence(first_request)
        if gcontext != "choice":
            if msg == "no":
                msg = ""
            if msg == "topic_1" or msg == "topic_2" or msg == "topic_3" or msg == "topic_4":
                res = msg
            else:
                # predict and get response
                ints = predict_class(first_request, model)
                res = getResponse(ints, intents)
            print(f"first_request - {first_request}, gcontext - {gcontext}, res - {res}")

        else:
            if msg.lower() == 'yes':
                print("---continue first_request(2)(choice)(yes)")
                res = "There are {0}{1}{2}{3}students<br>" \
                          .format(str(first_choice_count) + " ",
                                  str(gcondition_recommended[0]) + " ",
                                  str(gcondition_topic[0]) + " ",
                                  str(gcondition_course[0]) + " ")\
                          .replace('none ', '') + first_choice_list
            else:
                print("---continue first_request(2)(choice)(no)")
                res = "There are {0}{1}{2}{3}students<br>" \
                          .format(str(all_list_count) + " ",
                                  str(gcondition_recommended[0]) + " ",
                                  str(gcondition_topic[0]) + " ",
                                  str(gcondition_course[0]) + " ")\
                          .replace('none', '') + all_list
            gcondition_course = ["", 0]
            gcondition_topic = ["", 0]
            gcondition_recommended = ["", 0]
            first_request = []

    else:
        print("start first_request(2)")
        # tokenize the pattern
        msg, condition_course, condition_recommend = clean_up_sentence(msg)
        # save pattern to global for next use (if needed)
        first_request = msg
        # predict and get response
        ints = predict_class(msg, model)
        res = getResponse(ints, intents)

    if res == "topic_1" or res == "topic_2" or res == "topic_3" or res == "topic_4" or res == "search_student":
        res_done, res = read_csv(res, condition_course, condition_recommend)
        if res_done == 'yes':
            res = "There are {0}{1}{2}{3}students<br>"\
                      .format(str(all_list_count) + " ",
                              str(gcondition_recommended[0]) + " ",
                              str(gcondition_topic[0]) + " ",
                              str(gcondition_course[0]) + " ")\
                      .replace('none', '') + str(res)
            res += "<br><br>Anything else I can help you now?"
    elif res == '':
        res += "Sorry, i didnt catch that, could you repeat?"
    else:
        res += "<br><br>Anything else I can help you now?"

    print("---return:", res)
    return res

# get details
# def more_conversation(condition, context):
#     print(condition, context)
#


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
    if row['predProb'] == '':
        row_to_be_added += ["nil"]
        start_sentence += ["Probability"]
    else:
        row_to_be_added += [row['predProb']]
        start_sentence += ["Probability"]

    if row['Choice'] == '3':
        choice3 += [row_to_be_added]
    if row['Choice'] == '2':
        choice2 += [row_to_be_added]
    if row['Choice'] == '1':
        choice1 += [row_to_be_added]
        first_choice_count += 1

    return first_choice_count, choice3, choice2, choice1, start_sentence




# reading csv file
def read_csv(condition_topic, condition_course, condition_recommend):
    print("---enters read_csv(topic, course, recommend)", condition_topic, condition_course, condition_recommend)
    global first_choice_list
    global first_choice_count
    global all_list
    global all_list_count
    global gcondition_course
    global gcondition_recommended
    global gcondition_topic
    global gcontext

    condition_topic, condition_name = set_condition_topic(condition_topic)

    print(f'Condition Course: {condition_course}'
          f'\nCondition Recommended: {condition_recommend}'
          f'\nCondition Topic: {condition_name} | {condition_topic}')

    # reading result from file
    # with open('finalfinal.csv', mode='r') as csv_file:
    #     csv_reader = sorted(csv_file, key=lambda row: row[7])
    #     csv_reader = csv.DictReader(csv_reader)
    with open('finalfinalsortedPredProd.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        result_count = 0
        top_20 = 0
        first_choice_count = 0
        choice1 = []
        choice2 = []
        choice3 = []
        start_sentence = []
        for row in csv_reader:
            line_count += 1
            if line_count == 1:
                print(f'Column names are {", ".join(row)}')
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
                                        first_choice_count, choice3, choice2, choice1, start_sentence = add_to_choice(row,
                                                                                                      condition_course,
                                                                                                      condition_recommend,
                                                                                                      condition_topic,
                                                                                                      condition_name,
                                                                                                      choice3,
                                                                                                      choice2, choice1)
                                        result_count += 1
                                elif condition_recommend == "not recommended":
                                    top_20 += 1
                                    first_choice_count, choice3, choice2, choice1, start_sentence = add_to_choice(row, condition_course,
                                                                                                  condition_recommend,
                                                                                                  condition_topic,
                                                                                                  condition_name,
                                                                                                  choice3,
                                                                                                  choice2, choice1)
                                    result_count += 1
                        elif condition_course == 'nil':
                            # condition_recommend check
                            if condition_recommend == 'recommended':
                                if row['predict_recommend'] == '1':
                                    top_20 += 1
                                    first_choice_count, choice3, choice2, choice1, start_sentence = add_to_choice(row, condition_course,
                                                                                                  condition_recommend,
                                                                                                  condition_topic,
                                                                                                  condition_name,
                                                                                                  choice3,
                                                                                                  choice2, choice1)
                                    result_count += 1
                            elif condition_recommend == "not recommended":
                                top_20 += 1
                                first_choice_count, choice3, choice2, choice1, start_sentence = add_to_choice(row, condition_course,
                                                                                              condition_recommend,
                                                                                              condition_topic,
                                                                                              condition_name, choice3,
                                                                                              choice2, choice1)
                                result_count += 1
            else:
                # condition_course check
                if condition_course != 'nil':
                    if condition_course.upper() == row['Course Code'].upper():
                        # condition_recommend check
                        if condition_recommend == 'recommended':
                            if row['predict_recommend'] == '1':
                                top_20 += 1
                                first_choice_count, choice3, choice2, choice1, start_sentence = add_to_choice(row,
                                                                                              condition_course,
                                                                                              condition_recommend,
                                                                                              condition_topic,
                                                                                              condition_name,
                                                                                              choice3,
                                                                                              choice2, choice1)
                                result_count += 1
                        elif condition_recommend == "not recommended":
                            top_20 += 1
                            first_choice_count, choice3, choice2, choice1, start_sentence = add_to_choice(row, condition_course,
                                                                                          condition_recommend,
                                                                                          condition_topic,
                                                                                          condition_name,
                                                                                          choice3,
                                                                                          choice2, choice1)
                            result_count += 1
                elif condition_course == 'nil':
                    # condition_recommend check
                    if condition_recommend == 'recommended':
                        if row['predict_recommend'] == '1':
                            top_20 += 1
                            first_choice_count, choice3, choice2, choice1, start_sentence = add_to_choice(row, condition_course,
                                                                                          condition_recommend,
                                                                                          condition_topic,
                                                                                          condition_name,
                                                                                          choice3,
                                                                                          choice2, choice1)
                            result_count += 1
                    elif condition_recommend == "not recommended":
                        top_20 += 1
                        first_choice_count, choice3, choice2, choice1, start_sentence = add_to_choice(row, condition_course,
                                                                                      condition_recommend,
                                                                                      condition_topic,
                                                                                      condition_name,
                                                                                      choice3,
                                                                                      choice2, choice1)
                        result_count += 1
        result = choice1 + choice2 + choice3

        # remember the conditions
        if condition_course == 'nil':
            gcondition_course[0] = 'none'
        else:
            gcondition_course[0] = condition_course
        if condition_recommend == 'not recommended':
            gcondition_recommended[0] = 'none'
        else:
            gcondition_recommended[0] = condition_recommend
        if condition_topic == 'no':
            gcondition_topic[0] = 'none'
        else:
            gcondition_topic[0] = condition_name

        # if too many results
        if top_20 > 20:
            # first_choice_list = choice1
            # all_list = result
            first_choice_list = tabulate(choice1, headers=start_sentence, tablefmt="pretty")
            all_list = tabulate(result, headers=start_sentence, tablefmt="pretty")
            all_list_count = result_count
            result_complete = 'no'
            result = \
                "The list is too long ({0}{1}{2}{3}students)."\
                    .format(str(result_count)+" ",
                            str(gcondition_recommended[0]) + " ",
                            str(gcondition_topic[0]) + " ",
                            str(gcondition_course[0]) + " ").replace('none ', '')
            if gcondition_recommended == ['none', 0]:
                gcondition_recommended[1] += 1
                gcontext = "recommended"
                result += "<br>This list can be further filtered by recommendation. (Click the button)" \
                          "<br><input value=\"recommended\" onclick=\"myFunction(\'Recommended Students\', \'recommended\')\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\"/>"\
                          "<br><input value=\"no need\" onclick=\"myFunction(\'No Need To Filter\', \'no\')\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\"/>" \
                          "<br>"
            elif gcondition_topic == ['none', 0]:
                gcondition_topic[1] += 1
                gcontext = "topic"
                result += "<br>This list can be further filtered by topics. (Click the button)" \
                          "<br><input onclick=\"myFunction(\'Students with IT Skills\', \'topic_1\')\" value=\"IT Skills - Data, Python, Coding, Programming\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\"/>" \
                          "<br><input onclick=\"myFunction(\'Students with Achievement\', \'topic_2\')\" value=\"Achievement\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\"/>" \
                          "<br><input onclick=\"myFunction(\'Students with  Participation\', \'topic_3\')\" value=\"Participation\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\"/>" \
                          "<br><input onclick=\"myFunction(\'Other Students\', \'topic_4\')\" value=\"Others - Business, Certificate, CCA, Challenges\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\"/>" \
                          "<br><input onclick=\"myFunction(\'No Need To Filter\', \'no\')\" value=\"no need\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\"/>" \
                          "<br>"
            elif gcondition_course == ['none', 0]:
                gcondition_course[1] += 1
                gcontext = "course"
                result += "<br>This list can be further filtered by course. (Click the button)" \
                          "<br><input onclick=\"myFunction(\'Students in Diploma of Business & Financial Technology\', \'dbft\')\" value=\"Business & Financial Technology\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\"/>" \
                          "<br><input onclick=\"myFunction(\'Students in Diploma of Common ICT Program\', \'cip\')\" value=\"Common ICT Program\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\"/>" \
                          "<br><input onclick=\"myFunction(\'Students in Diploma of Business Intelligence & Analytics\', \'dba\')\" value=\"Business Intelligence & Analytics\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\"/>" \
                          "<br><input onclick=\"myFunction(\'Students in Diploma of Cybersecurity & Digital Forensics\', \'dsf\')\" value=\"Cybersecurity & Digital Forensics\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\"/>" \
                          "<br><input onclick=\"myFunction(\'Students in Diploma of Infocomm & Security\', \'dcs\')\" value=\"Infocomm & Security\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\"/>" \
                          "<br><input onclick=\"myFunction(\'Students in Diploma of Information Technology\', \'dit\')\" value=\"Information Technology\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\"/>" \
                          "<br><input onclick=\"myFunction(\'No Need To Filter\', \'no\')\" value=\"no need\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\"/>" \
                          "<br>"
            else:
                gcontext = "choice"
                result += "<br>Would you like to look for students who applied 1st choice? (Click the button)" \
                          "<br><input onclick=\"myFunction(\'Yes\', \'yes\')\" value=\"yes\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\"/>" \
                          "<br><input onclick=\"myFunction(\'No\', \'no\')\" value=\"no need\" type=\"submit\" class=\"btn btn-info form-control\" form=\"clickingForm\"/>" \
                          "<br>"
        else:
            all_list_count = result_count
            result = tabulate(result, headers=start_sentence, tablefmt="pretty")
            result_complete = 'yes'

        print(f'Processed top {top_20} in total.')
        print(f'Processed {first_choice_count} first choices in total.')
        print(f'Processed {result_count} results in total.')
        print(f'Processed {line_count} lines in total.')
        print(f'Request Completed? {result_complete}')
        print(f'first_request - {first_request}')

    return result_complete, result


# add to result


# chat functionalities
def clean_up_sentence(sentence):
    print("---enters clean_up_sentence(sentence)", sentence)
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    print("---return:", sentence_words)
    result_check_sentence, condition_course, condition_recommend = check_sentence(sentence_words)
    return result_check_sentence, condition_course, condition_recommend


# Check sentence for conditions
def check_sentence(sentence):
    condition_course = 'nil'
    condition_recommend = 'not recommended'
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
        # '''
        # setting condition_topic
        # '''
        # for s in [
        #     # data
        #     "data", "information", "datum", "data_point",
        #     # coding
        #     "cryptography", "coding", "secret_writing", "steganography",
        #     "code", "code", "encipher", "cipher", "cypher", "encrypt", "inscribe",
        #     "write_in_code", "gull", "dupe", "slang", "befool", "cod", "fool",
        #     "put_on", "take_in", "put_one_over", "put_one_across", "tease", "razz",
        #     "rag", "cod", "tantalize", "tantalise", "bait", "taunt", "twit", "rally", "ride",
        #     # programming
        #     "scheduling", "programming", "programing", "programming", "programing",
        #     "computer_programming", "computer_programing", "program", "programme", "program", "programme",
        #     # python
        #     "python", "python", "Python"
        # ]:
        #     if w == s:
        #         sentence[i] = 'topic_1'
        #
        # for s in [
        #     # achievement
        #     "accomplishment", "achievement"
        # ]:
        #     if w == s:
        #         sentence[i] = 'topic_2'
        #
        # for s in [
        #     # participation
        #     "engagement", "participation", "involvement", "involution", "participation", "involvement"
        # ]:
        #     if w == s:
        #         sentence[i] = 'topic_3'
        #
        # for s in [
        #     # business
        #     "business", "concern", "business_concern", "business_organization",
        #     "business_organisation", "commercial_enterprise", "business_enterprise",
        #     "business", "occupation", "business", "job", "line_of_work", "line",
        #     "business", "business", "business", "business", "business_sector", "clientele",
        #     "patronage", "business", "business", "stage_business", "byplay",
        #     # certificates
        #     "certificate", "certification", "credential", "credentials",
        #     "security", "certificate", "certificate", "certificate",
        #     # challenges
        #     "challenge", "challenge", "challenge", "challenge",
        #     "challenge", "challenge", "dispute", "gainsay", "challenge",
        #     "challenge", "challenge", "take_exception",
        #     # cca
        #     "cca", "Co-curricular activities",
        #     # values
        #     "values", "value", "value", "value", "economic_value", "value",
        #     "value", "time_value", "note_value", "value", "value", "prize", "value",
        #     "treasure", "appreciate", "respect", "esteem", "value", "prize", "prise",
        #     "measure", "evaluate", "valuate", "assess", "appraise", "value", "rate", "value"
        # ]:
        #     if w == s:
        #         sentence[i] = 'topic_4'


    print("---return sentence:", sentence, condition_course, condition_recommend)
    return sentence, condition_course, condition_recommend


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

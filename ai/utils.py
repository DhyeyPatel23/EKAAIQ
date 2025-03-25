import json
import os
from django.utils.timezone import now
from django.utils import timezone


# def load_questions():
#     # Adjust the path based on where your JSON file is stored
#     json_path = os.path.join(os.path.dirname(__file__), 'data', 'questions.json')
#     with open(json_path, 'r') as file:
#         questions = json.load(file)
#     return questions

####################################################################################
#                                   python                                         #
####################################################################################

def python_easy():
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'python' , 'py_easy.json')
    with open(json_path, 'r') as file:
        questions = json.load(file)
    return questions

def python_inter():
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'python' , 'py_inter.json')
    with open(json_path, 'r') as file:
        questions = json.load(file)
    return questions

def python_adv():
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'python' , 'py_adv.json')
    with open(json_path, 'r') as file:
        questions = json.load(file)
    return questions

####################################################################################
#                                       java                                       #
####################################################################################

def java_easy():
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'java' , 'jv_easy.json')
    with open(json_path, 'r') as file:
        questions = json.load(file)
    return questions

def java_inter():
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'java' , 'jv_inter.json')
    with open(json_path, 'r') as file:
        questions = json.load(file)
    return questions

def java_adv():
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'java' , 'jv_adv.json')
    with open(json_path, 'r') as file:
        questions = json.load(file)
    return questions

####################################################################################
#                                        c                                         #
####################################################################################

def c_easy():
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'c' , 'c_easy.json')
    with open(json_path, 'r') as file:
        questions = json.load(file)
    return questions

def c_inter():
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'c' , 'c_inter.json')
    with open(json_path, 'r') as file:
        questions = json.load(file)
    return questions

def c_adv():
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'c' , 'c_adv.json')
    with open(json_path, 'r') as file:
        questions = json.load(file)
    return questions

def check_quiz_status(start_time, end_time):
    """
    Checks if the quiz is active, upcoming, or expired based on the current time.

    Returns:
        - "active" if the quiz is currently running.
        - "upcoming" if the quiz has not started yet.
        - "expired" if the quiz has ended.
    """
    current_time = now()

    print("Current time: ", current_time)

    current_time = timezone.localtime(current_time)

    print("Current time: ", current_time)

    if start_time is None:
        # If start_time is None, consider the quiz as started
        if end_time is None:
            # If both start_time and end_time are None, the quiz is available
            return "active"
        elif end_time > current_time:
            return "active"
        else:
            return "expired"

    if start_time > current_time:
        return "upcoming"
    elif start_time <= current_time <= end_time:
        return "active"
    else:
        return "expired"

from gradio_client import Client
import json
from django.http import JsonResponse

def get_generated_quiz(text , count):
    client = Client("Dev1559/quizbot")
    result = client.predict(
            message= f"""
                Generate exactly {count} multiple-choice questions (MCQs) in **strict** JSON format based on the following text:

                {text}

                ### **Requirements:**  
                - **Generate exactly** {count} MCQs, no more and no less.  
                - Each question **must have exactly** 4 options.  
                - Ensure the correct answer is **always accurate** based on the given text.  
                - The correct answer should be formatted as `"option1"`, `"option2"`, `"option3"`, or `"option4"`.  
                - Do **not** include duplicate or factually incorrect answers.  
                - Use `"mcqs"` (plural) as the JSON key, **not** `"mcq"`.  
                - Ensure proper JSON syntax: brackets, commas, and quotation marks should be correctly placed.  
                - **Validate the JSON** before submitting to ensure it is well-formed and free of syntax errors.  
                - Do **not** hallucinate or assume facts not present in the provided text.  

                ### **JSON Output Format Example:**  
                ```json
                {{
                "mcqs": [
                    {{
                    "question": "What is the capital of France?",
                    "options": ["Paris", "London", "Berlin", "Rome"],
                    "correct_answer": "option1"
                    }},
                    {{
                    "question": "Which programming language is known for web development?",
                    "options": ["Python", "JavaScript", "C++", "Swift"],
                    "correct_answer": "option2"
                    }}
                ]
                }}

            """,
            system_message="You are an AI assistant specialized in generating accurate and well-structured multiple-choice questions in strict JSON format. Always ensure factual correctness, validate JSON syntax, and follow the given constraints strictly.",
            max_tokens=4096,
            temperature=0.2,
            top_p=0.9,
            api_name="/chat"
    )
    try : 
        response_content = result
        json_start = response_content.find("{")
        json_end = response_content.rfind("}") + 1
        cleaned_json = response_content[json_start:json_end]
        print(cleaned_json)

        parsed_json = json.loads(cleaned_json)

        # Ensure "mcqs" exists in the parsed data
        return parsed_json.get("mcqs", [])

    except json.JSONDecodeError as e:
            print("JSON Decode Error:", e)
            return []

def generate_question(text, offset = 1, count=1):
    client = Client("Dev1559/quizbot")
    result = client.predict(
            message= f"""
                Generate exactly {count} **unique** multiple-choice questions (MCQs) in **strict** JSON format based on the following text:  

                {text}  

                ### **Uniqueness Requirement:**  
                - We **already have** {offset} questions.  
                - **Do NOT repeat or generate similar** questions to the oneserated question must be **completely different** from  already present.  
                - Each genpreviously generated ones.  

                ### **General Requirements:**  
                - **Generate exactly** {count} MCQs, no more and no less.  
                - Each question **must have exactly** 4 options.  
                - The correct answer should be formatted as `"option1"`, `"option2"`, `"option3"`, or `"option4"`.  
                - Ensure **factual correctness** based on the given text.  
                - Use `"mcqs"` (plural) as the JSON key, **not** `"mcq"`.  
                - Ensure proper JSON syntax: brackets, commas, and quotation marks should be correctly placed.  
                - **Validate the JSON** before submitting to ensure it is well-formed and free of syntax errors.  
                - **Do not hallucinate or assume facts** not present in the provided text.  

                ### **JSON Output Format Example:**  
                ```json
                {{
                "mcqs": [
                    {{
                    "question": "Which planet is known as the Red Planet?",
                    "options": ["Earth", "Mars", "Jupiter", "Venus"],
                    "correct_answer": "option2"
                    }},
                    {{
                    "question": "Who wrote 'Romeo and Juliet'?",
                    "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
                    "correct_answer": "option2"
                    }}
                ]
                }}

            """,
            system_message="You are an AI assistant specialized in generating accurate and unique multiple-choice questions in strict JSON format. Always ensure factual correctness, validate JSON syntax, and follow the given constraints strictly. Do not repeat any previously generated questions.",
            max_tokens=4096,
            temperature=0.2,
            top_p=0.9,
            api_name="/chat"
    )
    try : 
        response_content = result
        json_start = response_content.find("{")
        json_end = response_content.rfind("}") + 1
        cleaned_json = response_content[json_start:json_end]
        print(cleaned_json)

        question = json.loads(cleaned_json)
        return question.get("mcqs", [])

    except json.JSONDecodeError as e:
            print("JSON Decode Error:", e)
            return []


##
"""
Generate {count} multiple-choice questions in JSON format from the following text:
                    
                    {text}
                    
                    Ensure each question has:
                    - Generate EXACTLY {count} questions, no more and no less
                    - 4 options
                    - The correct answer should be mentioned as (option1, option2, option3, or option4)
                    - make sure to open and close the brackets properly.
                    - JSON format strictly as shown below:
                    
                    {{
                        "mcqs": [
                            {{
                                "question": "What is the capital of France?",
                                "options": ["Paris", "London", "Berlin", "Rome"],
                                "correct_answer": "option1"
                            }},
                            {{
                                "question": "What is the capital of India?",
                                "options": ["Gujarat", "Mumbai", "Dehli", "Kashmir"],
                                "correct_answer": "option3"
                            }},
                            {{
                                "question": "What is the capital of Australia?",
                                "options": ["Paris", "London", "Berlin", "Canberra"],
                                "correct_answer": "option4"
                            }},
                            ...
                        ]
                    }}


                    generate exact {count} mcq in such way .
                    make sure to open and close the brackets properly.
                    verify the json format before submitting.
                    make sure to use word "mcqs" not "mcq" in json.
"""
##

###
"""Generate {count} multiple-choice questions in JSON format from the following text:
                    
                    {text}

                    These questions should be different from previous questions.
                    We already have {offset} questions, so make these completely different.
                    
                    Ensure each question has:
                    - 4 options
                    - The correct answer should be mentioned as (option1, option2, option3, or option4)
                    - make sure to open and close the brackets properly.
                    - JSON format strictly as shown below:
                    
                    {{
                        "mcqs": [
                            {{
                                "question": "What is the capital of France?",
                                "options": ["Paris", "London", "Berlin", "Rome"],
                                "correct_answer": "option1"
                            }},
                            {{
                                "question": "What is the capital of India?",
                                "options": ["Gujarat", "Mumbai", "Dehli", "Kashmir"],
                                "correct_answer": "option3"
                            }},
                            {{
                                "question": "What is the capital of Australia?",
                                "options": ["Paris", "London", "Berlin", "Canberra"],
                                "correct_answer": "option4"
                            }},
                            ...
                        ]
                    }}

                    generate {count} mcq in such way .
                    make sure to open and close the brackets properly.
                    verify the json format before submitting.
                    Use "mcqs" as the key name
"""
###

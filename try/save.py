import json

# Step 1: Create a list of Python-based MCQs
questions_data = [
    {
        "question": "What is the output of print(2**3)?",
        "options": ["6", "8", "9", "12"],
        "answer": "8"
    },
    {
        "question": "Which of the following is a Python keyword?",
        "options": ["for", "while", "loop", "function"],
        "answer": "for"
    },
    {
        "question": "What does the 'len()' function do?",
        "options": [
            "Returns the length of an object",
            "Returns a list of elements",
            "Checks the type of object",
            "None of the above"
        ],
        "answer": "Returns the length of an object"
    },
    {
        "question": "Which of the following is used to define a block of code in Python?",
        "options": ["Brackets", "Indentation", "Parentheses", "Quotes"],
        "answer": "Indentation"
    },
    {
        "question": "What is the correct file extension for Python files?",
        "options": [".pt", ".pyt", ".pyth", ".py"],
        "answer": ".py"
    },
    {
        "question": "Which operator is used to assign a value to a variable in Python?",
        "options": ["=", "==", ":=", "<-"],
        "answer": "="
    },
    {
        "question": "What is the output of print(10 // 3)?",
        "options": ["3", "3.33", "4", "10"],
        "answer": "3"
    },
    {
        "question": "Which function is used to read input from the user in Python?",
        "options": ["input()", "read()", "get()", "scan()"],
        "answer": "input()"
    },
    {
        "question": "Which of the following is not a valid Python data type?",
        "options": ["list", "set", "array", "tuple"],
        "answer": "array"
    },
    {
        "question": "How do you start a comment in Python?",
        "options": ["//", "/*", "#", "<!--"],
        "answer": "#"
    }
]

# Step 2: Save the questions data to a JSON file
with open('python_mcqs.json', 'w') as file:
    json.dump(questions_data, file, indent=4)

print("Questions have been saved to 'python_mcqs.json'")

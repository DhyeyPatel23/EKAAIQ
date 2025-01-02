import random
import json

# Step 1: Load the stored questions from the JSON file
with open('python_mcqs.json', 'r') as file:
    questions_data = json.load(file)

# Step 2: Select 10 random questions
random_questions = random.sample(questions_data, 10)

print(random_questions)

# Step 3: Save the random questions to a new JSON file
# with open('random_python_mcqs.json', 'w') as file:
#     json.dump(random_questions, file, indent=4)

# print("10 random questions have been saved to 'random_python_mcqs.json'")

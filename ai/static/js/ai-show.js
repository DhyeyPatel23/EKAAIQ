document.addEventListener("DOMContentLoaded", function () {
    let questionCounter = document.querySelectorAll('.question-container').length;
    var STATIC_URL = "/static/";


    document.querySelector('.add-question').addEventListener('click', function () {
        // Fetch new question from server
        fetch('/a/add_quiz/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({})
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(error => {
                    throw new Error(error.error || 'Failed to load question');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.questions && data.questions.length > 0) {
                const question = data.questions[0]; // Assuming add_questions contains one question
                questionCounter++;
                const questionTemplate = `
                    <div class="question-container">
                        <h2>Question ${questionCounter}</h2>
                        <input type="text" name="questions" value="${question.question}" placeholder="Enter Question here..." required>
                        
                        <img src="${STATIC_URL}${question.image_loc}" alt="" style="max-width: 500px;">
                        <input type="text" name="img" value="${question.image_loc}" hidden>
                        <br>

                        Option 1 : <input type="text" name="options" value="${question.options[0]}" placeholder="Option A" required>
                        <br>
                        Option 2 : <input type="text" name="options" value="${question.options[1]}" placeholder="Option B" required>
                        <br>
                        Option 3 : <input type="text" name="options" value="${question.options[2]}" placeholder="Option C" required>
                        <br>
                        Option 4 : <input type="text" name="options" value="${question.options[3]}" placeholder="Option D" required>


                        <br>
                        Correct Answer :
                        <br>
                        <select name="correct_options">
                            <option value="${question.answer}" >${question.answer}</option>
                        </select>
                        <br>

                        <button type="button" class="delete-question">Delete Question</button>
                    </div>
                `;
                document.querySelector('#question-list').insertAdjacentHTML('beforeend', questionTemplate);
                attachDeleteEvents();
                scrollToBottom();
            } else {
                console.error('Failed to load question:', data.error);
            }
        })
        .catch(error => console.error('Error:', error.message));
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function attachDeleteEvents() {
        document.querySelectorAll('.delete-question').forEach(button => {
            button.removeEventListener('click', handleDelete); // Remove previous event listeners to prevent duplicates
            button.addEventListener('click', handleDelete);
        });
    }

    // function handleDelete() {
    //     this.parentElement.remove(); // Remove the question container
    //     updateQuestionNumbers(); // Update question numbers after deletion
    // }

    function handleDelete() {
        const questionContainer = this.parentElement;
        questionContainer.remove(); // Remove the question container

        // Reindex remaining questions
        updateQuestionNumbers();

        // Update session storage or make an AJAX call to update session on the server
        updateSessionData();
    }

    // function handleDelete() {
    //     const questionText = this.parentElement.querySelector('input[name="questions"]').value;
        
    //     // Remove the question container from the DOM
    //     this.parentElement.remove();
    
    //     // Send an AJAX request to update session data on the server
    //     fetch('/a/remove_quiz_question/', {
    //         method: 'POST',
    //         headers: {
    //             'Content-Type': 'application/json',
    //             'X-CSRFToken': getCookie('csrftoken'),
    //             'X-Requested-With': 'XMLHttpRequest'
    //         },
    //         body: JSON.stringify({ question: questionText })
    //     }).then(response => {
    //         if (!response.ok) {
    //             return response.json().then(error => {
    //                 throw new Error(error.error || 'Failed to remove question');
    //             });
    //         }
    //         updateQuestionNumbers(); // Update question numbers after deletion
    //     }).catch(error => console.error('Error:', error.message));
    // }
    

    function updateQuestionNumbers() {
        document.querySelectorAll('.question-container').forEach((container, index) => {
            const questionNumber = index + 1;
            container.querySelector('h2').textContent = `Question ${questionNumber}`;
        });

        questionCounter = document.querySelectorAll('.question-container').length;
    }
    // function updateQuestionNumbers() {
    //     document.querySelectorAll('.question-container').forEach((container, index) => {
    //         const questionNumber = index + 1;
    //         container.querySelector('h2').textContent = `Question ${questionNumber}`;
            
    //         container.querySelectorAll('input').forEach((input, idx) => {
    //             const optionLetter = ['a', 'b', 'c', 'd'][idx];
    //             input.name = `option_${questionNumber}_${optionLetter}`;
    //         });

    //         container.querySelector('select').name = `correct_answer_${questionNumber}`;
    //     });

    //     questionCounter = document.querySelectorAll('.question-container').length;
    // }

    function scrollToBottom() {
        document.querySelector('.submit-quiz').scrollIntoView({ behavior: 'smooth' });
    }

    function updateSessionData() {
        // This function should update the session data on the server side
        // You can use AJAX to send the updated question list to the server
    }

    attachDeleteEvents(); // Attach delete events to existing questions on page load
});

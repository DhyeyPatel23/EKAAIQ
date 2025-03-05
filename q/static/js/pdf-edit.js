document.addEventListener("DOMContentLoaded", function () {
    let questionCounter = document.querySelectorAll('.question-container').length;
    var STATIC_URL = "/static/";

    // Add loading state handling
    function setLoadingState(button, isLoading) {
        if (isLoading) {
            button.disabled = true;
            button.originalText = button.textContent;
            button.textContent = "Generating Questions...";
            button.style.opacity = "0.7";
        } else {
            button.disabled = false;
            button.textContent = button.originalText;
            button.style.opacity = "1";
        }
    }

    document.querySelector('.add-question').addEventListener('click', async function() {
        const button = this;
        setLoadingState(button, true);

        try {
            // Get the quiz title or content to generate questions from
            const quizTitle = document.querySelector('#quizTitle')?.value || "General Knowledge";

            const response = await fetch('/q/generate_ai_questions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    // Generate one question at a time
                })
            });

            if (!response.ok) {
                throw new Error('Failed to generate question');
            }

            const data = await response.json();
            
            if (data.questions && data.questions.length > 0) {
                data.questions.forEach(question => {
                    questionCounter++;
                    
                    // Convert option index (option1, option2, etc.) to array index
                    const correctAnswerIndex = parseInt(question.correct_answer.replace('option', '')) - 1;
                    const correctAnswerText = question.options[correctAnswerIndex];

                    const questionTemplate = `
                        <div class="question-container" style="opacity: 0; transform: translateY(20px);">
                            <h2>Question ${questionCounter}</h2>
                            <input type="text" name="questions" value="${question.question}" placeholder="Enter Question here..." required>
                            
                            ${question.image_loc ? `
                                <img src="${STATIC_URL}${question.image_loc}" alt="" style="max-width: 500px;">
                                <input type="text" name="img" value="${question.image_loc}" hidden>
                            ` : ''}
                            <br>

                            Option 1: <input type="text" name="options" value="${question.options[0]}" placeholder="Option A" required>
                            <br>
                            Option 2: <input type="text" name="options" value="${question.options[1]}" placeholder="Option B" required>
                            <br>
                            Option 3: <input type="text" name="options" value="${question.options[2]}" placeholder="Option C" required>
                            <br>
                            Option 4: <input type="text" name="options" value="${question.options[3]}" placeholder="Option D" required>

                            <br>
                            Correct Answer:
                            <br>
                            <select name="correct_options">
                                <option value="${ question.correct_answer }">${ question.correct_answer }</option>
                            </select>
                            <br>

                            <button type="button" class="delete-question">Delete Question</button>
                        </div>
                    `;

                    const questionList = document.querySelector('#question-list');
                    questionList.insertAdjacentHTML('beforeend', questionTemplate);
                    
                    // Animate the new question appearance
                    const newQuestion = questionList.lastElementChild;
                    setTimeout(() => {
                        newQuestion.style.transition = 'all 0.5s ease';
                        newQuestion.style.opacity = '1';
                        newQuestion.style.transform = 'translateY(0)';
                        showNotification('Question generated successfully', 'success');
                    }, 50);
                });

                attachDeleteEvents();
                scrollToBottom();
            } else {
                showNotification('something went wrong', 'error');
            }

        } catch (error) {
            console.error('Error generating question:', error);
            showNotification('Failed to generate question', 'error');
        } finally {
            setLoadingState(button, false);
        }
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

    function handleDelete() {
        const questionContainer = this.parentElement;
        const questionData = {
            question: questionContainer.querySelector('input[name="questions"]').value,
            image: questionContainer.querySelector('input[name="img"]')?.value,
            options: Array.from(questionContainer.querySelectorAll('input[name="options"]')).map(input => input.value),
            correct_answer: questionContainer.querySelector('select[name="correct_options"]').value
        };

        // Remove the question container with animation
        questionContainer.style.opacity = '0';
        questionContainer.style.transform = 'translateY(-20px)';
        questionContainer.style.transition = 'all 0.3s ease';
        questionContainer.remove();
        updateQuestionNumbers();
        showNotification('Question removed successfully', 'success');

        // setTimeout(() => {
            
        //     // Send delete request to server
        //     fetch('/a/remove_quiz_question/', {
        //         method: 'POST',
        //         headers: {
        //             'Content-Type': 'application/json',
        //             'X-CSRFToken': getCookie('csrftoken'),
        //             'X-Requested-With': 'XMLHttpRequest'
        //         },
        //         body: JSON.stringify(questionData)
        //     })
        //     .then(response => {
        //         if (!response.ok) {
        //             throw new Error('Failed to remove question from server');
        //         }
        //         return response.json();
        //     })
        //     .then(data => {
        //         if (data.success) {
        //             showNotification('Question removed successfully', 'success');
        //         }
        //     })
        //     .catch(error => {
        //         console.error('Error:', error);
        //         showNotification('Failed to remove question', 'error');
        //     });
        // }, 300);
    }

    function attachDeleteEvents() {
        document.querySelectorAll('.delete-question').forEach(button => {
            button.removeEventListener('click', handleDelete); // Remove previous event listeners to prevent duplicates
            button.addEventListener('click', handleDelete);
        });
    }

    function updateQuestionNumbers() {
        document.querySelectorAll('.question-container').forEach((container, index) => {
            const questionNumber = index + 1;
            const heading = container.querySelector('h2');
            
            // Add transition effect
            heading.style.transition = 'opacity 0.3s ease';
            heading.style.opacity = '0';
            
            setTimeout(() => {
                heading.textContent = `Question ${questionNumber}`;
                heading.style.opacity = '1';
            }, 150);
        });

        questionCounter = document.querySelectorAll('.question-container').length;
    }

    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 8px;
            color: white;
            background-color: ${type === 'success' ? '#4CAF50' : '#f44336'};
            z-index: 1000;
            opacity: 0;
            transform: translateY(-20px);
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;

        document.body.appendChild(notification);
        
        // Trigger animation
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, 10);

        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-20px)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    function scrollToBottom() {
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
    }

    // Initialize delete events for existing questions
    attachDeleteEvents();

    // Optional: Add form submission handler
    document.querySelector('form').addEventListener('submit', function(e) {
        const questions = document.querySelectorAll('.question-container');
        if (questions.length === 0) {
            e.preventDefault();
            showNotification('Please add at least one question', 'error');
        }
    });
});
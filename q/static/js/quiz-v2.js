let questionCount = 1;

document.getElementById('addQuestionBtn').addEventListener('click', function() {
    questionCount++;
    const questionBlock = document.createElement('div');
    questionBlock.className = 'question-block';
    questionBlock.id = `question${questionCount}`;
    questionBlock.innerHTML = `
        <label for="question${questionCount}Input">Question ${questionCount}</label>

        <textarea  name="questions" id="question${questionCount}Input" placeholder="Enter Question here..." required ></textarea>
        <input type="file" name="images">
        <div class="options-container">
            <input  name="options" type="text" placeholder="Option A" class="option" required >
        </div>
        <div class="options-container">
            <input  name="options" type="text" placeholder="Option B" class="option" required >
        </div>
        <div class="options-container">
            <input  name="options" type="text" placeholder="Option C" class="option" required >
        </div>
        <div class="options-container">
            <input  name="options" type="text" placeholder="Option D" class="option" required >
        </div>
        <div class="question-controls">
            <select class="select-answer" name="correct_options" required >
                <option value="option1">Option A</option>
                <option value="option2">Option B</option>
                <option value="option3">Option C</option>
                <option value="option4">Option D</option>
            </select>
        </div>
        <button type="button" class="delete-question-btn">Delete Question</button>
    </div>
    `;
    document.getElementById('questionsContainer').appendChild(questionBlock);

    // Scroll to the new question
    questionBlock.scrollIntoView({ behavior: 'smooth' });
});

document.addEventListener('click', function(e) {
    if (e.target && e.target.className == 'delete-question-btn') {
        e.target.closest('.question-block').remove();
        questionCount--;
    }
});

// document.getElementById('quizForm').addEventListener('submit', function(e) {
//     e.preventDefault();
//     window.location.href = "/q/create"
//     alert('Quiz Submitted!');
// });

document.addEventListener('DOMContentLoaded', function() {
    // const startQuizBtn = document.getElementById('startQuizBtn');
    const container = document.querySelector('.container');
    const backgroundPattern = document.querySelector('.background-pattern');
    
    // Hover effect for background pattern
    container.addEventListener('mousemove', function(e) {
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;
        
        backgroundPattern.style.transform = `translate(${mouseX * 80}px, ${mouseY * 80}px)`;
    });

    container.addEventListener('mouseleave', function() {
        backgroundPattern.style.transform = 'translate(0, 0)';
    });
});

// Get the modal, signup button, and close button
const signupPopup = document.getElementById('signupPopup');
const signupBtn = document.getElementById('signupBtn');
const closeSignupPopup = document.getElementById('closeSignupPopup');

// Show the modal when the "Sign Up" button is clicked
signupBtn.addEventListener('click', function (event) {
    event.preventDefault();  // Prevent form submission
    signupPopup.classList.add('active');
});

// Close the modal when the close button is clicked
closeSignupPopup.addEventListener('click', function () {
    signupPopup.classList.remove('active');
});

// Optional: Close the modal when clicking outside the modal content
window.addEventListener('click', function (event) {
    if (event.target === signupPopup) {
        signupPopup.classList.remove('active');
    }
});
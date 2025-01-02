const closeBtn = document.querySelector(".fa-xmark");

const container = document.querySelector(".container");
const signupBtn = document.querySelector("#signupBtn");
const signupPopup = document.querySelector("#signupPopup");
const closeSignupPopup = document.querySelector("#closeSignupPopup");


// btn.addEventListener("click", () => {
//   div.classList.add("active");
//   container.classList.add("container-active");
// });


closeBtn.addEventListener("click", () => {
  div.classList.remove("active");
  container.classList.remove("container-active");
});


signupBtn.addEventListener("click", () => {
    signupPopup.classList.add("active");
    container.classList.add("container-active");
  });

closeSignupPopup.addEventListener("click", () => {
  signupPopup.classList.remove("active");
  container.classList.remove("container-active");
  });



document.addEventListener('DOMContentLoaded', function() {
  const usernameInput = document.getElementById('username');
  const usernameError = document.getElementById('usernameError');
  const form = document.querySelector('.registration-form'); // Or use login form if needed

  let isUsernameValid = false; // Flag to track username validity

  usernameInput.addEventListener('input', function() {
      const usernameValue = usernameInput.value;

      // Check if the username contains any number
      if (/\d/.test(usernameValue)) {
          usernameError.textContent = 'Numbers are not allowed in the username.';
          usernameError.style.color = 'red';
          usernameInput.style.borderColor = 'red';
          isUsernameValid = false; // Mark the username as invalid
      } else if (usernameValue.length > 0) {
          usernameError.textContent = 'Valid username.';
          usernameError.style.color = 'green';
          usernameInput.style.borderColor = 'green';
          isUsernameValid = true; // Mark the username as valid
      } else {
          usernameError.textContent = ''; // Clear error when input is empty
          usernameInput.style.borderColor = ''; // Reset border color
          isUsernameValid = false; // Consider empty as invalid
      }
  });

  // Prevent form submission if the username is invalid
  form.addEventListener('submit', function(event) {
      if (!isUsernameValid) {
          event.preventDefault(); // Stop form submission
          alert('Please correct the username before submitting.');
      }
  });
});

document.getElementById("forgotPasswordLink").addEventListener("click", function (event) {
  event.preventDefault();
  window.location.href = this.href; // Redirect on the first click
});

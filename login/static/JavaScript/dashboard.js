// script.js


// add hovered class to selected list item
let list = document.querySelectorAll(".navigation li");

function activeLink() {
  list.forEach((item) => {
    item.classList.remove("hovered");
  });
  this.classList.add("hovered");
}

list.forEach((item) => item.addEventListener("mouseover", activeLink));

// Menu Toggle
let toggle = document.querySelector(".toggle");
let navigation = document.querySelector(".navigation");
let main = document.querySelector(".main");


navigation.classList.toggle("active");
main.classList.toggle("active");

toggle.onclick = function () {
  navigation.classList.toggle("active");
  main.classList.toggle("active");
};



function createQuiz() {
    // Redirect to the enhanced quiz creation page
    window.location.href = "/q/create_enhanced";
}

function pdfQuiz() {
  // Redirect to the create quiz page
  // alert('Redirecting to Create Quiz Page');
  window.location.href = "/q/upload";
}

function aiQuiz() {
    // Redirect to the create quiz page
    // alert('Redirecting to Create Quiz Page');
    window.location.href = "/a/upload_text";
}

function joinQuiz() {
    // Redirect to the join quiz page
    // alert('Redirecting to Join Quiz Page');
    window.location.href = "/q/join_room";
}
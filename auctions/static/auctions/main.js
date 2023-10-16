const commentTextArea = document.getElementById("comment");

// Adjust the height of the textarea based on its content
commentTextArea.addEventListener("input", function () {
  this.style.height = "auto";
  this.style.height = this.scrollHeight + "px";
});

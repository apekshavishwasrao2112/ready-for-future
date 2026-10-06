const fileInput = document.getElementById("id_resume_file");
const fileName = document.getElementById("file-name");

if (fileInput && fileName) {
    fileInput.addEventListener("change", function () {
        fileName.textContent = fileInput.files.length
            ? fileInput.files[0].name
            : "No file selected";
    });
}

const uploadForm = document.querySelector(".resume-form");

if (uploadForm) {
    uploadForm.addEventListener("submit", function () {
        const uploadButton = uploadForm.querySelector("button[type='submit']");
        if (uploadButton) {
            uploadButton.disabled = true;
            uploadButton.textContent = "Uploading...";
        }
    });
}

const feedbackForm = document.querySelector(".feedback-form");

if (feedbackForm) {
    feedbackForm.addEventListener("submit", function () {
        const feedbackButton = feedbackForm.querySelector("button[type='submit']");
        if (feedbackButton) {
            feedbackButton.disabled = true;
            feedbackButton.textContent = "Reviewing PDF...";
        }
    });
}

const syllabusInput = document.getElementById("syllabusInput");
const datesheetInput = document.getElementById("datesheetInput");

const syllabusName = document.getElementById("syllabusName");
const datesheetName = document.getElementById("datesheetName");

const uploadBtn = document.querySelector(".upload-btn");

const dropAreas = document.querySelectorAll(".drop-area");


/* -----------------------
FILE SELECT
-----------------------*/

syllabusInput.addEventListener("change", () => {

    if (syllabusInput.files.length > 0) {
        syllabusName.textContent = syllabusInput.files.length + " file(s) selected";
    }

});

datesheetInput.addEventListener("change", () => {

    if (datesheetInput.files.length > 0) {
        datesheetName.textContent = datesheetInput.files[0].name;
    }

});


/* -----------------------
DRAG & DROP
-----------------------*/

dropAreas[0].addEventListener("dragover", e => {
    e.preventDefault();
});

dropAreas[0].addEventListener("drop", e => {

    e.preventDefault();

    const files = e.dataTransfer.files;

    syllabusInput.files = files;

    syllabusName.textContent = files.length + " file(s) selected";

});


dropAreas[1].addEventListener("dragover", e => {
    e.preventDefault();
});

dropAreas[1].addEventListener("drop", e => {

    e.preventDefault();

    const files = e.dataTransfer.files;

    datesheetInput.files = files;

    datesheetName.textContent = files[0].name;

});


/* -----------------------
UPLOAD TO FLASK
-----------------------*/

uploadBtn.addEventListener("click", async () => {

    if (!syllabusInput.files.length || !datesheetInput.files.length) {

        alert("Please upload both syllabus and datesheet");

        return;

    }

    const formData = new FormData();

    formData.append("userid", 1);

    for (let file of syllabusInput.files) {
        formData.append("files", file);
    }

    formData.append("files", datesheetInput.files[0]);


    try {

        const res = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        console.log("UPLOAD RESPONSE:", data);

        window.location.href = "/status";

    } catch (err) {

        console.error(err);

        alert("Upload failed");

    }

});
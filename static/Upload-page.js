const syllabusInput = document.getElementById("syllabusInput");
const syllabusName = document.getElementById("syllabusName");

syllabusInput.addEventListener("change", function(){

if(this.files.length > 1){
syllabusName.textContent = this.files.length + " files uploaded";
}
else if(this.files.length === 1){
syllabusName.textContent = this.files[0].name;
}
else{
syllabusName.textContent = "No file chosen";
}

});


const dateInput = document.getElementById("datesheetInput");
const dateName = document.getElementById("datesheetName");

dateInput.addEventListener("change", function(){

if(this.files.length > 0){
dateName.textContent = this.files[0].name;
}
else{
dateName.textContent = "No file chosen";
}

});

// Drag and Drop functionality
const dropAreas = document.querySelectorAll('.drop-area');

dropAreas.forEach(area => {
    const input = area.querySelector('input[type="file"]');
    const span = area.querySelector('.file-name');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        area.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop area when dragging over
    ['dragenter', 'dragover'].forEach(eventName => {
        area.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        area.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        area.classList.add('drag-over');
    }

    function unhighlight(e) {
        area.classList.remove('drag-over');
    }

    // Handle drop
    area.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        handleFiles(files);
    }

    function handleFiles(files) {
        // Create a DataTransfer object to set files
        const dt = new DataTransfer();
        for (let file of files) {
            dt.items.add(file);
        }
        input.files = dt.files;

        // Update display
        updateFileName();
    }

    function updateFileName() {
        if (input.files.length > 1) {
            span.textContent = input.files.length + " files uploaded";
        } else if (input.files.length === 1) {
            span.textContent = input.files[0].name;
        } else {
            span.textContent = "No file chosen";
        }
    }
});
// static/upload.js
const syllabusInput = document.getElementById("syllabusInput");
const datesheetInput = document.getElementById("datesheetInput");
const syllabusName = document.getElementById("syllabusName");
const datesheetName = document.getElementById("datesheetName");
const uploadBtn = document.getElementById("uploadBtn");
const syllabusDrop = document.getElementById("syllabusDrop");
const datesheetDrop = document.getElementById("datesheetDrop");

function wireDrop(area, inputEl, nameEl){
  area.addEventListener("dragover", e => { e.preventDefault(); area.classList.add("drag-over"); });
  area.addEventListener("dragleave", e => { area.classList.remove("drag-over"); });
  area.addEventListener("drop", e => {
    e.preventDefault(); area.classList.remove("drag-over");
    const files = e.dataTransfer.files;
    inputEl.files = files;
    if(files.length > 1) nameEl.textContent = files.length + " files selected";
    else nameEl.textContent = files[0].name;
  });
}
wireDrop(syllabusDrop, syllabusInput, syllabusName);
wireDrop(datesheetDrop, datesheetInput, datesheetName);

syllabusInput.addEventListener("change", ()=> {
  syllabusName.textContent = syllabusInput.files.length + " file(s) selected";
});
datesheetInput.addEventListener("change", ()=> {
  datesheetName.textContent = datesheetInput.files[0].name;
});

uploadBtn.addEventListener("click", async ()=>{
  if(!syllabusInput.files.length || !datesheetInput.files.length){
    alert("Please upload both syllabus and datesheet");
    return;
  }
  const fd = new FormData();
  for(let f of syllabusInput.files) fd.append("files", f);
  fd.append("files", datesheetInput.files[0]);
  try{
    const res = await fetch("/upload", { method: "POST", body: fd });
    if(!res.ok) {
      const t = await res.text();
      console.error(t);
      alert("Upload failed. See terminal.");
      return;
    }
    const data = await res.json();
    console.log("Uploaded:", data);
    window.location = "/status";
  }catch(e){
    console.error(e);
    alert("Upload failed");
  }
});
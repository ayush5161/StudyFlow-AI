/* -----------------------------
ELEMENTS
----------------------------- */

const hoursList = document.getElementById("hoursList")

/* -----------------------------
SHOW "OTHER STATUS" TEXTBOX
----------------------------- */

document.querySelectorAll(".status-select").forEach(select => {

select.addEventListener("change", () => {

const input = select.parentElement.querySelector(".other-input")

if(select.value === "others"){
input.style.display = "block"
}else{
input.style.display = "none"
}

})

})


/* -----------------------------
PARSE DATE SAFELY
----------------------------- */

function parseDate(dateStr){

if(!dateStr || dateStr === "null") return null

const d = new Date(dateStr)

if(isNaN(d)) return null

return d

}


/* -----------------------------
GENERATE STUDY DAY ROWS
(today → last exam)
----------------------------- */

function generateDateRows(){

let lastExam = null

document.querySelectorAll(".exam-date").forEach(span => {

const examDate = parseDate(span.innerText)

if(!examDate) return

if(!lastExam || examDate > lastExam){
lastExam = examDate
}

})


if(!lastExam){
console.log("No exam dates found")
return
}


const today = new Date()

today.setHours(0,0,0,0)

let cur = new Date(today)

while(cur <= lastExam){

const row = document.createElement("div")
row.className = "date-row"


/* DATE */

const dateSpan = document.createElement("span")

const formatted =
cur.getFullYear() + "-" +
String(cur.getMonth()+1).padStart(2,'0') + "-" +
String(cur.getDate()).padStart(2,'0')

dateSpan.innerText = formatted


/* INPUT */

const input = document.createElement("input")

input.type = "number"
input.placeholder = "hours"
input.min = "0"
input.max = "24"


row.appendChild(dateSpan)
row.appendChild(input)

hoursList.appendChild(row)

cur.setDate(cur.getDate() + 1)

}

}

generateDateRows()


/* -----------------------------
COLLECT SUBJECT STATUS
----------------------------- */

function collectSubjects(){

const subjects = []

document.querySelectorAll(".subject-block").forEach(block => {

const name = block.querySelector("h2").innerText
const exam = block.querySelector(".exam-date").innerText

const topics = []

block.querySelectorAll(".topic-row").forEach(row => {

const topic = row.querySelector(".topic-name").innerText
const status = row.querySelector(".status-select").value
const other = row.querySelector(".other-input").value

topics.push({
topic: topic,
status: status === "others" ? other : status
})

})

subjects.push({
subject: name,
exam_date: exam,
topics: topics
})

})

return subjects

}


/* -----------------------------
COLLECT DAILY HOURS
----------------------------- */

function collectHours(){

const daily_hours = {}

document.querySelectorAll(".date-row").forEach(row => {

const date = row.children[0].innerText
const hours = row.children[1].value

if(hours){
daily_hours[date] = parseInt(hours)
}

})

return daily_hours

}


/* -----------------------------
GENERATE SCHEDULE
----------------------------- */

document.getElementById("generateBtn").addEventListener("click", async () => {

const payload = {

subjects: collectSubjects(),
daily_hours: collectHours()

}

try{

await fetch("/submit_status/1",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify(payload)
})

await fetch("/generate_schedule/1",{
method:"POST"
})

window.location = "/schedule_page"

}catch(err){

console.error("Schedule generation failed:", err)
alert("Failed to generate schedule")

}

})
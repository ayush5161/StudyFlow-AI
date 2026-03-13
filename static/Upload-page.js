const hoursList = document.getElementById("hoursList")

/* --------------------------
SHOW OTHER TEXTBOX
---------------------------*/

document.querySelectorAll(".status-select").forEach(select=>{

select.addEventListener("change",()=>{

const input = select.parentElement.querySelector(".other-input")

if(select.value==="others"){
input.style.display="block"
}else{
input.style.display="none"
}

})

})


/* --------------------------
GENERATE DATE RANGE
---------------------------*/

function generateDateRows(){

let lastExam = null

document.querySelectorAll(".exam-date").forEach(span=>{

const txt = span.innerText

if(txt==="No exam date") return

const d = new Date(txt)

if(!lastExam || d>lastExam){
lastExam=d
}

})

if(!lastExam) return

const today = new Date()

let cur = new Date(today)

while(cur<=lastExam){

const row = document.createElement("div")
row.className="date-row"

const dateSpan=document.createElement("span")

const formatted=
cur.getFullYear()+"-"+String(cur.getMonth()+1).padStart(2,'0')+"-"+String(cur.getDate()).padStart(2,'0')

dateSpan.innerText=formatted

const input=document.createElement("input")

input.type="number"
input.placeholder="hours"

row.appendChild(dateSpan)
row.appendChild(input)

hoursList.appendChild(row)

cur.setDate(cur.getDate()+1)

}

}

generateDateRows()



/* --------------------------
GENERATE SCHEDULE
---------------------------*/

document.getElementById("generateBtn").addEventListener("click",async()=>{

const subjects=[]

document.querySelectorAll(".subject-block").forEach(block=>{

const name=block.querySelector("h2").innerText
const exam=block.querySelector(".exam-date").innerText

const topics=[]

block.querySelectorAll(".topic-row").forEach(row=>{

const topic=row.querySelector(".topic-name").innerText
const status=row.querySelector(".status-select").value
const other=row.querySelector(".other-input").value

topics.push({

topic:topic,
status:status==="others"?other:status

})

})

subjects.push({

subject:name,
exam_date:exam,
topics:topics

})

})


const daily_hours={}

document.querySelectorAll(".date-row").forEach(row=>{

const date=row.children[0].innerText
const hours=row.children[1].value

if(hours){
daily_hours[date]=parseInt(hours)
}

})


const payload={

subjects:subjects,
daily_hours:daily_hours

}


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


window.location="/schedule_page"

})
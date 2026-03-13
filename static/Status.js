// static/Status.js
// show/hide other input
document.querySelectorAll(".status-select").forEach(s => {
  s.addEventListener("change", ()=> {
    const inp = s.parentElement.querySelector(".other-input");
    if(s.value === "others") inp.style.display = "inline-block";
    else inp.style.display = "none";
  });
});

// populate study_days on right using subjects JSON from server (rendered server-side)
async function loadStudyDays(){
  // fetch subjects JSON to get study_days reliably
  const res = await fetch("/subjects");
  if(!res.ok) return;
  const data = await res.json();
  const container = document.getElementById("hoursList");
  container.innerHTML = "";
  (data.study_days || []).forEach(d => {
    const row = document.createElement("div");
    row.className = "date-row";
    const span = document.createElement("span"); span.innerText = d.date;
    const input = document.createElement("input"); input.type = "number"; input.placeholder = "hours";
    row.appendChild(span); row.appendChild(input);
    container.appendChild(row);
  });
}
loadStudyDays();

// generate schedule button
document.getElementById("generateBtn").addEventListener("click", async ()=>{
  // collect status
  const subjects = [];
  document.querySelectorAll(".subject-block").forEach(block=>{
    const name = block.querySelector("h2").innerText;
    const exam = block.querySelector(".exam-date").innerText;
    const topics = [];
    block.querySelectorAll(".topic-row").forEach(row=>{
      const topic = row.querySelector(".topic-name").innerText;
      const status = row.querySelector(".status-select").value;
      const other = row.querySelector(".other-input").value;
      topics.push({ topic: topic, status: status === "others" ? other : status });
    });
    subjects.push({ subject: name, exam_date: exam, topics: topics });
  });

  const daily_hours = {};
  document.querySelectorAll(".date-row").forEach(row=>{
    const date = row.children[0].innerText;
    const val = row.children[1].value;
    if(val) daily_hours[date] = parseInt(val);
  });

  const payload = { subjects, daily_hours };
  // save status
  await fetch("/submit_status", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload) });
  // generate schedule
  const gen = await fetch("/generate_schedule", { method:"POST" });
  if(!gen.ok) {
    alert("Schedule generation failed. Check server logs.");
    return;
  }
  window.location = "/schedule_page";
});
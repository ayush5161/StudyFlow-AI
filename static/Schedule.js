// static/schedule.js
async function loadSchedule(){
  const res = await fetch("/schedule");
  if(!res.ok){
    document.getElementById("scheduleContainer").innerText = "No schedule yet";
    return;
  }
  const data = await res.json();
  const container = document.getElementById("scheduleContainer");
  container.innerHTML = "";
  const schedule = data.schedule || data; // flexible
  Object.keys(schedule).sort().forEach(date => {
    const dateBlock = document.createElement("div");
    dateBlock.className = "date-block";
    const dateTitle = document.createElement("div"); dateTitle.className = "date-title"; dateTitle.innerText = date;
    dateBlock.appendChild(dateTitle);
    const subjects = {};
    schedule[date].forEach(item=>{
      const parts = (item.topic || "").split(" - ");
      const subject = parts[0] || "Misc";
      const topic = parts.slice(1).join(" - ") || parts[0];
      if(!subjects[subject]) subjects[subject] = [];
      subjects[subject].push({ topic: topic, duration: item.duration || "" });
    });
    Object.keys(subjects).forEach(s=>{
      const sb = document.createElement("div"); sb.className = "subject-block";
      const sn = document.createElement("div"); sn.className = "subject-name"; sn.innerText = s;
      sb.appendChild(sn);
      subjects[s].forEach(t=>{
        const row = document.createElement("div"); row.className = "topic-row";
        const tn = document.createElement("div"); tn.className = "topic-name"; tn.innerText = t.topic;
        const du = document.createElement("div"); du.className = "duration"; du.innerText = t.duration;
        row.appendChild(tn); row.appendChild(du); sb.appendChild(row);
      });
      dateBlock.appendChild(sb);
    });
    container.appendChild(dateBlock);
  });
}
loadSchedule();
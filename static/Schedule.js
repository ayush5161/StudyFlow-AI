async function loadSchedule(){

    const container = document.getElementById("scheduleContainer");

    const res = await fetch("http://127.0.0.1:5000/schedule/1");

    const data = await res.json();

    const schedule = data.schedule;

    Object.keys(schedule).forEach(date => {

        const dateBlock = document.createElement("div");
        dateBlock.className = "date-block";

        const dateTitle = document.createElement("div");
        dateTitle.className = "date-title";
        dateTitle.innerText = date;

        dateBlock.appendChild(dateTitle);

        const subjects = {};

        schedule[date].forEach(item => {

            const parts = item.topic.split(" - ");
            const subject = parts[0];
            const topic = parts[1];

            if(!subjects[subject]) subjects[subject] = [];

            subjects[subject].push({
                topic:topic,
                duration:item.duration
            });

        });

        Object.keys(subjects).forEach(subject => {

            const subjectBlock = document.createElement("div");
            subjectBlock.className = "subject-block";

            const subjectName = document.createElement("div");
            subjectName.className = "subject-name";
            subjectName.innerText = subject;

            subjectBlock.appendChild(subjectName);

            subjects[subject].forEach(t => {

                const row = document.createElement("div");
                row.className = "topic-row";

                const topicName = document.createElement("div");
                topicName.className = "topic-name";
                topicName.innerText = t.topic;

                const duration = document.createElement("div");
                duration.className = "duration";
                duration.innerText = t.duration;

                row.appendChild(topicName);
                row.appendChild(duration);

                subjectBlock.appendChild(row);

            });

            dateBlock.appendChild(subjectBlock);

        });

        container.appendChild(dateBlock);

    });

}

loadSchedule();
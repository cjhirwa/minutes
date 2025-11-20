const apiUrl = 'http://127.0.0.1:8001/api';

function toggleMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    mobileMenu.style.display = mobileMenu.style.display === 'flex' ? 'none' : 'flex';
}

function showProgressUpdate(message) {
    document.getElementById('progress-updates').textContent = message;
}

function closeMenu() {
    document.getElementById('mobileMenu').style.display = 'none';
}

function showGenerator() {
    document.getElementById('generator').classList.add('active');
    document.getElementById('generator').scrollIntoView({ behavior: 'smooth' });
}

async function generateMinutesFromTranscript(transcript) {
    showProgressUpdate('Summarizing transcript...');

    try {
        const response = await fetch(`${apiUrl}/summarize/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                transcript: transcript
            })
        });

        const data = await response.json();

        if (data.minutes) {
            showProgressUpdate('Done summarizing...');

            if (data.minutes.error) {
                showError(data.minutes.error);
                return;
            }
            displayMinutes(data.minutes);
            localStorage.removeItem('lastTranscript');
        } else {
            showError('Invalid response from server.');
        }
    } catch (error) {
        console.error(error);
        showError('Failed to generate minutes. Please try again.');
        
    } finally {
        document.getElementById('loading').classList.remove('active');
        document.getElementById('generateBtn').disabled = false;
    }
}

async function generateMinutes(event) {
    event.preventDefault();

    // Hide previous results and alerts
    hideAlerts();
    document.getElementById('results').classList.remove('active');
    
    // Show loading
    document.getElementById('loading').classList.add('active');
    document.getElementById('generateBtn').disabled = true;

    showProgressUpdate('Transcribing audio...');

    // directly call summary frunction if there is a saved transcript
    const savedTranscript = localStorage.getItem('lastTranscript');
    if (savedTranscript) {
        generateMinutesFromTranscript(savedTranscript);
        return;
    }

    try {
        const fileInput = document.getElementById('recordFile');
        if (!fileInput.files.length) {
            showError('Please select a file first.');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        const response = await fetch(`${apiUrl}/transcribe/`, {
            method: 'POST',
            body: formData
        });


        const data = await response.json();
        
        if (data.transcript) {
            // save transcript to local storage
            localStorage.setItem('lastTranscript', data.transcript);
            showProgressUpdate('Done Transcribing audio, generating summary...');
            generateMinutesFromTranscript(data.transcript);
        } else {
            showError('Invalid response from server.');
        }
    } catch (error) {
        console.error(error);
        showError('Failed to generate minutes. Please try again.');
    } finally {
        document.getElementById('loading').classList.remove('active');
        document.getElementById('generateBtn').disabled = false;
    }

}

function displayMinutes(data) {
    const minutesContent = document.getElementById('minutesContent');
    const resultsSection = document.getElementById('results');

    // Extract the actual minutes object
    const minutes = data.minutes;
    
    // Build HTML
    let html = `
        <h2>${minutes.title || "Meeting Minutes"}</h2>

        <p><strong>Date:</strong> ${minutes.date || "N/A"}</p>
        <p><strong>Attendees:</strong> ${minutes.attendees || "N/A"}</p>

        <h3>Summary</h3>
        <p>${minutes.summary || ""}</p>

        <h3>Topics Discussed</h3>
    `;

    // Topics
    if (Array.isArray(minutes.topics)) {
        minutes.topics.forEach(topic => {
            html += `
                <div class="topic-block">
                    <h4>${topic.topic}</h4>
                    <ul>
                        ${topic.points.map(point => `<li>${point}</li>`).join("")}
                    </ul>
                </div>
            `;
        });
    }

    // Action Items
    if (Array.isArray(minutes.action_items) && minutes.action_items.length > 0) {
        html += `
            <h3>Action Items</h3>
            <ul>
                ${minutes.action_items.map(item => `
                    <li>
                        <strong>${item.task}</strong><br>
                        <em>Responsible:</em> ${item.responsible}<br>
                        <em>Deadline:</em> ${item.deadline}
                    </li>
                `).join("")}
            </ul>
        `;
    }

    // Recommendations
    if (Array.isArray(minutes.recommendations) && minutes.recommendations.length > 0) {
        html += `
            <h3>Recommendations</h3>
            <ul>
                ${minutes.recommendations.map(rec => `<li>${rec}</li>`).join("")}
            </ul>
        `;
    }

    // Next Meeting
    if (minutes.next_meeting) {
        html += `
            <h3>Next Meeting</h3>
            <p><strong>Date & Time:</strong> ${minutes.next_meeting.date_time}</p>
            <p><strong>Location:</strong> ${minutes.next_meeting.location}</p>
        `;
    }

    // Approval
    html += `
        <h3>Approval</h3>
        <p><strong>Approved by:</strong> ${minutes.approved_by}</p>
        <p><strong>Date:</strong> ${minutes.approval_date}</p>
    `;

    // Insert into DOM
    minutesContent.innerHTML = html;

    resultsSection.classList.add('active');
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}


function copyMinutes() {
    const minutesText = document.getElementById('minutesContent').innerText;
    
    navigator.clipboard.writeText(minutesText).then(() => {
        showSuccess();
    }).catch(err => {
        showError('Failed to copy to clipboard');
    });
}

function showSuccess() {
    hideAlerts();
    const alert = document.getElementById('successAlert');
    alert.classList.add('active');
    setTimeout(() => alert.classList.remove('active'), 3000);
}

function showError(message) {
    hideAlerts();
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorAlert').classList.add('active');
}

function hideAlerts() {
    document.getElementById('successAlert').classList.remove('active');
    document.getElementById('errorAlert').classList.remove('active');
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
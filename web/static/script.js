const apiUrl = 'http://172.29.98.127:8080/api';

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

function validateAudio() {
    const fileInput = document.getElementById('recordFile');
    const file = fileInput.files[0];
    const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/x-m4a', 'audio/flac', 'audio/ogg', 'audio/webm'];

    if (file && !allowedTypes.includes(file.type)) {
        showError('Invalid file type. Please upload an audio file (mp3, wav, m4a, flac, ogg, webm).');
        fileInput.value = ''; // Clear the invalid file
    } else {
        // check size limit (e.g., 100MB)
        const maxSize = 100 * 1024 * 1024; // 100MB
        if (file && file.size > maxSize) {
            showError('File size exceeds the 100MB limit. Please upload a smaller file. Your file size: ' + (file.size / (1024 * 1024)).toFixed(2) + ' MB');
            fileInput.value = ''; // Clear the invalid file
        } else {
            hideAlerts();
        }
    }
}

function showGenerator() {
    document.getElementById('generator').classList.add('active');
    document.getElementById('generator').scrollIntoView({ behavior: 'smooth' });
}

async function fetchWithTimeout(url, options = {}, timeout = 3600000) { // 1 hour default
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, { ...options, signal: controller.signal });
        return response;
    } finally {
        clearTimeout(id);
    }
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
            displayMinutes(data.minutes);
            localStorage.removeItem('lastTranscript');
        } else {
            showError('Invalid response from server.');
        }
    } catch (error) {
        showError('Failed to generate minutes. Please try again.');
        
    } finally {
        document.getElementById('loading').classList.remove('active');
        document.getElementById('generateBtn').disabled = false;
    }
}

async function generateMinutes(event) {
    event.preventDefault();

    hideAlerts();
    document.getElementById('results').classList.remove('active');
    document.getElementById('loading').classList.add('active');
    document.getElementById('generateBtn').disabled = true;

    showProgressUpdate('Transcribing audio...');

    // If there’s a saved transcript, skip transcription
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

        // Use fetchWithTimeout for long transcription requests
        const response = await fetchWithTimeout(`${apiUrl}/transcribe/`, {
            method: 'POST',
            body: formData
        }, 3600000); // 1 hour timeout for long audio files

        const data = await response.json();

        if (data.transcript) {
            localStorage.setItem('lastTranscript', data.transcript);
            showProgressUpdate('Done Transcribing audio, generating summary...');
            generateMinutesFromTranscript(data.transcript);
        } else {
            showError('Invalid response from server.');
        }

    } catch (error) {
        if (error.name === 'AbortError') {
            showError('Transcription timed out. Please try a smaller file or wait longer.');
        } else {
            showError('Failed to generate minutes. Please try again.');
        }
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
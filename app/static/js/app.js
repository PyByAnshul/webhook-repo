let events = [];
let isConnected = true;
const UPDATE_INTERVAL = 15000;

function updateLastUpdate() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('lastUpdate').textContent = `Last updated: ${timeString}`;
}

function getEventTypeClass(fromBranch, toBranch) {

    if (!fromBranch || fromBranch === '') {
        return 'push'; 
    } else {
        return 'pull-request'; 
    }
}

function formatEventCard(event) {
    const eventClass = getEventTypeClass(event.from_branch, event.to_branch);
    const isPushEvent = !event.from_branch || event.from_branch === '';
    
    
    let formattedMessage;
    if (isPushEvent) {
        formattedMessage = `${event.author} pushed to ${event.to_branch}`;
    } else {
        formattedMessage = `${event.author} submitted a pull request from ${event.from_branch} to ${event.to_branch}`;
    }
    
    return `
        <div class="event-card ${eventClass}">
            <div class="event-header">
                <span class="event-type ${eventClass}">${isPushEvent ? 'PUSH' : 'PULL_REQUEST'}</span>
                <span class="event-timestamp">${event.timestamp}</span>
            </div>
            <div class="event-message">${formattedMessage}</div>
            <div class="event-details">
                <div class="event-author">Author: ${event.author}</div>
                <div class="event-branches">
                    ${isPushEvent ? 
                        `Branch: ${event.to_branch}` : 
                        `From: ${event.from_branch} → To: ${event.to_branch}`
                    }
                </div>
                <div class="event-commit">Commit: ${event.request_id.substring(0, 8)}</div>
            </div>
        </div>
    `;
}

function displayEvents() {
    const container = document.getElementById('eventsContainer');
    
    if (events.length === 0) {
        container.innerHTML = `
            <div class="no-events">
                <h3>No events yet</h3>
                <p>GitHub webhook events will appear here once they are received.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = events.map(formatEventCard).join('');
}

function showError(message) {
    const container = document.getElementById('eventsContainer');
    container.innerHTML = `
        <div class="error-message">
            <strong>Error:</strong> ${message}
        </div>
    `;
}

async function fetchEvents() {
    try {
        const response = await fetch('/webhook/events');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            events = data.events || [];
            displayEvents();
            updateLastUpdate();
            isConnected = true;
        } else {
            throw new Error(data.message || 'Failed to fetch events');
        }
    } catch (error) {
        console.error('Error fetching events:', error);
        isConnected = false;
        showError(`Failed to fetch events: ${error.message}`);
    }
}


fetchEvents();


setInterval(fetchEvents, UPDATE_INTERVAL);


document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        fetchEvents();
    }
}); 
// Events Map JavaScript

let map;
let markers = [];
let tempMarker = null;
let selectedLocation = null;

// Initialize the map when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    setupEventListeners();
    loadEvents();
});

/**
 * Initialize the Leaflet map
 */
function initializeMap() {
    // Create map centered on a default location (can be customized)
    map = L.map('map').setView([40.7128, -74.0060], 12); // New York as default
    
    // Add OpenStreetMap tiles (similar to Google Maps)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Add click handler for selecting location
    map.on('click', onMapClick);
}

/**
 * Handle map click for setting event location
 */
function onMapClick(e) {
    const form = document.getElementById('create-event-form');
    if (!form.classList.contains('hidden')) {
        selectedLocation = e.latlng;
        
        // Update form fields
        document.getElementById('event-latitude').value = e.latlng.lat.toFixed(6);
        document.getElementById('event-longitude').value = e.latlng.lng.toFixed(6);
        
        // Remove previous temp marker if exists
        if (tempMarker) {
            map.removeLayer(tempMarker);
        }
        
        // Add temporary marker
        tempMarker = L.marker(e.latlng, {
            icon: L.divIcon({
                className: 'temp-marker',
                iconSize: [20, 20]
            })
        }).addTo(map);
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Filter form
    document.getElementById('filter-form').addEventListener('submit', function(e) {
        e.preventDefault();
        loadEvents();
    });
    
    // Clear filters button
    document.getElementById('clear-filters').addEventListener('click', function() {
        document.getElementById('filter-form').reset();
        loadEvents();
    });
    
    // Show create form button
    document.getElementById('show-create-form').addEventListener('click', function() {
        document.getElementById('create-event-form').classList.remove('hidden');
        this.classList.add('hidden');
    });
    
    // Cancel create button
    document.getElementById('cancel-create').addEventListener('click', function() {
        document.getElementById('create-event-form').classList.add('hidden');
        document.getElementById('show-create-form').classList.remove('hidden');
        document.getElementById('create-event-form').reset();
        
        // Remove temp marker
        if (tempMarker) {
            map.removeLayer(tempMarker);
            tempMarker = null;
        }
        selectedLocation = null;
    });
    
    // Create event form
    document.getElementById('create-event-form').addEventListener('submit', function(e) {
        e.preventDefault();
        createEvent();
    });
}

/**
 * Load events from API with filters
 */
async function loadEvents() {
    try {
        // Build query parameters from filters
        const params = new URLSearchParams();
        
        const sport = document.getElementById('sport-filter').value;
        if (sport) params.append('sport', sport);
        
        const dateFrom = document.getElementById('date-from-filter').value;
        if (dateFrom) params.append('date_from', dateFrom);
        
        const dateTo = document.getElementById('date-to-filter').value;
        if (dateTo) params.append('date_to', dateTo);
        
        const place = document.getElementById('place-filter').value;
        if (place) params.append('place', place);
        
        const difficulty = document.getElementById('difficulty-filter').value;
        if (difficulty) params.append('difficulty', difficulty);
        
        const queryString = params.toString();
        const url = `/api/events${queryString ? '?' + queryString : ''}`;
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const events = await response.json();
        displayEventsOnMap(events);
    } catch (error) {
        console.error('Error loading events:', error);
        showNotification('Failed to load events', 'error');
    }
}

/**
 * Display events on the map
 */
function displayEventsOnMap(events) {
    // Clear existing markers
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    
    // Add markers for each event
    events.forEach(event => {
        const marker = L.marker([event.latitude, event.longitude])
            .addTo(map)
            .bindPopup(createEventPopup(event));
        
        markers.push(marker);
    });
    
    // Fit map to show all markers if there are any
    if (markers.length > 0) {
        const group = L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}

/**
 * Create popup content for an event
 */
function createEventPopup(event) {
    const date = new Date(event.date);
    const formattedDate = date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const difficultyClass = `difficulty-${event.difficulty.toLowerCase()}`;
    
    return `
        <div class="event-popup">
            <h3>${event.sport}</h3>
            <p><strong>Location:</strong> ${event.place}</p>
            <p><strong>Date:</strong> ${formattedDate}</p>
            <p><strong>Difficulty:</strong> <span class="event-difficulty ${difficultyClass}">${event.difficulty}</span></p>
            ${event.description ? `<p><strong>Details:</strong> ${event.description}</p>` : ''}
        </div>
    `;
}

/**
 * Create a new event
 */
async function createEvent() {
    try {
        // Validate location is selected
        if (!selectedLocation) {
            showNotification('Please click on the map to select event location', 'error');
            return;
        }
        
        // Get form data
        const formData = {
            sport: document.getElementById('event-sport').value,
            date: document.getElementById('event-date').value,
            place: document.getElementById('event-place').value,
            difficulty: document.getElementById('event-difficulty').value,
            latitude: parseFloat(document.getElementById('event-latitude').value),
            longitude: parseFloat(document.getElementById('event-longitude').value),
            description: document.getElementById('event-description').value
        };
        
        // Send POST request
        const response = await fetch('/api/events', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create event');
        }
        
        const newEvent = await response.json();
        
        // Show success message
        showNotification('Event created successfully!', 'success');
        
        // Reset form and hide it
        document.getElementById('create-event-form').reset();
        document.getElementById('create-event-form').classList.add('hidden');
        document.getElementById('show-create-form').classList.remove('hidden');
        
        // Remove temp marker
        if (tempMarker) {
            map.removeLayer(tempMarker);
            tempMarker = null;
        }
        selectedLocation = null;
        
        // Reload events to show the new one
        loadEvents();
    } catch (error) {
        console.error('Error creating event:', error);
        showNotification(error.message || 'Failed to create event', 'error');
    }
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Events Map JavaScript

let map;
let markers = [];
let tempMarker = null;
let selectedLocation = null;
let useLeaflet = typeof L !== 'undefined';
let currentView = 'map'; // 'map' or 'list'
let currentEvents = [];
let editingEventId = null;

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
    if (useLeaflet) {
        // Create map centered on a default location (can be customized)
        map = L.map('map').setView([40.7128, -74.0060], 12); // New York as default
        
        // Add OpenStreetMap tiles (similar to Google Maps)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19
        }).addTo(map);
        
        // Add click handler for selecting location
        map.on('click', onMapClick);
    } else {
        // Fallback: Create a simple placeholder map
        initializeFallbackMap();
    }
}

/**
 * Initialize fallback map when Leaflet is not available
 */
function initializeFallbackMap() {
    const mapElement = document.getElementById('map');
    mapElement.innerHTML = `
        <div style="width: 100%; height: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    display: flex; flex-direction: column; align-items: center; justify-content: center; 
                    color: white; text-align: center; padding: 2rem;">
            <h2 style="margin-bottom: 1rem; font-size: 1.5rem;">Interactive Map</h2>
            <p style="margin-bottom: 1rem;">Click anywhere on this area to set event location</p>
            <div id="fallback-markers" style="margin-top: 2rem; width: 100%; max-height: 300px; overflow-y: auto;"></div>
        </div>
    `;
    
    // Add click handler for fallback map
    mapElement.addEventListener('click', function(e) {
        // Calculate relative position as coordinates
        const rect = mapElement.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Convert to lat/lng (simplified)
        const lat = 40.7128 + (y / rect.height - 0.5) * 0.1;
        const lng = -74.0060 + (x / rect.width - 0.5) * 0.1;
        
        selectedLocation = { lat: lat, lng: lng };
        document.getElementById('event-latitude').value = lat.toFixed(6);
        document.getElementById('event-longitude').value = lng.toFixed(6);
        
        showNotification('Location selected on map', 'success');
    });
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
    } else {
        // Filter by clicking on map location
        filterByMapClick(e.latlng);
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
    
    // View toggle buttons
    document.getElementById('toggle-map-view').addEventListener('click', function() {
        switchView('map');
    });
    
    document.getElementById('toggle-list-view').addEventListener('click', function() {
        switchView('list');
    });
    
    // Show create form button
    document.getElementById('show-create-form').addEventListener('click', function() {
        showCreateForm();
    });
    
    // Cancel create button
    document.getElementById('cancel-create').addEventListener('click', function() {
        cancelForm();
    });
    
    // Create event form
    document.getElementById('create-event-form').addEventListener('submit', function(e) {
        e.preventDefault();
        if (editingEventId) {
            updateEvent(editingEventId);
        } else {
            createEvent();
        }
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
        currentEvents = events;
        
        if (currentView === 'map') {
            displayEventsOnMap(events);
        } else {
            displayEventsInList(events);
        }
    } catch (error) {
        console.error('Error loading events:', error);
        showNotification('Failed to load events', 'error');
    }
}

/**
 * Display events on the map
 */
function displayEventsOnMap(events) {
    if (useLeaflet) {
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
    } else {
        // Fallback: Display events in a list
        displayEventsInFallback(events);
    }
}

/**
 * Display events in fallback mode
 */
function displayEventsInFallback(events) {
    const container = document.getElementById('fallback-markers');
    if (!container) return;
    
    if (events.length === 0) {
        container.innerHTML = '<p style="padding: 1rem;">No events to display</p>';
        return;
    }
    
    container.innerHTML = events.map(event => `
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; margin: 0.5rem; border-radius: 8px; text-align: left;">
            <h4 style="margin: 0 0 0.5rem 0;">${event.sport}</h4>
            <p style="margin: 0.25rem 0; font-size: 0.9rem;">${event.place}</p>
            <p style="margin: 0.25rem 0; font-size: 0.85rem;">${new Date(event.date).toLocaleString()}</p>
            <p style="margin: 0.25rem 0; font-size: 0.85rem;">Difficulty: ${event.difficulty}</p>
        </div>
    `).join('');
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
            <div class="event-actions">
                <button class="btn-small" onclick="editEvent(${event.id})">Edit</button>
                <button class="btn-small btn-danger" onclick="deleteEvent(${event.id})">Delete</button>
            </div>
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
        cancelForm();
        
        // Reload events to show the new one
        loadEvents();
    } catch (error) {
        console.error('Error creating event:', error);
        showNotification(error.message || 'Failed to create event', 'error');
    }
}

/**
 * Update an existing event
 */
async function updateEvent(eventId) {
    try {
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
        
        // Send PUT request
        const response = await fetch(`/api/events/${eventId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update event');
        }
        
        // Show success message
        showNotification('Event updated successfully!', 'success');
        
        // Reset form and hide it
        cancelForm();
        
        // Reload events to show the updated one
        loadEvents();
    } catch (error) {
        console.error('Error updating event:', error);
        showNotification(error.message || 'Failed to update event', 'error');
    }
}

/**
 * Edit an event - load event data into form
 */
function editEvent(eventId) {
    const event = currentEvents.find(e => e.id === eventId);
    if (!event) {
        showNotification('Event not found', 'error');
        return;
    }
    
    // Populate form
    editingEventId = eventId;
    document.getElementById('event-id').value = eventId;
    document.getElementById('event-sport').value = event.sport;
    
    // Format date for datetime-local input
    const date = new Date(event.date);
    const formattedDate = date.toISOString().slice(0, 16);
    document.getElementById('event-date').value = formattedDate;
    
    document.getElementById('event-place').value = event.place;
    document.getElementById('event-difficulty').value = event.difficulty;
    document.getElementById('event-latitude').value = event.latitude;
    document.getElementById('event-longitude').value = event.longitude;
    document.getElementById('event-description').value = event.description || '';
    
    selectedLocation = { lat: event.latitude, lng: event.longitude };
    
    // Update form title and button
    document.getElementById('form-title').textContent = 'Edit Event';
    document.getElementById('submit-btn').textContent = 'Update Event';
    document.getElementById('form-help-text').textContent = 'Click on map to change location';
    
    // Show form
    document.getElementById('create-event-form').classList.remove('hidden');
    document.getElementById('show-create-form').classList.add('hidden');
    
    // Add temp marker if using Leaflet
    if (useLeaflet && tempMarker) {
        map.removeLayer(tempMarker);
    }
    if (useLeaflet) {
        tempMarker = L.marker([event.latitude, event.longitude], {
            icon: L.divIcon({
                className: 'temp-marker',
                iconSize: [20, 20]
            })
        }).addTo(map);
        map.setView([event.latitude, event.longitude], 13);
    }
}

/**
 * Delete an event
 */
async function deleteEvent(eventId) {
    if (!confirm('Are you sure you want to delete this event?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/events/${eventId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to delete event');
        }
        
        showNotification('Event deleted successfully!', 'success');
        loadEvents();
    } catch (error) {
        console.error('Error deleting event:', error);
        showNotification(error.message || 'Failed to delete event', 'error');
    }
}

/**
 * Switch between map and list views
 */
function switchView(view) {
    currentView = view;
    
    const mapView = document.getElementById('map-view');
    const listView = document.getElementById('list-view');
    const mapBtn = document.getElementById('toggle-map-view');
    const listBtn = document.getElementById('toggle-list-view');
    
    if (view === 'map') {
        mapView.classList.add('active-view');
        listView.classList.remove('active-view');
        listView.classList.add('hidden');
        mapBtn.classList.add('active');
        listBtn.classList.remove('active');
        displayEventsOnMap(currentEvents);
    } else {
        listView.classList.add('active-view');
        mapView.classList.remove('active-view');
        listView.classList.remove('hidden');
        listBtn.classList.add('active');
        mapBtn.classList.remove('active');
        displayEventsInList(currentEvents);
    }
}

/**
 * Display events in list view
 */
function displayEventsInList(events) {
    const listContainer = document.getElementById('events-list');
    
    if (events.length === 0) {
        listContainer.innerHTML = '<p class="no-events">No events to display. Create your first event!</p>';
        return;
    }
    
    listContainer.innerHTML = events.map(event => {
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
            <div class="event-card">
                <h3>${event.sport}</h3>
                <p><strong>📍 ${event.place}</strong></p>
                <p>🗓️ ${formattedDate}</p>
                ${event.description ? `<p>${event.description}</p>` : ''}
                <div class="event-meta">
                    <span class="event-difficulty ${difficultyClass}">${event.difficulty}</span>
                    <span>📍 ${event.latitude.toFixed(4)}, ${event.longitude.toFixed(4)}</span>
                </div>
                <div class="event-actions">
                    <button class="btn btn-primary" onclick="editEvent(${event.id})">Edit</button>
                    <button class="btn btn-secondary" onclick="deleteEvent(${event.id})">Delete</button>
                    ${useLeaflet ? `<button class="btn btn-primary" onclick="showOnMap(${event.latitude}, ${event.longitude})">Show on Map</button>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Show event location on map
 */
function showOnMap(lat, lng) {
    switchView('map');
    if (useLeaflet) {
        map.setView([lat, lng], 15);
    }
}

/**
 * Filter events by clicking on map
 */
function filterByMapClick(latlng) {
    // Find nearest event within 1km
    const nearbyEvents = currentEvents.filter(event => {
        const distance = calculateDistance(
            latlng.lat, latlng.lng,
            event.latitude, event.longitude
        );
        return distance < 1; // 1km radius
    });
    
    if (nearbyEvents.length > 0) {
        // Get the place name from the nearest event
        const place = nearbyEvents[0].place;
        document.getElementById('place-filter').value = place;
        loadEvents();
        showNotification(`Filtering by location: ${place}`, 'info');
    } else {
        showNotification('No events found near this location', 'info');
    }
}

/**
 * Calculate distance between two points (Haversine formula)
 */
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of Earth in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

/**
 * Show create form
 */
function showCreateForm() {
    editingEventId = null;
    document.getElementById('form-title').textContent = 'Create Event';
    document.getElementById('submit-btn').textContent = 'Create Event';
    document.getElementById('form-help-text').textContent = '* Click on the map to set event location';
    document.getElementById('create-event-form').classList.remove('hidden');
    document.getElementById('show-create-form').classList.add('hidden');
}

/**
 * Cancel form and reset
 */
function cancelForm() {
    document.getElementById('create-event-form').classList.add('hidden');
    document.getElementById('show-create-form').classList.remove('hidden');
    document.getElementById('create-event-form').reset();
    
    // Remove temp marker
    if (tempMarker && useLeaflet) {
        map.removeLayer(tempMarker);
        tempMarker = null;
    }
    selectedLocation = null;
    editingEventId = null;
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

document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results-container');
    const errorMessage = document.getElementById('error-message');

    let timeline = null;

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (query) {
            performSearch(query);
        }
    });

    function performSearch(query) {
        errorMessage.textContent = '';
        resultsContainer.style.display = 'none';
        resultsContainer.innerHTML = '<p>Buscando...</p>';
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `query=${encodeURIComponent(query)}`
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || `HTTP error! status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            errorMessage.textContent = `Error al buscar: ${error.message}. Por favor, intente de nuevo.`;
            resultsContainer.style.display = 'none';
        });
    }

    function displayResults(result) {
        resultsContainer.innerHTML = `
            <h2>${result.name}</h2>
            <p><strong>Tipo:</strong> ${result.type}</p>
            <p><strong>País:</strong> ${result.country}</p>
            <p><strong>Período de actividad:</strong> ${result['life-span'].begin || 'Desconocido'} - ${result['life-span'].ended ? result['life-span'].end : 'Presente'}</p>
            <p><strong>Géneros:</strong> ${result.genres.join(', ') || 'No especificado'}</p>
            
            <h3>Línea de tiempo:</h3>
            <div id="timeline-container"></div>
            <div id="event-details"></div>

            <h3>Colaboraciones:</h3>
            <ul class="collaborations-list">
                ${result.collaborations.map(collab => `<li>${collab[1]}</li>`).join('')}
            </ul>

            <h3>Enlaces de interés:</h3>
            <ul class="links-list">
                ${result.urls.map(url => `<li><a href="${url}" target="_blank">${url}</a></li>`).join('')}
            </ul>
        `;
        resultsContainer.style.display = 'block';
        createTimeline(result.timeline_events);
    }

    function createTimeline(events) {
        if (events.length === 0) {
            document.getElementById('timeline-container').innerHTML = '<p>No hay eventos para mostrar en la línea de tiempo.</p>';
            return;
        }

        const container = document.getElementById('timeline-container');
        container.innerHTML = ''; // Limpiar el contenedor

        const items = new vis.DataSet(events.map(event => ({
            id: event.id,
            content: event.title,
            start: event.date,
            type: event.type === 'release' ? 'box' : 'point',
            className: event.type
        })));

        const options = {
            height: '400px',
            start: events[0].date,
            end: events[events.length - 1].date
        };

        if (timeline) {
            timeline.destroy();
        }

        timeline = new vis.Timeline(container, items, options);

        timeline.on('select', function(properties) {
            const selectedEvent = events.find(event => event.id === properties.items[0]);
            if (selectedEvent) {
                document.getElementById('event-details').innerHTML = `
                    <h4>${selectedEvent.title}</h4>
                    <p>Fecha: ${selectedEvent.date}</p>
                    <p>Tipo: ${selectedEvent.type === 'release' ? 'Lanzamiento' : 'Colaboración'}</p>
                `;
            }
        });
    }
});
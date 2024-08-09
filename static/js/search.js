document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results-container');

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (query) {
            performSearch(query);
        }
    });

    function performSearch(query) {
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `query=${encodeURIComponent(query)}`
        })
        .then(response => response.json())
        .then(data => {
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function displayResults(result) {
        resultsContainer.innerHTML = '';
        if (result.error) {
            resultsContainer.innerHTML = `<p>${result.error}</p>`;
            return;
        }

        const artistCard = document.createElement('div');
        artistCard.classList.add('artist-card');
        artistCard.innerHTML = `
            <h2>${result.name}</h2>
            <p><strong>Tipo:</strong> ${result.type}</p>
            <p><strong>País:</strong> ${result.country}</p>
            <p><strong>Período de actividad:</strong> ${result['life-span'].begin || 'Desconocido'} - ${result['life-span'].ended ? result['life-span'].end : 'Presente'}</p>
            <p><strong>Géneros:</strong> ${result.genres.join(', ') || 'No especificado'}</p>
            <h3>Lanzamientos recientes:</h3>
            <ul>
                ${result.releases.slice(0, 5).map(release => `<li>${release.title} (${release.date || 'Fecha desconocida'})</li>`).join('')}
            </ul>
            <h3>Enlaces oficiales:</h3>
            <ul>
                ${result.urls.map(url => `<li><a href="${url}" target="_blank">${url}</a></li>`).join('')}
            </ul>
        `;
        resultsContainer.appendChild(artistCard);
    }
});
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results-container');
    const errorMessage = document.getElementById('error-message');

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (query) {
            performSearch(query);
        }
    });

    function performSearch(query) {
        errorMessage.textContent = '';
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
            resultsContainer.innerHTML = '';
        });
    }

    function displayResults(result) {
        resultsContainer.innerHTML = '';
        const artistCard = document.createElement('div');
        artistCard.classList.add('artist-card');
        artistCard.innerHTML = `
            <h2>${result.name}</h2>
            <p><strong>Tipo:</strong> ${result.type}</p>
            <p><strong>País:</strong> ${result.country}</p>
            <p><strong>Período de actividad:</strong> ${result['life-span'].begin || 'Desconocido'} - ${result['life-span'].ended ? result['life-span'].end : 'Presente'}</p>
            <p><strong>Géneros:</strong> ${result.genres.join(', ') || 'No especificado'}</p>
            
            <h3>Lanzamientos recientes:</h3>
            <div id="releases-container"></div>
            
            <h3>Artistas relacionados:</h3>
            <ul>
                ${result.related_artists.map(artist => `<li>${artist.name}</li>`).join('')}
            </ul>
            
            <h3>Enlaces oficiales:</h3>
            <ul>
                ${result.urls.map(url => `<li><a href="${url}" target="_blank">${url}</a></li>`).join('')}
            </ul>
        `;
        resultsContainer.appendChild(artistCard);

        const releasesContainer = document.getElementById('releases-container');
        let currentPage = 1;
        const releasesPerPage = 5;

        function displayReleases(page) {
            const start = (page - 1) * releasesPerPage;
            const end = start + releasesPerPage;
            const pageReleases = result.releases.slice(start, end);

            releasesContainer.innerHTML = pageReleases.map(release => `
                <div class="release-item">
                    <h4>${release.title}</h4>
                    <p>Fecha: ${release.date}</p>
                    <p>Tipo: ${release.type}</p>
                    <p>Número de pistas: ${release.track_count}</p>
                </div>
            `).join('');

            if (result.releases.length > releasesPerPage) {
                const paginationControls = document.createElement('div');
                paginationControls.classList.add('pagination-controls');
                paginationControls.innerHTML = `
                    <button id="prev-page" ${page === 1 ? 'disabled' : ''}>Anterior</button>
                    <span>Página ${page} de ${Math.ceil(result.releases.length / releasesPerPage)}</span>
                    <button id="next-page" ${end >= result.releases.length ? 'disabled' : ''}>Siguiente</button>
                `;
                releasesContainer.appendChild(paginationControls);

                document.getElementById('prev-page').addEventListener('click', () => {
                    if (currentPage > 1) {
                        displayReleases(--currentPage);
                    }
                });

                document.getElementById('next-page').addEventListener('click', () => {
                    if (currentPage < Math.ceil(result.releases.length / releasesPerPage)) {
                        displayReleases(++currentPage);
                    }
                });
            }
        }

        displayReleases(currentPage);
    }
});
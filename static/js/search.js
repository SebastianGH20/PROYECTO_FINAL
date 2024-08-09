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

    function displayResults(results) {
        resultsContainer.innerHTML = '';
        results.forEach(result => {
            const resultCard = document.createElement('div');
            resultCard.classList.add('result-card');
            resultCard.innerHTML = `
                <h3>${result.artist}</h3>
                <ul>
                    ${result.releases.map(release => `<li>${release.title} (${release.date || 'N/A'})</li>`).join('')}
                </ul>
            `;
            resultsContainer.appendChild(resultCard);
        });
    }
});
document.getElementById('searchForm').addEventListener('submit', event => {
    event.preventDefault();
    const searchQuery = document.getElementById('searchInput').value;
    const newUrl = new URL(window.location.href);
    newUrl.searchParams.set('query', searchQuery);
    window.location.href = newUrl.toString();
});


document.getElementById('chooseDatasetSelect').addEventListener("change", event => {
    const newUrl = new URL(window.location.href.split('?')[0]);
    newUrl.searchParams.set('dataset', event.target.value);
    window.location.href = newUrl.toString();
});
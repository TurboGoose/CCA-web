$(document).ready(function () {
    $("#searchForm").submit(function (event) {
        if (!getCurrentDataset()) {
            return
        }
        event.preventDefault();
        const searchQuery = $("searchInput").value();
        window.location.href = addQueryParamToCurrentURL(searchQuery);
    })

    $("#chooseDatasetSelect").change(function (event) {
        redirectToNewDataset(event.target.value);
    })
})

function getCurrentDataset() {
    const url = new URL(window.location.href);
    return url.searchParams.get("dataset");
}

function addQueryParamToCurrentURL(query) {
    const newUrl = new URL(window.location.href);
    newUrl.searchParams.set('query', query);
    return newUrl.toString();
}

function redirectToNewDataset(dataset) {
    const newUrl = new URL(window.location.pathname);
    newUrl.searchParams.set('dataset', dataset);
    window.location.href = newUrl.toString();
}

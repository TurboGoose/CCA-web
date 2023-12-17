const DEFAULT_LABEL_PLACEHOLDER = "Choose label";
let currentLabel = DEFAULT_LABEL_PLACEHOLDER;

// choose selected label
$("#chooseLabelSelect").each(function () {
    if ($(this).children().length === 0) {
        $(this).append(
            $(`<option value='default'>${DEFAULT_LABEL_PLACEHOLDER}</option>`)
        )
    }
    currentLabel = $(this).children(":first")
        .prop("selected", true)
        .prop("disabled", true)
        .text();
});


// change label
$("#chooseLabelSelect").change(function () {
    $(this).children("option[value='default']").remove();
    $(this).children("option:selected").each(function () {
        currentLabel = $(this).text();
    });
    $(this).children("option:selected")
        .prop("disabled",true)
        .siblings().removeAttr("disabled");
})

function getCurrentDataset() {
    const url = new URL(window.location.href);
    return url.searchParams.get("dataset");
}

// assign label
$("#assignLabelButton").click(function () {
    if (!getCurrentDataset() || currentLabel === DEFAULT_LABEL_PLACEHOLDER) {
        return;
    }
    const ids = [];
    $("input[id^='checkbox-']:checked").each(function() {
        const checkbox = $(this).prop("checked", false).get(0);
        const id = checkbox.id.split("-")[1];
        ids.push(parseInt(id, 10));
    });

    const url = new URL(window.location.origin);
    url.pathname = "/mark";

    const body = {"label": currentLabel, "dataset": getCurrentDataset(), "ids": ids};

    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    }).then(function () {
        ids.forEach(id => $(`td[id="label-${id}"]`).text(currentLabel))
    });
});

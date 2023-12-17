function getCurrentDataset() {
    const url = new URL(window.location.href);
    return url.searchParams.get("dataset");
}

const DEFAULT_LABEL_PLACEHOLDER = 'Choose label';
let labelSelect = document.getElementById('chooseLabelSelect');

function setDefaultLabel() {
    if (labelSelect.options.length === 0) {
        console.log()
        let placeholderOption = document.createElement('option');
        placeholderOption.textContent = DEFAULT_LABEL_PLACEHOLDER;
        placeholderOption.value = 'default';
        labelSelect.appendChild(placeholderOption);
    }
    const firstOpt = labelSelect.options[0];
    firstOpt.selected = true;
    firstOpt.disabled = true;
    return firstOpt.text;
}

let currentLabel = setDefaultLabel();

// change label
document.getElementById('chooseLabelSelect').addEventListener("change", event => {
    selectOption('chooseLabelSelect', event.target.value);
});

function selectOption(selectId, optionValue) {
    currentLabel = optionValue;
    const selectElement = document.getElementById(selectId);
    const options = selectElement.options;

    for (let i = 0; i < options.length; i++) {
        if (options[i].disabled) {
            if (options[i].text === DEFAULT_LABEL_PLACEHOLDER) {
                labelSelect.remove(i);
            } else {
                options[i].disabled = false;
            }
            break;
        }
    }

    for (let j = 0; j < options.length; j++) {
        if (options[j].value === optionValue) {
            options[j].disabled = true;
            break;
        }
    }
}

// assign label
document.getElementById('assignLabelButton').addEventListener("click", event => {
    if (!getCurrentDataset() || currentLabel === DEFAULT_LABEL_PLACEHOLDER) {
        return
    }
    const checkedBoxes = document.querySelectorAll('input[id^="checkbox-"]:checked');
    const ids = [];
    checkedBoxes.forEach(element => {
        element.checked = false;
        const checkboxId = element.id;
        const parts = checkboxId.split('-');
        const id = parts[1];
        ids.push(parseInt(id, 10));
    });

    const body = {"label": currentLabel, "dataset": getCurrentDataset(), "ids": ids};
    const url = new URL(window.location.href.split("?")[0]);
    url.pathname = "/mark";

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    });

    ids.forEach(id => {
        const label = document.querySelector(`td[id^="label-${id}"]`);
        label.innerText = currentLabel;
    })
});
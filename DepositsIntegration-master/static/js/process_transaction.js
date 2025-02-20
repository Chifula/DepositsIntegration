const processBtn = document.getElementById('process-btn');
const searchBtn = document.getElementById('search-button');
const modalSubmitBtn = document.getElementById('modal-submit-btn');
const loader = document.getElementById('spinner')
const rows = document.querySelectorAll('#table-body tr');
const checkboxes = document.querySelectorAll('input[type="checkbox"]');
const searchInput = document.getElementById('search-input');
const filterOptions = document.getElementById('filter-options');

let selectedVendorsInvoiceNumber = [];
let selectedPageNumber = 1;
let numberOfPages = 0;
let hasClickedOnSearchBtn = false;
let query_params = [];
let selectedTransactionType = {}

let combinedValues = [];
sessionStorage.clear();

addCheckBoxandSelectValues(rows);
addEventListenerToCheckboxes(checkboxes);
addEventListenerToAnchorTag();
addEventListenersToSelect(rows)


function addEventListenersToSelect(rows) {
    rows.forEach(row => {
        const selectTags = row.querySelectorAll('select');
        selectTags.forEach(select => {
            select.addEventListener('change', () => {
                updateTransactionType(selectTags[0]);
                const accountName = selectTags[0].value;
                const transactionType = selectTags[1].value;

                const trow = select.closest('tr');
                const inputElement = trow.querySelector('input[name="transaction"]');
                const value = inputElement.value;
                if (transactionType && accountName) {
                    if (value) {
                        inputElement.removeAttribute('disabled');
                    } else {
                        inputElement.setAttribute('disabled', 'disabled');
                    }
                    sessionStorage.setItem("accountName-" + value, accountName);
                    sessionStorage.setItem("transactionType-" + value, transactionType);
                    console.log(sessionStorage)
                } else {
                    sessionStorage.removeItem("accountName-" + value);
                    sessionStorage.removeItem("transactionType-" + value);
                }
            });
        });
    });
}

function addCheckBoxandSelectValues(rows) {
    rows.forEach(row => {
        const value = row.id;
        const inputElement = row.querySelector('input[name="transaction"]');
        const selectTags = row.querySelectorAll('select');
        const accountName = sessionStorage.getItem("accountName-" + value);
        const transactionType = sessionStorage.getItem("transactionType-" + value);
        const checkbox = sessionStorage.getItem(value)
        if (accountName && transactionType) {
            if (checkbox) {
                inputElement.checked = true
            }
            selectTags[0].value = accountName;
            selectTags[1].value = transactionType;
            inputElement.removeAttribute('disabled');
        } else {
            selectTags[0].value = ''; // Reset the select values if not found in sessionStorage
            selectTags[1].value = '';
            inputElement.setAttribute('disabled', 'disabled');
        }
    });
}


function addEventListenerToCheckboxes(checkboxes) {
    checkboxes.forEach(cb => {
        cb.addEventListener('change', () => {
            if (cb.checked) {
                const row = cb.closest('tr');
                const rowData = {
                    values: [],
                };
                // Iterate over each cell
                for (let j = 0; j < row.cells.length; j++) {
                    const cell = row.cells[j];

                    if (j === 6) {
                        const select = cell.querySelector('.form-select');
                        fetch(`account_details/?account_name=${select.value}`)
                            .then(response => response.json())
                            .then(res => {

                                rowData.values.push(res.account_details[0].account_no);
                                rowData.values.push(res.account_details[0].sort_code);
                                rowData.values.push(res.account_details[0].bicCode);
                                rowData.values.push(res.account_details[0].bank_name);
                            });
                        rowData.values.push(select.value);
                    } else if (j === 7) {
                        const select = cell.querySelector('.form-select');
                        rowData.values.push(select.value);
                    } else {
                        // Handle text cells
                        rowData.values.push(cell.textContent);
                    }
                }
                // Add the row data to the combined values array
                if (!combinedValues.some(item => JSON.stringify(item) === JSON.stringify(rowData))) {
                    combinedValues.push(rowData);
                    processBtn.removeAttribute('disabled')
                    //console.log(combinedValues[0].values[0]);
                }
                const value = cb.value;
                const checked = cb.checked;
                addSelectedVendorsInvoiceNumber(cb.value);
                sessionStorage.setItem(value, checked);
                saveSelectedRows('table-body');
            }
        })
    })
}

var isScrolledToTop = true;

function scrollToTopOrBottom() {
    if (isScrolledToTop) {
        scrollToBottom();
        isScrolledToTop = false;
    } else {
        scrollToTop();
        isScrolledToTop = true;
    }
}

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: "smooth" // Optional: Add smooth scrolling animation
    });
}

function scrollToBottom() {
    window.scrollTo({
        top: document.documentElement.scrollHeight,
        behavior: "smooth" // Optional: Add smooth scrolling animation
    });
}

function updateTransactionType(select) {
    const rows = select.closest('tr');
    console.log(rows)

    fetch(`account_details/?account_name=${select.value}`)
        .then(response => response.json())
        .then(res => {
            const accountNo = res.account_details[0].account_no;
            fetch(`account_number/?acc_name=${accountNo}`)
                .then(data => data.json())
                .then(d => {
                    if (d.resp.length === 0) {
                        const selectTags = rows.querySelectorAll('select');
                        transType = selectTags[1]
                        const options = transType.querySelectorAll('option');

                        options.forEach(option => {
                            if (option.value === 'IFT') {
                                option.disabled = true;
                                if (transType.value === 'IFT') {
                                    transType.value = '';
                                }
                            }
                        });


                    }
                    ;
                });
        })


}


function addSelectedVendorsInvoiceNumber(invoiceId) {

    if (!selectedVendorsInvoiceNumber.includes(invoiceId)) {
        selectedVendorsInvoiceNumber.push(invoiceId);

    }
}

function saveSelectedRows(tableID) {
    let rows = document.querySelectorAll(`#${tableID} tr`);
    rows.forEach((row) => {
            let cb = row.querySelector('td input[type="checkbox"]')
            if (cb.checked) {
                let transactionType = row.querySelector('td select[name="transaction_type"]').value;
                // let accountName = row.querySelector('td select[name="account_name"]').value;

                //selectedAccountName[cb.value] = accountName;
                selectedTransactionType[cb.value] = transactionType;
                console.log(selectedTransactionType)
            }
        }
    )
}

function createModalTableBody(tableBodyID) {

    let tableBody = document.getElementById(tableBodyID);
    tableBody.innerHTML = '';
    combinedValues.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.values[1]}</td>
            <td>${item.values[2]}</td>
            <td>${item.values[3]}</td>
            <td>${item.values[4]}</td>
            <td>${item.values[5]}</td>
            <td>${item.values[6]}</td>
            <td>${item.values[7]}</td>
            <td>${item.values[8]}</td>
            <td>${item.values[9]}</td>
            <td>${item.values[10]}</td>`


        tableBody.appendChild(tr);
    })

}


// handles the click even of the anchor tags
function handleClick(event) {
    event.preventDefault();
    const url = event.target.getAttribute('href');
    fetch(url)
        .then(response => response.text())
        .then(html => {
            updateTableAndPaginator(html)
            addEventListenerToAnchorTag();
        });
}

function addEventListenerToAnchorTag() {
    const paginationLinks = document.querySelectorAll('.custom-pagination a');
    paginationLinks.forEach(link => {
        link.addEventListener('click', handleClick); // Add the handleClick function as the event listener
    });
}

function removeEventListenerFromAnchorTag() {
    const paginationLinks = document.querySelectorAll('.custom-pagination a');
    paginationLinks.forEach(link => {
        link.removeEventListener('click', handleClick); // Remove the handleClick function as the event listener
    });
}

function updateTableAndPaginator(html) {
    const parser = new DOMParser();
    const newDoc = parser.parseFromString(html, 'text/html');

    const newRow = newDoc.querySelectorAll("#table-body tr");
    const newCheckboxes = newDoc.querySelectorAll('input[type="checkbox"]');

    addCheckBoxandSelectValues(newRow);
    addEventListenersToSelect(newRow);
    addEventListenerToCheckboxes(newCheckboxes);

    const newTable = newDoc.getElementById('table-body');
    const newPaginator = newDoc.getElementById('paginator');
    document.getElementById('table-body').replaceWith(newTable);
    document.getElementById('paginator').replaceWith(newPaginator);

    // Add any other necessary post-update operations
}

searchBtn.addEventListener('click', (e) => {
    e.preventDefault();
    hasClickedOnSearchBtn = true;
    query_params = [searchInput.value, filterOptions.value];

    fetchSearchResults(query_params, selectedPageNumber);
})

function fetchSearchResults(queryParams, page) {
    const searchInput = queryParams[0];
    const filterOptions = queryParams[1];

    fetch(`search/?search_params=${searchInput}&filter_options=${filterOptions}&page=${page}`)
        .then(response => response.text())
        .then(html => {
            // Parse the HTML response
            const parser = new DOMParser();
            const newDoc = parser.parseFromString(html, 'text/html');

            // Get the new HTML elements
            const newRow = newDoc.querySelectorAll("#table-body tr");
            const newCheckboxes = newDoc.querySelectorAll('input[type="checkbox"]');
            const newTable = newDoc.getElementById('table-body');
            const newPaginator = newDoc.getElementById('paginator');
            numberOfPages = parseInt(newPaginator.dataset.numPages);
            console.log(numberOfPages, selectedPageNumber)
            // Update the pagination links
            // Add event listeners to the new elements
            addCheckBoxandSelectValues(newRow);
            addEventListenersToSelect(newRow);
            addEventListenerToCheckboxes(newCheckboxes);

            // Replace the existing table and paginator with the new ones
            const tableBody = document.getElementById('table-body');
            const paginator = document.getElementById('paginator');

            tableBody.replaceWith(newTable);
            paginator.replaceWith(newPaginator)
            console.log(newPaginator)
            updatePaginationLinks(newPaginator);
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
        });
}


modalSubmitBtn.addEventListener('click', (e) => {
    loader.classList.remove('d-none')
    e.preventDefault()
///    // Send selected invoice numbers & transaction type to server using ajax
    $.ajax({
        type: 'POST',
        url: 'post-transactions/',
        data: {
            'csrfmiddlewaretoken': getCSRFToken(),
            'transactions': JSON.stringify(combinedValues),
            'invoice_ids[]': JSON.stringify(selectedVendorsInvoiceNumber),
            'transaction_type': JSON.stringify(selectedTransactionType),
            //'account_name':JSON.stringify(selectedAccountName)
        },
        dataType: 'json',
    }).then(res => {
        loader.classList.add('d-none')
        if (res.stats !== 200) {
            Swal.fire({
                icon: 'error',
                title: 'Your Request Could Not Be processed:',
                text: res.resps,
                confirmButtonText: "OK",
                timer: 2000,
                footer: 'Try Again Later'
            })
            $('#post-transaction-modal').modal('hide');
        } else {
            Swal.fire({
                icon: 'success',
                title: 'Your Request Has Been Successfully Processed:',
                confirmButtonText: "OK",
                timer: 2000,
                text: res.resps,
            }).then(() => {
                window.location.href = 'dashboard';
            });
        }

    }).catch(err => console.log(err));

});

processBtn.addEventListener('click', (e) => {

    e.preventDefault();
    createModalTableBody('modal-table-body');

});

// Add event listener to change page links

function getCSRFToken() {
    let csrfToken = document.cookie.split('; ').find(row => row.startsWith('csrftoken')).split('=')[1];
    if (csrfToken == null) {
        csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    }
    return csrfToken;
}

function updatePaginationLinks(newDoc) {
    const nextLink = newDoc.querySelector('#next')
    if (nextLink) {
        nextPageLink(nextLink)
    }
    const firstLink = newDoc.querySelector('#first')
    if (firstLink) {
        firstPageLink(firstLink)
    }
    const lastLink = newDoc.querySelector('#last')
    if (lastLink) {
        lastPageLink(lastLink)
    }
    const previousLink = newDoc.querySelector('#previous')
    if (previousLink) {
        previousPageLink(previousLink)
    }
}

async function goToPage() {

    try {
        fetchSearchResults(query_params, selectedPageNumber)
    } catch (err) {
        console.log(err);
    }
}

function nextPageLink(nextLink) {
    nextLink.addEventListener('click', (e) => {
        if (hasClickedOnSearchBtn === true) {
            e.preventDefault();
            if (selectedPageNumber !== numberOfPages) {
                selectedPageNumber += 1;
            }

            goToPage();

        }
    });
}

function previousPageLink(previousLink) {
    previousLink.addEventListener('click', (e) => {
        if (hasClickedOnSearchBtn === true) {
            e.preventDefault();
            if (selectedPageNumber !== 1) {
                selectedPageNumber -= 1;
            }

            goToPage();
        }
    });
}

function lastPageLink(lastLink) {
    lastLink.addEventListener('click', (e) => {
        if (hasClickedOnSearchBtn === true) {
            e.preventDefault();
            selectedPageNumber = numberOfPages;
            goToPage();
        }
    });
}

function firstPageLink(firstLink) {
    firstLink.addEventListener('click', (e) => {
        if (hasClickedOnSearchBtn === true) {
            e.preventDefault();
            selectedPageNumber = 1;
            goToPage();
        }
    });
}





const sortCodeDiv = document.getElementById("sortCodeDiv");
const sortCodeInput = document.getElementById("sortcode");
const accountname = document.getElementById('accountname')
const bankNameSelect = document.getElementById('bankNameSelect')
const branchDescSelect = document.getElementById('branchDesc');
const branchNameDv = document.getElementById('branchNameSelectDiv')
const accountNumber = document.getElementById('accountno')
const submitBtn = document.getElementById('submit')
const accInput = document.getElementById('acc_if_zicb')
const zicbDiv = document.getElementById('zicb_bank_details')
const  zicbBranchName = document.getElementById('zicb_branch_name')
const zicbSortCode = document.getElementById('zicb_sort_code')
const detailsForm = document.getElementById('bankDetailsForm')

let groupedData = {};
const selectedBank = []

service_IDs = {
    'ATLASMARA': 347,
    'AB BANK': 329,
    'ACCESS BANK': 332,
    'ABSA': 377,
    'BANK OF CHINA': 317,
    'FIRST CAPITAL BANK': 314,
    'CITIBANK': 368,
    'ECOBANK': 320,
    'FIRST ALLIANCE BANK': 326,
    'FIRST NATIONAL BANK': 383,
    'INDO ZAMBIA BANK': 371,
    'INVESTRUST': 380,
    'STANDARD CHARTERED': 362,
    'STANBIC': 374,
    'UNITED BANK FOR AFRICA': 323,
    'ZANACO': 359,
    'ZNBS': 356
}

loadBankList();

function loadBankList() {
    fetch('loadBanks')
        .then(response => response.json())
        .then(data => {
                // Group the data by bank
                data.forEach(entry => {
                    const bankName = entry.bankName;
                    if (!groupedData[bankName]) {
                        groupedData[bankName] = [];
                    }
                    groupedData[bankName].push(entry);

                });
                for (const bankName in groupedData) {
                    const option = document.createElement('option');
                    option.value = bankName;
                    option.textContent = bankName;
                    bankNameSelect.appendChild(option);
                }
            }
        )
        .catch(error => {
            console.error(error);
        });
}

function addBankServiceID(bank) {
    if (selectedBank === []) {
        selectedBank.push(bank)
    } else {
        selectedBank[0] = bank
    }
}

accountNumber.addEventListener('blur', (ev) => {
    const bankN = selectedBank[0];
    console.log(bankN)
    if (bankN === 'ZICB') {
        fetch(`verify_account/zicb/?account_no=${ev.target.value}`)
            .then(response => response.json())
            .then(data => {
                let accountName;
                if (data.response === false) {
                    submitBtn.setAttribute('disabled', 'disabled')
                    accountname.value = ''

                } else {
                    accountName = data.response[0].accountTitle
                    console.log(accountName)
                    accountname.value = accountName
                    accountname.readOnly = true
                    zicbBranchName.value = data.response[0].branchname
                    zicbSortCode.value = data.response[0].brnCode
                    zicbDiv.classList.remove('d-none')
                    submitBtn.removeAttribute('disabled')



                }
            })
    } else {
        const service_id = service_IDs[bankN]
        fetch(`verify_account/other/?account_no=${ev.target.value}&service_id=${service_id}`)
            .then(response => response.json())
            .then(data => {
                if (data.response === false) {
                    submitBtn.setAttribute('disabled', 'disabled')

                } else {

                    submitBtn.removeAttribute('disabled')
                }
            })

    }
})
bankNameSelect.addEventListener('change', (ev) => {

    const bankName = ev.target.value
    addBankServiceID(bankName.toUpperCase())
    if (bankName === 'ZICB') {
        accInput.classList.remove('d-none');
    /*} else {
        branchNameDv.classList.remove('d-none')
        branchDescSelect.innerHTML = ''
        const bankEntries = groupedData[bankName]
        for (const entry of bankEntries) {
            const branchDesc = entry.branchDesc;
            const option = document.createElement('option');
            option.value = branchDesc;
            option.textContent = branchDesc;
            branchDescSelect.appendChild(option);
        }
        branchDescSelect.addEventListener('change', (ev) => {
            sortCodeDiv.classList.remove('d-none')
            const branchDesc = ev.target.value
            const sortCode = getSortCode(bankName, branchDesc); // Get the sort code based on the selected bank name and branch description
            sortCodeInput.value = sortCode;
            sortCodeInput.readOnly = true

        })*/
    }
})

function getSortCode(bankName, branchDesc) {
    // Iterate over the grouped data to find the matching bank name and branch description
    const bankEntries = groupedData[bankName]
    for (const entry of bankEntries) {

        if (entry.branchDesc === branchDesc) {
            return entry.sortCode; // Return the sort code of the matched entry
        }
    }
    return ''; // Return an empty string if no matching entry is found
}

/*detailsForm.addEventListener('submit', function(event) {
  event.preventDefault(); // Prevent default form submission

  // Collect form data
  const formData = new FormData(detailsForm);

  // Send an HTTP POST request to the Django backend
  fetch('/bank_details/upload/', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    // Handle the response from the backend
    console.log(data);
    // Perform any necessary actions based on the response
  })
  .catch(error => {
    // Handle any errors that occurred during the request
    console.error(error);
  });
});


let sortC = document.getElementById('sortcode').value
const sortCodeInput = document.getElementById('sortcode')
sortCodeInput.addEventListener('input', handleInputChange);
sortCodeInput.addEventListener('keydown', handleKeyDown);
sortCodeInput.addEventListener('blur', handleBlur);

function handleInputChange(event) {
    const currentValue = event.target.value;
    if (currentValue !== sortC) {
        // Value has changed
        sortC = currentValue;
        searchBySortCode(currentValue);
    }
}

function handleKeyDown(event) {
    if (event.key === 'Enter') {
        // Enter key pressed, handle the change
        const currentValue = event.target.value;
        if (currentValue !== sortC) {
            sortC = currentValue;
            searchBySortCode(currentValue);
        }
    }
}

function handleBlur(event) {
    // Handle change when the input loses focus
    const currentValue = event.target.value;
    if (currentValue !== sortC) {
        sortC = currentValue;
        searchBySortCode(currentValue);
    }
}

function createChainedDropdown() {


}

function searchBySortCode(sortC) {

    branchNameDiv.innerHTML = "";
    bankNameDiv.innerHTML = "";
    // Iterate over each bank in the grouped data
    for (const bankName in groupedData) {
        const bankEntries = groupedData[bankName];

        // Iterate over each entry in the bank
        for (const entry of bankEntries) {
            if (entry.sortCode === sortC) {
                const bankName = entry.bankName
                const branchName = entry.branchDesc
                var branchNameLabel = document.createElement("label");
                branchNameLabel.className = "formbold-form-label";
                branchNameLabel.textContent = "Branch Name";
                var branchNameInput = document.createElement("input");
                branchNameInput.className = "formbold-form-input"
                branchNameInput.type = "text";
                branchNameInput.value = branchName;
                branchNameInput.readOnly = true;

                var bankNameLabel = document.createElement("label");
                bankNameLabel.className = "formbold-form-label";
                bankNameLabel.textContent = "Bank Name";
                var bankNameInput = document.createElement("input");
                bankNameInput.type = "text";
                bankNameInput.className = "formbold-form-input"
                bankNameInput.value = bankName;
                bankNameInput.readOnly = true;

                bankNameDiv.appendChild(bankNameLabel)
                bankNameDiv.appendChild(bankNameInput)
                bankNameDiv.classList.remove('d-none')

                branchNameDiv.appendChild(branchNameLabel)
                branchNameDiv.appendChild(branchNameInput)
                branchNameDiv.classList.remove('d-none')
            }

        }
    }

};*/
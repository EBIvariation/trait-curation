const csrftoken = Cookies.get("csrftoken");

let selectedRowIndex = -1;
let selectedTableId = "";
let currentTraitId = -1;
let selectedTermId = -1;

function selectRow(row, tableId, traitId, termId) {
  selectedTableId = tableId;
  selectedRowIndex = row.rowIndex;
  currentTraitId = traitId;
  selectedTermId = termId;
  selectedRow = document.getElementById(selectedTableId).rows[selectedRowIndex];
  if (selectedRow.classList.contains("suggestion-table__row--current")) {
    selectedRowIndex = -1;
    return;
  }
  for (const row of document.getElementsByTagName("tr"))
    row.classList.remove("suggestion-table__row--selected");
  selectedRow.classList.add("suggestion-table__row--selected");
}

function mapButtonClicked() {
  if (selectedRowIndex < 1) return;
  axios
    .post(`/traits/${currentTraitId}/mapping`, {'term': parseInt(selectedTermId)})
    .then((response) => {
      // handle success
      console.log(response);
      location.reload(); 
    });
}

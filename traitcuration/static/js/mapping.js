/*
This module contains all the funcionality for mapping traits to ontology terms, via a trait's suggestion table
*/
let selectedRowIndex = -1;
let selectedTableId = "";
let currentTraitId = -1;
let selectedTermId = -1;

/* 
This function takes in the clicked row of the mapping suggestion table, and the term and trait ids for its mapping
suggestion, and sets them as selected
*/
function selectRow(row, tableId, traitId, termId) {
  selectedTableId = tableId;
  selectedRowIndex = row.rowIndex;
  currentTraitId = traitId;
  selectedTermId = termId;
  // If the currently mapped row was selected, set the selected index as -1 to prevent unnecessary mapping requests
  selectedRow = document.getElementById(selectedTableId).rows[selectedRowIndex];
  if (selectedRow.classList.contains("suggestion-table__row--current")) {
    selectedRowIndex = -1;
    return;
  }
  // Remove the 'selected' class from all table rows, and add it to the selected row
  for (const row of document.getElementsByTagName("tr"))
    row.classList.remove("suggestion-table__row--selected");
  selectedRow.classList.add("suggestion-table__row--selected");
}

// This function makes an ajax request to create a current mapping with the selected term 
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

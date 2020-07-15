/*
This module contains all the funcionality for mapping traits to ontology terms, via a trait's suggestion table
*/
let selectedRowIndex = -1;
let selectedTableId = "";
let currentTraitId = window.location.href.split("/").slice(-2)[0];
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
    .post(`/traits/${currentTraitId}/mapping`, {
      term: parseInt(selectedTermId),
    })
    .then((response) => {
      // handle success
      console.log(response);
      location.reload();
    });
}


/* This function accepts a term IRI pasted by a user and if it doesn't already exist, creates a new mapping suggestion
and mapping for that term */
async function existingTermButtonClicked() {
  // Check if the IRI field is empty
  termIRI = document.getElementById("existingTermIRI").value;
  if (termIRI === "") return;
  // Check if a mapping suggestion with the given IRI already exists in the suggestions
  for (const row of document.querySelectorAll(".suggestion-table__link")) {
    if (row.getAttribute('href') === termIRI) {
      UIkit.notification({
        message: "A suggestion of this term already exists",
        status: "warning",
        pos: "top-center",
        timeout: 3000,
      })
      return;
    }
  }
  /*
    Extract the ontology id from the term iri, to be used for OLS queries by reading the last part of an iri and
    reading the ontology id using the term prefix
    E.g. extract 'mondo' from http://purl.obolibrary.org/obo/MONDO_0019482
  */
  termOntologyId = termIRI.split("/").slice(-1)[0].split("_")[0].toLowerCase();
  if (termOntologyId === 'orphanet') termOntologyId = 'ordo'
  try {
    await axios.get(
      `https://www.ebi.ac.uk/ols/api/ontologies/${termOntologyId}/terms?iri=${termIRI}`
    );
    axios
      .post(`/traits/${currentTraitId}/mapping/add`, { term_iri: termIRI })
      .then((response) => {
        // handle success
        console.log(response);
        location.reload();
      });
  } catch (err) {
    UIkit.notification({
      message: "Error verifying term! Check if given IRI is valid",
      status: "danger",
      pos: "top-center",
      timeout: 3000,
    });
  }
}

/*
This module contains all the funcionality for mapping traits to ontology terms, via a trait's suggestion table
*/
let selectedRowIndex = -1;
let selectedTableId = -1;
let currentTraitId = -1;
let selectedTermId = -1;


// Setter function for current trait id
function setCurrentTraitId(traitId) {
  currentTraitId = traitId;
}


// Check if the "Newly suggested terms" table is empty, and hide it if it is.
const NewTermSuggestionTable = document.querySelector('#newSuggestionTable')
if (NewTermSuggestionTable.rows.length === 1) {
  NewTermSuggestionTable.classList.add('hidden')
  document.querySelector('#newSuggestionTable-title').classList.add('hidden')
} 
  

/*  This function takes in the clicked row of the mapping suggestion table, and the term and trait ids for its mapping
suggestion, and sets them as selected */
function selectRow(row, tableId, traitId, termId) {
  selectedTableId = tableId;
  selectedRowIndex = row.rowIndex;
  currentTraitId = traitId;
  selectedTermId = termId;

  // Remove the 'selected' class from all table rows
  for (const row of document.getElementsByTagName("tr"))
    row.classList.remove("suggestion-table__row--selected");

  // If the currently mapped row was selected, set the selected index as -1 to prevent unnecessary mapping requests
  selectedRow = document.getElementById(selectedTableId).rows[selectedRowIndex];
  if (selectedRow.classList.contains("suggestion-table__row--current") || 
      selectedRow.classList.contains("suggestion-table__row--awaiting_review")
      ) {
    selectedRowIndex = -1;
    return;
  }

  // Add the 'selected' class to the selected row
  selectedRow.classList.add("suggestion-table__row--selected");
}


// This function makes an ajax request to create a current mapping with the selected term
function mapButtonClicked() {
  if (selectedRowIndex < 1) {
    showNotification('No mapping selected', 'warning');
    return;
  }
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
  if (termIRI === "") {
    showNotification('No term IRI given', 'warning');
    return;
  }
  // Check if a mapping suggestion with the given IRI already exists in the suggestions
  for (const row of document.querySelectorAll(".suggestion-table__link")) {
    if (row.getAttribute('href') === termIRI) {
      showNotification('A suggestion of this term already exists', 'warning');
      return;
    }
  }
  /* Extract the ontology id from the term iri, to be used for OLS queries by reading the last part of an iri and
     reading the ontology id using the term prefix
     E.g. extract 'mondo' from http://purl.obolibrary.org/obo/MONDO_0019482 */
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
    showNotification('Error verifying term! Check if given IRI is valid', 'danger');
  }
}


// Show a form to create a new term suggestion, once the 'Create a new term' button is clicked
function newTermButtonClicked() {
  newTermForm = document.querySelector(".new_term");
  if (newTermForm.classList.contains("hidden")) {
    newTermForm.classList.remove("hidden");
    newTermForm.scrollIntoView();
    document.querySelector("#id_label").focus();
  } else {
    newTermForm.classList.add("hidden");
  }
}


function showNotification(message, status) {
  UIkit.notification({
    message: message,
    status: status,
    pos: "top-center",
    timeout: 3000,
  });
}


function reviewButtonClicked() {
  axios
    .post(`/traits/${currentTraitId}/mapping/review`)
    .then((response) => {
      // handle success
      console.log(response);
      location.reload();
    });
}


function commentButtonClicked() {
  commentBody = document.querySelector('#commentBody').value;
  if (commentBody.trim().length === 0) {
    showNotification("The comment form is empty", "warning")
    return;
  }
  // Empty the textarea once the comment has been submitted
  document.querySelector('#commentBody').value = "";
  axios
    .post(`/traits/${currentTraitId}/comment`, {
      comment_body: commentBody,
    })
    .then((response) => {
      // handle success
      console.log(response);
      location.reload();
    });
}

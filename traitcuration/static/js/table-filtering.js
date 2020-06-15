/*
This script contains all the filtering logic of the main traits table using list.js
*/

//Add all the possible values to filter by and enable asynchronous indexing
const options = {
  valueNames: ["name", "curie", "label", "status"],
  indexAsync: true,
};

//Initialize the table with the previously created values
const table = new List("traits-table", options);

//Function to prevent the enter key from reloading the page
var input = document.getElementById("test");
input.addEventListener("keydown", (event) => {
  if (event.keyCode === 13) {
    event.preventDefault();
  }
});

//Function to do filtering by status. Fires whenever a user clicks a status button
function filterClicked(status, activeClass) {
  const s = status.getAttribute("data-filter");
  //Get all the status buttons and remove their active class if any
  const filterButtons = document.getElementsByClassName("filter");
  for (const button of filterButtons) {
    button.classList.remove("button-outlined--primary--active");
    button.classList.remove("button-outlined--success--active");
    button.classList.remove("button-outlined--danger--active");
    button.classList.remove("button-outlined--warning--active");
  }
  //Add and active class to the clicked button
  document
    .getElementById(s)
    .classList.add(`button-outlined--${activeClass}--active`);
  //If the 'all' button is clicked, show all traits
  if (s === "all") {
    table.filter();
    return;
  }
  //Loop through all the traits and only show the ones matching the selected status
  table.filter(function (item) {
    status = item.elm.getAttribute("status");
    if (status == s) {
      return true;
    } else {
      return false;
    }
  });
}

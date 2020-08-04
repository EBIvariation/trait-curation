// This module contains utilities for date formatting and output.


const timeFormat = "MMMM Do YYYY, H:mm"; // e.g. July 29th 2020, 14:25

// Uses moment.js library to format a ISO formatted date string
function formatDate(isoformat_timestamp) {
  const momentObj = moment(isoformat_timestamp);
  return momentObj.format(timeFormat);
}


// Queries elements containing dates and appends the formatted date strings to their HTML
function outputDates() {
  const elements = document.querySelectorAll(".date");

  for (const element of elements) {
    element.innerHTML = formatDate(element.getAttribute("date"));
  }
}

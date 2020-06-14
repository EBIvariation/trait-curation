var options = {
  valueNames: ["name", "curie", "label", "status"],
};

var table = new List("traits-table", options);

function search(searchstring) {
  table.search(searchstring, ["name", "curie", "label"]);
}

function filterClicked(status, activeClass) {
  var s = status.getAttribute("data-filter");
  var filterButtons = document.getElementsByClassName("filter");
  for (var button of filterButtons) {
    button.classList.remove("button-outlined--primary--active");
    button.classList.remove("button-outlined--success--active");
    button.classList.remove("button-outlined--danger--active");
    button.classList.remove("button-outlined--warning--active");
  }
  document.getElementById(s).classList.add("active");
  if (s === "all") {
    table.filter();
    document.getElementById(s).classList.add(activeClass);
    return;
  }
  table.filter(function (item) {
    document.getElementById(s).classList.add(activeClass);
    status = item.elm.getAttribute("status");
    if (status == s) {
      return true;
    } else {
      return false;
    }
  });
}

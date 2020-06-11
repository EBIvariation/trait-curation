var options = {
  valueNames: ["name", "label", "status"],
};

var table = new List("traits-table", options);

function search(searchstring) {
  table.search(searchstring, ["name", "label"]);
}

function filterClicked(status) {
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
    document.getElementById(s).classList.add("button-outlined--primary--active");
    return;
  }
  table.filter(function (item) {
    switch (s) {
      case "current":
        document
          .getElementById(s)
          .classList.add("button-outlined--success--active");
        break;
      case "awaiting_review":
        document
          .getElementById(s)
          .classList.add("button-outlined--warning--active");
        break;
      case "unmapped":
      case "obsolete":
      case "deleted":
        document
          .getElementById(s)
          .classList.add("button-outlined--danger--active");
        break;
    }
    status = item.elm.getAttribute("status");
    if (status == s) {
      return true;
    } else {
      return false;
    }
  });
}

baseUrl = '/traits/datasources/'

let olsProgressUrl = "";
let zoomaProgressUrl = "";
let clinvarProgressUrl = "";

// Setter functions for the various task ids.
function setOlsProgressUrl(progressUrl) {
  olsProgressUrl = progressUrl
}

function setZoomaProgressUrl(progressUrl) {
  zoomaProgressUrl = progressUrl
}

function setClinvarProgressUrl(progressUrl) {
  clinvarProgressUrl = progressUrl
  console.log(clinvarProgressUrl != "None");
}

// The following code is used to initialize the progress bars in the 'Sources' page
if (olsProgressUrl != "None") {
  document.addEventListener("DOMContentLoaded", () => {
    CeleryProgressBar.initProgressBar(olsProgressUrl, {
      progressBarId: "ols-progress-bar",
      progressBarMessageId: "ols-progress-bar-message",
      onError: progressError,
      onProgress: olsImportProgress
    });
  });
}


if (zoomaProgressUrl != "None") {
  document.addEventListener("DOMContentLoaded", function () {
    CeleryProgressBar.initProgressBar(zoomaProgressUrl, {
      progressBarId: "zooma-progress-bar",
      progressBarMessageId: "zooma-progress-bar-message",
      onError: progressError,
      onProgress: zoomaImportProgress
    });
  });
}

if (clinvarProgressUrl !== "None") {
  console.log('hi')
  document.addEventListener("DOMContentLoaded", function () {
    CeleryProgressBar.initProgressBar(clinvarProgressUrl, {
      progressBarId: "clinvar-progress-bar",
      progressBarMessageId: "clinvar-progress-bar-message",
      onError: progressError,
      onProgress: traitImportProgress
    });
  });
}


// Function to make a call to the backend datasource providers
function makeDatasourceRequest(selectedDatasource) {
    axios
    .post(baseUrl, {'datasource': selectedDatasource})
    .then((response) => {
      // handle success
      console.log(response);
    });
}


// The following functions are customizing progress and error messages for the progress bars in the 'Sources' page
function progressError(progressBarElement, progressBarMessageElement, excMessage) {
  progressBarElement.style.backgroundColor = "#B22929";
  progressBarMessageElement.innerHTML = `Error: ${excMessage}`
}


function olsImportProgress (progressBarElement, progressBarMessageElement, progress){
  progressBarElement.style.backgroundColor = '#68a9ef';
  progressBarElement.style.width = progress.percent + "%";
  progressBarMessageElement.innerHTML = progress.current + ' ontology terms of ' + progress.total + ' processed...';
}


function zoomaImportProgress (progressBarElement, progressBarMessageElement, progress){
  progressBarElement.style.backgroundColor = '#68a9ef';
  progressBarElement.style.width = progress.percent + "%";
  progressBarMessageElement.innerHTML = progress.current + ' traits of ' + progress.total + ' processed...';
}

function traitImportProgress (progressBarElement, progressBarMessageElement, progress){
  progressBarElement.style.backgroundColor = '#68a9ef';
  progressBarElement.style.width = progress.percent + "%";
  progressBarMessageElement.innerHTML = progress.current + ' MB of ' + progress.total + ' MB downloaded...';
}






// Function to validate the GitHub issue submission form
async function validateAndSubmit() {
  issue_repo = document.querySelector("#id_repo");
  issue_title = document.querySelector("#id_title");
  issue_body = document.querySelector("#id_body");
  isValid = true;

  // Clear any previous errors
  errorLabels = document.querySelectorAll(".field__error");
  for (const label of errorLabels) label.innerHTML = "";

  fields = document.querySelectorAll(".field");
  for (field of fields) field.setCustomValidity("");

  // Make sure the GitHub repo provided is valid and exists
  try {
    await axios
    .get(`https://api.github.com/repos/${issue_repo.value}`, {
      headers: {
        "Content-Type": "application/json",
      },
    }) 
    }
    catch (error)  {
      if (error.response.status === 404) {
        isValid = false;
        issue_repo.setCustomValidity("This GitHub repo was not found");
        document.querySelector("#id_repo-error").innerHTML =
          "This GitHub repo was not found. Make sure the value provided is in 'owner_name/repo_name' form.";
      }
    };

  // Check if a title was given
  if (issue_title.value.length < 1) {
    isValid = false;
    document.querySelector("#id_title-error").innerHTML = "The 'title' field is required";
  }

  // Check if the issue body containts the '{spreadsheet_url}' tag, which will be replaces with the actual sheet link.
  if (!issue_body.value.includes("{speadsheet_url}")) {
    isValid = false;
    issue_body.setCustomValidity("Field must include the '{spreadsheet_url}' tag");
    document.querySelector("#id_body-error").innerHTML = "Field must include the '{spreadsheet_url}' tag";
  }

  if (isValid) {
    form = document.querySelector("#form");
    form.submit();
  }
}


// Function to poll the server for the progress of the current github submission and update the display accordingly.
function pollFeedbackTask(task_id) {
  const progressDiv = document.querySelector(".progress");;
  const progressSpinner = document.querySelector(".progress__spinner");
  const progressIcon = document.querySelector(".progress__icon");
  const progressMessage = document.querySelector(".progress__message");

  // Initialize the progress display
  progressDiv.classList.remove(
    "hidden",
    "progress--success",
    "progress--danger"
  );
  progressIcon.classList.add("hidden");
  progressSpinner.classList.remove("hidden");
  progressMessage.innerHTML = "Creating spreadsheet and GitHub issue...";

  // Query the server for the task progress every 500 ms
  const intervalId = setInterval(() => {
    axios.get(`/traits/celery-progress/${task_id}`).then((response) => {
      // If the task was successful display a success message and the GitHub issue link
      if (response.data.complete && response.data.success) 
      {
        progressDiv.classList.add("progress--success");
        progressSpinner.classList.add("hidden");
        progressIcon.classList.remove("hidden");
        progressMessage.innerHTML =
             `Feedback submitted: <a target="_blank" class="progress__link" href="${response.data.result}"> See issue </a>`;
        clearInterval(intervalId);
      } 
      // If the task was unsuccessful display an error message
      else if (response.data.complete && !response.data.success) 
      {
        progressDiv.classList.add("progress--danger");
        progressSpinner.classList.add("hidden");
        progressIcon.classList.remove("hidden");
        progressIcon.setAttribute("uk-icon", "warning");
        progressMessage.innerHTML = `Error: ${response.data.result}`;
        clearInterval(intervalId);
      }
    });
  }, 500);
}

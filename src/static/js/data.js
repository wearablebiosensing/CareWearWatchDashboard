const gWatchIDInput = document.getElementById("watchIDInput");
const gUserIDInput = document.getElementById("userIDInput");
const gTaskDropdown = document.getElementById("taskDropdownInput");
const gTestWatchButton = document.getElementById("testWatchButton");

// Controls
const STATUS_ENUM = Object.freeze({
  UNKNOWN: {
    text: "Unknown",
    color: "#a0a0a0",
  },
  RECEIVING: {
    text: "Recieving",
    color: "#4bd36b",
  },
  STOPPED: {
    text: "Stopped",
    color: "#dc2323",
  },
});
const gCurrentStatus = document.getElementById("status");
updateStatus("UNKNOWN");

// Start and Stop Button Elements
const gStartButton = document.getElementById("start");
const gStopButton = document.getElementById("stop");

/**
 * Asynchronously checks the connection status of a specified watch.
 *
 * @param {string} watchID - The ID of the watch to check.
 * @param {function} callback - A callback function that handles the connection status.
 *                              The callback takes two parameters:
 *                              1. {boolean} isWatchConnected - Whether the watch is connected.
 *                              2. {string} message - A message describing the status.
 */
async function checkWatchConnection(watchID, callback) {
  try {
    const res = await fetch(`/check_watch_connection?watchID=${watchID}`, {
      method: "POST",
      headers: {
        Accept: "application/json",
      },
    });

    const data = await res.json();
    const isWatchConnected = data["status"] == "online";
    const message = data["msg"];
    callback(isWatchConnected, message);
  } catch {
    callback(false, "Something went wrong");
  }
}

/**
 * Updates the current status display element with the specified status key.
 *
 * @param {string} key - The key representing the status to update.
 *                       This key corresponds to an entry in the STATUS_ENUM object.
 */
function updateStatus(key) {
  gCurrentStatus.innerHTML = STATUS_ENUM[key].text + ": " + (gTaskDropdown.value == "none" ? "?" : gTaskDropdown.value);
  gCurrentStatus.style.color = STATUS_ENUM[key].color;
}

/**
 * Displays a loading indicator on a button and disables it.
 *
 * @param {HTMLElement} button_element - The button element to show the loading indicator on.
 */
function startButtonLoading(button_element) {
  button_element.innerHTML = "<div class='loader-container'><div class='loader'></div></div>";
  button_element.disabled = true;
}

/**
 * Restores a button to its original state and enables it.
 *
 * @param {HTMLElement} button_element - The button element to restore.
 * @param {string} original_text - The original text to display on the button.
 */
function stopButtonLoading(button_element, original_text) {
  button_element.innerHTML = original_text;
  button_element.disabled = false;
}

function showToast(message, type) {
  let backgroundColor;
  switch (type) {
    case "success":
      backgroundColor = "linear-gradient(to right, #00b09b, #96c93d)";
      break;
    case "error":
      backgroundColor = "linear-gradient(to right, #ff5f6d, #ee6666)";
      break;
    case "info":
      backgroundColor = "linear-gradient(to right, #3498db, #2ecc71)";
      break;
    default:
      backgroundColor = "linear-gradient(to right, #bdc3c7, #2c3e50)";
  }

  Toastify({
    text: message,
    duration: 5000,
    close: true,
    gravity: "top", // `top` or `bottom`
    position: "left", // `left`, `center` or `right`
    backgroundColor: backgroundColor,
    className: "custom-toast",
    style: {
      fontSize: "1.1em",
      padding: "12px",
    },
  }).showToast();
}

// Event Listeners
gTestWatchButton.addEventListener("click", () => {
  // Ensure watchID is provided
  const watchID = gWatchIDInput.value;
  if (watchID.trim().length == 0) {
    showToast("Please Input Watch ID", "error");
    return;
  }

  // Start Loading
  startButtonLoading(gTestWatchButton);

  checkWatchConnection(watchID, (watchStatus, msg) => {
    if (watchStatus) {
      showToast(msg, "success");
    } else {
      showToast(msg, "error");
    }

    // Stop Loading
    stopButtonLoading(gTestWatchButton, "Test Watch");
  });
});

gStartButton.addEventListener("click", () => {
  // Ensure watchID is provided
  const watchID = gWatchIDInput.value;
  if (watchID.trim().length == 0) {
    showToast("Please Input Watch ID", "error");
    return;
  }

  // Ensure userID is provided
  const userID = gUserIDInput.value;
  if (userID.trim().length == 0) {
    showToast("Please Input User ID", "error");
    return;
  }

  // Ensure task is provided
  const taskValue = gTaskDropdown.value;
  if (taskValue === "none") {
    showToast("Please Select Task", "error");
    return;
  }

  // Start Loading
  startButtonLoading(gStartButton);

  checkWatchConnection(watchID, (watchStatus, msg) => {
    if (!watchStatus) {
      showToast(msg, "error");
      stopButtonLoading(gStartButton, "Start");
      return;
    }

    // Start data collection
    // Pass in data as query parameters
    fetch(`/start_data_collection?watchID=${watchID}&task=${taskValue}&userID=${userID}`, {
      method: "POST",
      headers: {
        Accept: "application/json",
      },
    })
      .then((res) => {
        return res.json();
      })
      .then((data) => {
        const isDataCollectionStarted = data["status"] == "success";
        const msg = data["msg"];
        if (isDataCollectionStarted) {
          showToast(msg, "success");
          updateStatus("RECEIVING");
        } else {
          showToast(msg, "error");
          updateStatus("UNKNOWN");
        }
      })
      .finally(() => {
        // Stop Loading
        stopButtonLoading(gStartButton, "Test Watch");
      });
  });
});

gStopButton.addEventListener("click", () => {
  // Ensure watchID is provided
  const watchID = gWatchIDInput.value;
  if (watchID.trim().length == 0) {
    showToast("Please Input Watch ID", "error");
    updateStatus("UNKNOWN");
    return;
  }

  // Start Loading
  startButtonLoading(gStopButton);

  // Start data collection
  fetch(`/stop_data_collection?watchID=${watchID}`, {
    method: "POST",
    headers: {
      Accept: "application/json",
    },
  })
    .then((res) => {
      return res.json();
    })
    .then((data) => {
      const isDataCollectionStopped = data["status"] == "success";
      const msg = data["msg"];
      if (isDataCollectionStopped) {
        showToast(msg, "success");
        updateStatus("STOPPED");
      } else {
        showToast(msg, "error");
        updateStatus("UNKNOWN");
      }
    })
    .finally(() => {
      // Stop Loading
      stopButtonLoading(gStopButton, "Stop");
    });
});

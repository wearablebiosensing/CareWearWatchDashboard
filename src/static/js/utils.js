const CAREWEAR_WATCHID_LS = "carewear_watch_id";
const CAREWEAR_USERID_LS = "carewear_user_id";
const CAREWEAR_TASK_LS = "carewear_task_id";

function getWatchID() {
  const gWatchIDInput = document.getElementById("watchIDInput");
  if (gWatchIDInput.value.trim().length == 0) {
    return null;
  }
  return gWatchIDInput.value;
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

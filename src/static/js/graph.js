var socket = io.connect("http://" + document.domain + ":" + location.port);
const maxDataPoints = 300; // Maximum data points to display on each chart

let chart = null;
let currentListener = null;
const gGraphDropdownInput = document.getElementById("graphDropdownInput");
gGraphDropdownInput.addEventListener("change", () => {
  if (chart) {
    chart.destroy();
  }
  if (currentListener) {
    socket.off(currentListener);
  }

  initializeChart(gGraphDropdownInput.value, maxDataPoints);
  startChart(gGraphDropdownInput.value);
});

function startChart() {
  const watchID = getWatchID();
  if (watchID == null) {
    showToast("Cannot show chart as WatchID is not provided ", "info");
    return;
  }

  const canvasId = document.getElementById("graphDropdownInput").value;

  currentListener = "mqtt_data_" + canvasId + "_" + watchID;
  socket.on(currentListener, function (msg) {
    var time = new Date().toLocaleTimeString();
    if (chart.data.labels.length >= maxDataPoints) {
      chart.data.labels.shift(); // Remove the oldest label
      chart.data.datasets.forEach((dataset) => {
        dataset.data.shift(); // Remove the oldest data point
      });
    }
    chart.data.labels.push(time);
    chart.data.datasets.forEach((dataset) => {
      dataset.data.push(msg.data);
    });
    chart.update();
  });
}

function setupCharts() {
  // Initialize charts for each canvas
  initializeChart("accelerometer", maxDataPoints);
}
setupCharts();

function initializeChart(canvasId, maxDataPoints) {
  var ctx = document.getElementById("chart").getContext("2d");

  chart = new Chart(ctx, {
    type: "line",

    data: {
      labels: [],
      datasets: [
        {
          label: `${canvasId}`,
          data: [],
          borderWidth: 1,
          borderColor: "#4CAF50", // Chart line color
          backgroundColor: "transparent",
        },
      ],
    },
    options: {
      scales: {
        x: {
          ticks: {
            color: "#ffffff", // Tick label color
          },
          grid: {
            drawOnChartArea: false,
          },
          display: true,
          ticks: {
            display: false,
          },
        },
        y: {
          grid: {
            color: "#37474F",
          },
          ticks: {
            color: "#ffffff",
          },
        },
      },
      legend: {
        labels: {
          fontColor: "#ffffff", // Adjust legend label color for dark theme
        },
      },
      elements: {
        line: {
          tension: 0.4,
        },
        point: {
          radius: 0,
        },
      },
    },
  });
  chart.update();

  // const watchID = getWatchID();
  // if (watchID == null) {
  //   showToast("Cannot show chart as WatchID is not provided ", "info");
  // }

  // currentListener = "mqtt_data_" + canvasId + "_" + watchID;
  // socket.on(currentListener, function (msg) {
  //   var time = new Date().toLocaleTimeString();
  //   if (chart.data.labels.length >= maxDataPoints) {
  //     chart.data.labels.shift(); // Remove the oldest label
  //     chart.data.datasets.forEach((dataset) => {
  //       dataset.data.shift(); // Remove the oldest data point
  //     });
  //   }
  //   chart.data.labels.push(time);
  //   chart.data.datasets.forEach((dataset) => {
  //     dataset.data.push(msg.data);
  //   });
  //   chart.update();
  // });
}

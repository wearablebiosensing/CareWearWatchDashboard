function openPanel() {
  if (window.innerWidth <= 800) {
    document.getElementById("myPanel").style.width = "80%";
  } else {
    document.getElementById("myPanel").style.width = "25%";
  }
}

function closePanel() {
  document.getElementById("myPanel").style.width = "0";
}

function toggleFolder(element) {
  element.classList.toggle("open");
}

window.addEventListener("resize", () => {
  if (document.getElementById("myPanel").style.width !== "0px") {
    openPanel();
  }
});

async function getFolderData(folderPath) {
  try {
    const res = await fetch(`/get_folder_data?folder_path=${folderPath}`, {
      method: "POST",
      headers: {
        Accept: "application/json",
      },
    });

    const json = await res.json();

    if (json["status"] == "failure") {
      showToast(json["msg"], "errpr");
      return [];
    }

    const folderData = json["data"];
    return folderData;
  } catch {
    showToast("Unable to get folder info", "error");
    return [];
  }
}

let fileInfoTable = {};

function updateFolderStructure() {
  const folders = ["accelerometer", "gyroscope", "linear_acceleration"];

  folders.forEach(async (folder) => {
    const folderData = await getFolderData(`data/${folder}`);
    fileInfoTable[folder] = folderData;
    folderData.forEach((fileInfo) => {
      addFileToFolder(document.getElementById(folder), fileInfo["filename"]);
    });
  });
  console.log(fileInfoTable);
}

function getFileInfoByName(filename) {
  for (const key in fileInfoTable) {
    if (fileInfoTable.hasOwnProperty(key)) {
      const array = fileInfoTable[key];
      for (const obj of array) {
        if (obj["filename"] == filename) {
          return obj;
        }
      }
    }
  }
  return null;
}

function displayFileInfo(file_element) {
  const filename = file_element.dataset.name;
  const info = getFileInfoByName(filename);

  if (info != null) {
    showToast(`# Of Lines: ${info["lines"]}\n  Timestamp: ${info["ts"]}`, "info");
  }
}

updateFolderStructure();

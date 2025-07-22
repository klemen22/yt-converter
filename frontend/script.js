const logsLink = document.getElementById("logs_link");
const statsLink = document.getElementById("stats_link");
const toastContainer = document.getElementById("toast_container");
const toastTitle = document.getElementById("toast_title");
const toastBody = document.getElementById("toast_body");
const xMark = document.getElementById("x_mark");
const formatSelect = document.getElementById("convert_format");
const resolutionSelect = document.getElementById("convert_resolution");
const results = document.getElementById("convert_result");
const submitButton = document.getElementById("submit_button");
const downloadButton = document.getElementById("download_button");
const ytURL = document.getElementById("yt_url");
const invalidLinkFeedback = document.getElementById("invalid_link");

document.addEventListener("DOMContentLoaded", () => {
  let downloadUrl = null;
  let filename = null;
  formatSelect.value = "mp3";
  resolutionSelect.hidden = true;
  invalidLinkFeedback.hidden = true;
  downloadButton.hidden = true;
  submitButton.hidden = false;
  submitButton.disabled = false;
  downloadButton.disabled = false;
  results.hidden = true;
  logsLink.disabled = false;
  toastContainer.classList.remove("slide-in");
  toastContainer.classList.remove("fade-out");

  if (ytURL.classList.contains("is-invalid")) {
    ytURL.classList.remove("is-invalid");
    invalidLinkFeedback.hidden = true;
  }

  formatSelect.addEventListener("change", () => {
    resolutionSelect.hidden = formatSelect.value !== "mp4";
  });

  logsLink.addEventListener("click", downloadLogs);
  statsLink.addEventListener("click", (e) => {
    e.preventDefault();
    showStatsToast();
  });

  xMark.addEventListener("click", hideToast);

  submitButton.addEventListener("click", async (event) => {
    event.preventDefault();
    event.stopPropagation();

    if (downloadUrl) {
      window.URL.revokeObjectURL(downloadUrl);
      downloadUrl = null;
      filename = null;
    }

    const url = ytURL.value.trim();
    const format = formatSelect.value;

    if (!url.includes("https://www.youtube.com/")) {
      ytURL.classList.add("is-invalid");
      invalidLinkFeedback.hidden = false;
      return;
    }

    ytURL.classList.remove("is-invalid");
    invalidLinkFeedback.hidden = true;
    submitButton.disabled = true;
    resolutionSelect.disabled = true;
    formatSelect.disabled = true;

    const payload = {
      url: url,
      format: format,
      resolution: null,
    };

    if (format == "mp4") {
      payload.resolution = resolutionSelect.value;
    }

    console.log(payload);
    results.hidden = false;
    results.textContent = "Converting...";

    try {
      const response = await fetch("http://localhost:8000/api/convert", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (response.ok == false) {
        results.textContent = "Error while sedning data!";
        console.log("Error while sending data!");
        return;
      }

      const data = await response.json();
      if (data.status == "success") {
        results.textContent = "Download is ready!";
        downloadButton.hidden = false;
        submitButton.hidden = true;

        downloadButton.addEventListener("click", async () => {
          const downloadLink = `http://localhost:8000/api/download/${encodeURIComponent(
            data.filename
          )}`;
          downloadButton.disabled = true;
          results.textContent = "Downloading...";

          try {
            const response = await fetch(downloadLink);
            if (response.ok == false) {
              results.textContent = "Error downloading file!";
              downloadButton.disabled = false;
              return;
            }
            const blob = await response.blob();
            const objectURL = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            // create an invisible element to signalize when the download of the file is complete
            a.href = objectURL;
            a.download = data.filename;
            a.style.display = "none";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(objectURL);

            results.textContent = "Download finished!";
            submitButton.disabled = false;
            submitButton.hidden = false;
            downloadButton.disabled = false;
            downloadButton.hidden = true;
            resolutionSelect.disabled = false;
            formatSelect.disabled = false;

            // send signal to backend to delete the file
            await fetch(
              `http://localhost:8000/api/delete/${encodeURIComponent(
                data.filename
              )}`,
              {
                method: "DELETE",
              }
            );
          } catch (error) {
            console.error("Download error: ", error);
            results.textContent = "Error while downloading the file!";
            downloadButton.disabled = false;
          }
        });
      } else {
        results.textContent = "Error: " + data.message;
      }
    } catch (error) {
      console.error("Error:", error);
      results.textContent = "Error with backend connection!";
    }
  });
});

async function downloadLogs() {
  logsLink.disabled = true;
  const resposne = await fetch("http://localhost:8000/api/logs");
  const blob = await resposne.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");

  a.href = url;
  a.download = "logs.txt";
  a.style.display = "none";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  await fetch("http://localhost:8000/api/delete/logs.txt", {
    method: "DELETE",
  });
  logsLink.disabled = false;
}

async function showStatsToast() {
  try {
    const response = await fetch("http://localhost:8000/api/stats");
    if (response.ok == false) {
      throw new Error("Error while fetching server stats!");
    }
    const stats = await response.json();
    toastTitle.textContent = "Page stats";
    toastBody.innerHTML = `
      Total conversions: ${stats.total_conversions}
      &nbsp;&nbsp;&nbsp;&nbsp;MP3: ${stats.number_of_mp3}
      &nbsp;&nbsp;&nbsp;&nbsp;MP4: ${stats.number_of_mp4}`;
    showToast();
    setTimeout(() => {
      hideToast();
    }, 5000);
  } catch (error) {
    toastTitle.textContent = "Error";
    toastBody.textContent = "Could not load stats!";
    console.error(error);
    showToast();
    setTimeout(() => {
      hideToast();
    }, 5000);
  }
}

function showToast() {
  toastContainer.hidden = false;
  toastContainer.classList.remove("fade-out");
  toastContainer.classList.add("slide-in");
}

function hideToast() {
  toastContainer.classList.remove("slide-in");
  toastContainer.classList.remove("fade-out");
  toastContainer.classList.add("fade-out");

  toastContainer.addEventListener(
    "animationend",
    () => {
      toastContainer.hidden = true;
      toastContainer.classList.remove("fade-out");
    },
    { once: true }
  );
}

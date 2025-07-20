document.addEventListener("DOMContentLoaded", () => {
  const formatSelect = document.getElementById("convert_format");
  const resolutionSelect = document.getElementById("convert_resolution");
  const results = document.getElementById("convert_result");
  const submitButton = document.getElementById("submit_button");
  const downloadButton = document.getElementById("download_button");
  const ytURL = document.getElementById("yt_url");
  const invalidLinkFeedback = document.getElementById("invalid_link");

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

  if (ytURL.classList.contains("is-invalid")) {
    ytURL.classList.remove("is-invalid");
    invalidLinkFeedback.hidden = true;
  }

  formatSelect.addEventListener("change", () => {
    resolutionSelect.hidden = formatSelect.value !== "mp4";
  });

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
          const downloadLink = `http://localhost:8000/api/download/${data.filename}`;
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
            await fetch(`http://localhost:8000/api/delete/${data.filename}`, {
              method: "DELETE",
            });
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

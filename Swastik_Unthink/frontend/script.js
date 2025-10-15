const fileInput = document.getElementById("audioFile");
const submitBtn = document.getElementById("submitBtn");
const loader = document.getElementById("loader");
const output = document.getElementById("output");
const transcriptEl = document.getElementById("transcript");
const summaryEl = document.getElementById("summary");
const dropZone = document.getElementById("drop-zone");
const uploadText = document.getElementById("uploadText");

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.style.borderColor = "#3d8bfd";
});
dropZone.addEventListener("dragleave", () => {
  dropZone.style.borderColor = "rgba(255,255,255,0.1)";
});
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  fileInput.files = e.dataTransfer.files;
  uploadText.textContent = fileInput.files[0].name;
  dropZone.style.borderColor = "rgba(255,255,255,0.1)";
});
fileInput.addEventListener("change", () => {
  uploadText.textContent = fileInput.files[0].name;
});

submitBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) return alert("Please select an audio file first.");

  loader.style.display = "block";
  output.style.display = "none";

  const formData = new FormData();
  formData.append("audio_file", file);

  try {
    const res = await fetch("http://localhost:8000/summarize", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    loader.style.display = "none";

    if (data.error) {
      alert(data.error);
      return;
    }

    transcriptEl.textContent = data.transcript;
    summaryEl.textContent = data.summary;
    output.style.display = "block";
  } catch (err) {
    loader.style.display = "none";
    alert("Error connecting to backend: " + err.message);
  }
});
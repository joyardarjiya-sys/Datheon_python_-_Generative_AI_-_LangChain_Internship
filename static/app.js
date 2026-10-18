const state = { documentType: "invoice", busy: false };

const $ = (selector) => document.querySelector(selector);
const sourceText = $("#sourceText");
const guidance = $("#guidance");
const provider = $("#provider");
const extractButton = $("#extractButton");
const charCount = $("#charCount");
const inputHint = $("#inputHint");
const emptyState = $("#emptyState");
const loadingState = $("#loadingState");
const errorState = $("#errorState");
const successState = $("#successState");
const resultStatus = $("#resultStatus");
const resultTitle = $("#resultTitle");

const labels = {
  invoice: { title: "Invoice fields", hint: "Invoice schema active · strict fields", placeholder: "Paste the raw invoice text here…\n\nTip: Include the whole document. The extractor will use null when a field is not supported by the source." },
  resume: { title: "Resume fields", hint: "Resume schema active · strict fields", placeholder: "Paste the raw resume text here…\n\nTip: Include the whole document. The extractor will use null when a field is not supported by the source." },
};

function setPipeline(step) {
  document.querySelectorAll(".pipeline-step").forEach((node, index) => node.classList.toggle("active", index === step));
}

function setStatus(kind, text) {
  resultStatus.className = `result-status ${kind}`;
  resultStatus.innerHTML = `<span class="status-dot"></span>${text}`;
}

function showOnly(element) {
  [emptyState, loadingState, errorState, successState].forEach((node) => node.classList.add("hidden"));
  element.classList.remove("hidden");
}


function setType(type) {
  // Don't switch document types while extraction is running.
  if (state.busy) return;

  // Clear the previous document text.
  sourceText.value = "";
  charCount.textContent = "0 / 12,000";

  // Update the selected document type.
  state.documentType = type;
  const copy = labels[type];

  document.querySelectorAll(".type-option").forEach((button) => {
    const selected = button.dataset.type === type;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-selected", selected ? "true" : "false");
  });

  // Update the input guidance.
  sourceText.placeholder = copy.placeholder;
  inputHint.textContent = copy.hint;

  // Reset the previous result.
  resultTitle.textContent = "Awaiting a document";
  setStatus("idle", "Not run");
  showOnly(emptyState);
  setPipeline(0);

  // Focus the empty input area.
  sourceText.focus();
}


document.querySelectorAll(".type-option").forEach((button) => button.addEventListener("click", () => setType(button.dataset.type)));
sourceText.addEventListener("input", () => { charCount.textContent = `${sourceText.value.length.toLocaleString()} / 12,000`; });
$("#retryButton").addEventListener("click", () => sourceText.focus());

function displayValue(value) {
  if (value === null || value === undefined || value === "") return "Not present in source";
  if (Array.isArray(value)) {
    if (!value.length) return "None found";
    return value.map((item) => typeof item === "object" ? Object.entries(item).map(([key, val]) => `${key.replaceAll("_", " ")}: ${displayValue(val)}`).join(" · ") : String(item)).join("\n");
  }
  if (typeof value === "object") return Object.entries(value).map(([key, val]) => `${key.replaceAll("_", " ")}: ${displayValue(val)}`).join("\n");
  return String(value);
}

function renderFields(data) {
  const fieldList = $("#fieldList");
  fieldList.replaceChildren();
  Object.entries(data).forEach(([key, value]) => {
    const item = document.createElement("div");
    item.className = `field-item${Array.isArray(value) || (value && typeof value === "object") ? " full" : ""}`;
    const name = document.createElement("span");
    name.className = "field-name";
    name.textContent = key.replaceAll("_", " ");
    const content = document.createElement("span");
    content.className = `field-value${value === null || value === "" || (Array.isArray(value) && !value.length) ? " null-value" : ""}`;
    content.style.whiteSpace = "pre-line";
    content.textContent = displayValue(value);
    item.append(name, content);
    fieldList.appendChild(item);
  });
}

function showError(message, code) {
  $("#errorTitle").textContent = code === "INPUT_REJECTED" ? "Input stopped before provider call." : "The result could not be verified.";
  $("#errorMessage").textContent = message || "Try reviewing the input and run the pipeline again.";
  resultTitle.textContent = "Verification stopped";
  setStatus("error", "Not verified");
  showOnly(errorState);
  setPipeline(0);
}

async function runExtraction() {
  if (state.busy) return;
  state.busy = true;
  extractButton.disabled = true;
  extractButton.querySelector("span:first-child").textContent = "Verifying…";
  resultTitle.textContent = "Reading the source";
  setStatus("idle", "Running");
  showOnly(loadingState);
  setPipeline(1);

  try {
    const response = await fetch("/api/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ document_type: state.documentType, provider: provider.value, text: sourceText.value, guidance: guidance.value }),
    });
    const body = await response.json();
    if (!response.ok || !body.ok || !body.verified) throw new Error(JSON.stringify(body.error || { message: "The output was not verified." }));

    renderFields(body.data);
    $("#jsonOutput").textContent = JSON.stringify(body.data, null, 2);
    $("#verificationNote").textContent = body.verification.note;
    $("#resultMeta").textContent = `${body.provider.toUpperCase()} · ${body.model}`;
    $("#requestId").textContent = `request ${body.request_id}`;
    resultTitle.textContent = labels[state.documentType].title;
    setStatus("verified", "Verified");
    showOnly(successState);
    setPipeline(2);
  } catch (error) {
    let parsed = { message: "Try reviewing the input and run the pipeline again.", code: "OUTPUT_NOT_VERIFIED" };
    try { parsed = JSON.parse(error.message); } catch (_) { /* keep safe fallback */ }
    showError(parsed.message, parsed.code);
  } finally {
    state.busy = false;
    extractButton.disabled = false;
    extractButton.querySelector("span:first-child").textContent = "Run extraction";
  }
}

extractButton.addEventListener("click", runExtraction);
sourceText.addEventListener("keydown", (event) => { if ((event.metaKey || event.ctrlKey) && event.key === "Enter") runExtraction(); });
setType("invoice");
console.log("Date and time script is running");

function updateDateTime() {
  const now = new Date();

  const dateElement = document.getElementById("current-date");
  const timeElement = document.getElementById("current-time");

  if (!dateElement || !timeElement) {
    console.error("Date/time elements not found in HTML");
    return;
  }

  dateElement.textContent = now.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    timeZone: "Asia/Kolkata"
  });

  timeElement.textContent = now.toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
    timeZone: "Asia/Kolkata"
  });
}

updateDateTime();
setInterval(updateDateTime, 1000);



const API_BASE = "http://127.0.0.1:8000/api";

const notesList = document.getElementById("notesList");
const noteForm = document.getElementById("noteForm");
const filenameInput = document.getElementById("filename");
const titleInput = document.getElementById("title");
const authorInput = document.getElementById("author");
const tagsInput = document.getElementById("tags");
const contentInput = document.getElementById("content");
const statusMessage = document.getElementById("statusMessage");
const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");
const newNoteButton = document.getElementById("newNoteButton");
const deleteButton = document.getElementById("deleteButton");
const archiveButton = document.getElementById("archiveButton");
const restoreButton = document.getElementById("restoreButton");

let currentFilename = null;



async function loadNotes() {
  const response = await fetch(`${API_BASE}/notes`);
  const notes = await response.json();

  notesList.innerHTML = "";

  for (const note of notes) {
    const li = document.createElement("li");
    li.textContent = note.title || note.filename;
    li.addEventListener("click", () => loadNote(note.filename));
    notesList.appendChild(li);
  }
}



async function loadNote(filename) {
  const response = await fetch(`${API_BASE}/notes/${encodeURIComponent(filename)}`);

  if (!response.ok) {
    showStatus("Could not load note.");
    return;
  }

  const note = await response.json();

  currentFilename = note.filename;
  filenameInput.value = note.filename;
  titleInput.value = note.title || "";
  authorInput.value = note.author || "";
  tagsInput.value = (note.tags || []).join(", ");
  contentInput.value = note.content || "";
}



async function saveNote(event) {
  event.preventDefault();

  const payload = {
    filename: filenameInput.value.trim(),
    title: titleInput.value.trim(),
    author: authorInput.value.trim(),
    content: contentInput.value,
    tags: tagsInput.value
      .split(",")
      .map(tag => tag.trim())
      .filter(tag => tag.length > 0)
  };

  let response;

  if (currentFilename && currentFilename === payload.filename) {
    response = await fetch(`${API_BASE}/notes/${encodeURIComponent(payload.filename)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: payload.content })
    });
  } else {
    response = await fetch(`${API_BASE}/notes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  }

  if (!response.ok) {
    const error = await response.json();
    showStatus(error.detail || "Save failed.");
    return;
  }

  const saved = await response.json();
  currentFilename = saved.filename;
  showStatus("Note saved.");
  await loadNotes();
}



async function deleteNote() {
  if (!currentFilename) {
    showStatus("No note selected.");
    return;
  }

  const confirmed = window.confirm(`Delete ${currentFilename}?`);
  if (!confirmed) return;

  const response = await fetch(`${API_BASE}/notes/${encodeURIComponent(currentFilename)}`, {
    method: "DELETE"
  });

  if (!response.ok) {
    showStatus("Delete failed.");
    return;
  }

  clearForm();
  showStatus("Note deleted.");
  await loadNotes();
}



async function archiveNote() {
  if (!currentFilename) {
    showStatus("No note selected.");
    return;
  }

  const response = await fetch(`${API_BASE}/notes/${encodeURIComponent(currentFilename)}/archive`, {
    method: "POST"
  });

  if (!response.ok) {
    showStatus("Archive failed.");
    return;
  }

  showStatus("Note archived.");
  await loadNotes();
}

async function restoreNote() {
  if (!currentFilename) {
    showStatus("No note selected.");
    return;
  }

  const response = await fetch(`${API_BASE}/notes/${encodeURIComponent(currentFilename)}/restore`, {
    method: "POST"
  });

  if (!response.ok) {
    showStatus("Restore failed.");
    return;
  }

  showStatus("Note restored.");
  await loadNotes();
}



async function searchNotes() {
  const query = searchInput.value.trim();

  if (!query) {
    await loadNotes();
    return;
  }

  const response = await fetch(`${API_BASE}/search/notes?q=${encodeURIComponent(query)}`);
  const results = await response.json();

  notesList.innerHTML = "";

  for (const item of results) {
    const li = document.createElement("li");
    li.textContent = item.title || item.id;
    li.addEventListener("click", () => loadNote(item.id));
    notesList.appendChild(li);
  }
}



function clearForm() {
  currentFilename = null;
  filenameInput.value = "";
  titleInput.value = "";
  authorInput.value = "";
  tagsInput.value = "";
  contentInput.value = "";
}

function showStatus(message) {
  statusMessage.textContent = message;
}



noteForm.addEventListener("submit", saveNote);
deleteButton.addEventListener("click", deleteNote);
archiveButton.addEventListener("click", archiveNote);
restoreButton.addEventListener("click", restoreNote);
searchButton.addEventListener("click", searchNotes);
newNoteButton.addEventListener("click", clearForm);

loadNotes();
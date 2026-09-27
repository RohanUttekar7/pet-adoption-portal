// Mobile menu toggle
const navToggle = document.getElementById("navToggle");
const navLinks = document.getElementById("navLinks");
if (navToggle) {
  navToggle.addEventListener("click", () => navLinks.classList.toggle("open"));
}

// Show an emoji placeholder if a pet image URL fails to load
function showPlaceholder(img) {
  const span = document.createElement("span");
  span.className = "ph";
  span.textContent = img.dataset.type || "🐾";
  img.replaceWith(span);
}
document.querySelectorAll("img[data-type]").forEach((img) => {
  img.addEventListener("error", () => showPlaceholder(img));
  if (img.complete && img.naturalWidth === 0) showPlaceholder(img);
});

// Hide flash messages after a few seconds
document.querySelectorAll(".flash").forEach((el) => {
  setTimeout(() => (el.style.display = "none"), 6000);
});

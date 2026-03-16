// Shared utilities — loaded on every page

// Highlight active nav link
document.addEventListener("DOMContentLoaded", () => {
  const links = document.querySelectorAll(".nav-links a");
  links.forEach(link => {
    if (link.getAttribute("href") === window.location.pathname) {
      link.style.color = "#a78bfa";
    }
  });
});

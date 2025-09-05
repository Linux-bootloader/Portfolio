// Copyright © 2025 Jacob Jones. All rights reserved.
// Licensed for private, personal, non-commercial use only.
// Commercial licence: https://jacobjones.gumroad.com/l/Coffee

document.addEventListener("DOMContentLoaded", function () {

  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll(".navbar a");

  navLinks.forEach(link => {
    link.classList.remove("active");

    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });
});

document.addEventListener("DOMContentLoaded", function () {

  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll(".sidebar a");

  navLinks.forEach(link => {
    link.classList.remove("active");

    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });
});

function showSidebar(){
    const sidebar = document.querySelector('.sidebar')
    sidebar.style.display = 'flex'
}
function hideSidebar(){
    const sidebar = document.querySelector('.sidebar')
    sidebar.style.display = 'none'
}
// give the class 'active' to the current nav link
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

// give the class 'active' to the current nav link for mobile nav
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
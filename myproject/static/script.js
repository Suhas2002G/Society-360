// Add active class on click
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function() {
      document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
      this.classList.add('active');
    });
  });


  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function() {
      document.querySelectorAll('.s-nav-link').forEach(link => link.classList.remove('active'));
      this.classList.add('active');
    });
  });




  document.addEventListener("DOMContentLoaded", function () {
    const navLinks = document.querySelectorAll(".admin-dash-sidebar .nav-link");
  
    navLinks.forEach(link => {
      link.addEventListener("click", function () {
        // Remove active class from all links
        navLinks.forEach(nav => nav.classList.remove("active"));
  
        // Add active class to the clicked link
        this.classList.add("active");
  
        // Store the active link in localStorage to persist across page reloads
        localStorage.setItem("activeNav", this.getAttribute("href"));
      });
    });
  
    // Apply active class based on localStorage (for page refresh)
    const currentActive = localStorage.getItem("activeNav");
    if (currentActive) {
      const activeLink = document.querySelector(`.admin-dash-sidebar .nav-link[href="${currentActive}"]`);
      if (activeLink) {
        activeLink.classList.add("active");
      }
    }
  });

  



  document.addEventListener("DOMContentLoaded", function () {
    const sNavLinks = document.querySelectorAll(".owner-sidebar .s-nav-link");
  
    sNavLinks.forEach(link => {
      link.addEventListener("click", function () {
        // Remove active class from all links
        sNavLinks.forEach(nav => nav.classList.remove("active"));
  
        // Add active class to the clicked link
        this.classList.add("active");
  
        // Optionally, store the active link in localStorage to persist across page reloads
        localStorage.setItem("activeOwnerNav", this.getAttribute("href"));
      });
    });
  
    // Apply active class based on localStorage (for page refresh)
    const currentOwnerActive = localStorage.getItem("activeOwnerNav");
    if (currentOwnerActive) {
      const activeOwnerLink = document.querySelector(`.owner-sidebar .s-nav-link[href="${currentOwnerActive}"]`);
      if (activeOwnerLink) {
        activeOwnerLink.classList.add("active");
      }
    }
  });
  
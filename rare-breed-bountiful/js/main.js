(function () {
  var toggle = document.querySelector(".menu-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  var form = document.getElementById("lead-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var company = form.querySelector("#company");
      if (company && company.value) return;
      var success = document.getElementById("form-success");
      if (success) success.style.display = "block";
      form.reset();
    });
  }

  var contactForm = document.getElementById("contact-form");
  if (contactForm) {
    contactForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var company = contactForm.querySelector("#company2");
      if (company && company.value) return;
      var success = document.getElementById("contact-success");
      if (success) success.style.display = "block";
      contactForm.reset();
    });
  }
})();

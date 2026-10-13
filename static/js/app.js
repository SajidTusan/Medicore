document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-password-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const input = document.getElementById(button.dataset.passwordToggle);
      if (!input) return;
      const showing = input.type === "password";
      input.type = showing ? "text" : "password";
      button.textContent = showing ? "Hide" : "Show";
      button.setAttribute("aria-pressed", String(showing));
    });
  });

  document.querySelectorAll("[data-username-suggestion]").forEach((button) => {
    button.addEventListener("click", () => {
      const input = document.getElementById("id_username");
      if (!input) return;
      input.value = button.dataset.usernameSuggestion;
      input.focus();
    });
  });
  const menuButton = document.querySelector(".menu-toggle");
  const backdrop = document.querySelector("[data-sidebar-close]");

  const closeMenu = () => {
    document.body.classList.remove("sidebar-open");
    menuButton?.setAttribute("aria-expanded", "false");
  };

  menuButton?.addEventListener("click", () => {
    const isOpen = document.body.classList.toggle("sidebar-open");
    menuButton.setAttribute("aria-expanded", String(isOpen));
  });
  backdrop?.addEventListener("click", closeMenu);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMenu();
  });
});

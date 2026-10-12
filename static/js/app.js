document.addEventListener("DOMContentLoaded", () => {
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

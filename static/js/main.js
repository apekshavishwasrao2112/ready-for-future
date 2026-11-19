function scrollToSection(sectionId) {

    const section = document.getElementById(sectionId);

    if (section) {
        section.scrollIntoView({
            behavior: "smooth"
        });
    }
}

const menuButton = document.querySelector("[data-menu-toggle]");
const primaryNavigation = document.getElementById("primary-navigation");

if (menuButton && primaryNavigation) {
    const closeMenu = () => {
        document.querySelector(".navbar")?.classList.remove("is-menu-open");
        menuButton.setAttribute("aria-expanded", "false");
        menuButton.setAttribute("aria-label", "Open navigation menu");
    };

    menuButton.addEventListener("click", () => {
        const isOpen = menuButton.getAttribute("aria-expanded") === "true";
        document.querySelector(".navbar")?.classList.toggle("is-menu-open", !isOpen);
        menuButton.setAttribute("aria-expanded", String(!isOpen));
        menuButton.setAttribute(
            "aria-label",
            isOpen ? "Open navigation menu" : "Close navigation menu",
        );
    });

    primaryNavigation.addEventListener("click", (event) => {
        if (event.target.closest("a")) closeMenu();
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") closeMenu();
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth > 600) closeMenu();
    });
}


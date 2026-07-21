document.addEventListener("DOMContentLoaded", () => {
    const currentTheme = localStorage.getItem("theme") || "dark";
    document.documentElement.setAttribute("data-theme", currentTheme);

    const themeToggleBtn = document.getElementById("themeToggle");
    if (themeToggleBtn) {
        updateThemeIcon(currentTheme, themeToggleBtn);
        themeToggleBtn.addEventListener("click", () => {
            const activeTheme = document.documentElement.getAttribute("data-theme");
            const newTheme = activeTheme === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", newTheme);
            localStorage.setItem("theme", newTheme);
            updateThemeIcon(newTheme, themeToggleBtn);
        });
    }

    const menuToggleBtn = document.getElementById("menuToggle");
    const sidebarElement = document.getElementById("sidebar");
    if (menuToggleBtn && sidebarElement) {
        menuToggleBtn.addEventListener("click", () => {
            sidebarElement.classList.toggle("active");
        });
    }

    highlightActiveSidebarLink();
});

function updateThemeIcon(theme, button) {
    const icon = button.querySelector("i");
    if (icon) {
        if (theme === "dark") {
            icon.className = "ri-sun-line";
        } else {
            icon.className = "ri-moon-line";
        }
    }
}

function highlightActiveSidebarLink() {
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll(".sidebar-link");
    links.forEach(link => {
        const href = link.getAttribute("href");
        if (href && (currentPath === href || (href !== "/" && currentPath.startsWith(href)))) {
            link.classList.add("active");
        } else {
            link.classList.remove("active");
        }
    });
}

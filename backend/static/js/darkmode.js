// ===============================
// Dark / Light Mode
// ===============================

const body = document.body;

const themeToggle = document.getElementById("theme-toggle");

// Load saved theme
if (localStorage.getItem("theme") === "dark") {
    body.classList.add("dark-mode");

    if (themeToggle) {
        themeToggle.innerHTML = "☀️ Light Mode";
    }
}

if (themeToggle) {

    themeToggle.addEventListener("click", function () {

        body.classList.toggle("dark-mode");

        if (body.classList.contains("dark-mode")) {

            localStorage.setItem("theme", "dark");

            themeToggle.innerHTML = "☀️ Light Mode";

        } else {

            localStorage.setItem("theme", "light");

            themeToggle.innerHTML = "🌙 Dark Mode";

        }

    });

}
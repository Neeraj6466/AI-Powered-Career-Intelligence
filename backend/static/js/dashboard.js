// =====================================
// AI Career Dashboard JavaScript
// =====================================

// ---------- Dark Mode ----------
const themeToggle = document.getElementById("theme-toggle");

themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");

    if (document.body.classList.contains("dark-mode")) {
        themeToggle.innerHTML = "☀️ Light Mode";
        localStorage.setItem("theme", "dark");
    } else {
        themeToggle.innerHTML = "🌙 Dark Mode";
        localStorage.setItem("theme", "light");
    }
});

// Load saved theme
if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark-mode");
    themeToggle.innerHTML = "☀️ Light Mode";
}

// ---------- Resume File Name ----------

const resumeInput = document.getElementById("resume");

if (resumeInput) {

    resumeInput.addEventListener("change", function () {

        const fileName = document.getElementById("fileName");

        if (this.files.length > 0) {

            fileName.innerHTML =
                "📄 " + this.files[0].name;

        }

    });

}

// ---------- Resume Analytics Chart ----------

const resumeChart = document.getElementById("resumeChart");

if (resumeChart) {

    new Chart(resumeChart, {

        type: "bar",

        data: {

            labels: [

                "Resume",

                "ATS",

                "Career",

                "Courses"

            ],

            datasets: [{

                label: "AI Analytics",

                data: [90, 85, 80, 70],

                backgroundColor: [

                    "#2563eb",

                    "#16a34a",

                    "#7c3aed",

                    "#f59e0b"

                ],

                borderRadius: 8

            }]

        },

        options: {

            responsive: true,

            plugins: {

                legend: {

                    display: false

                }

            },

            scales: {

                y: {

                    beginAtZero: true,

                    max: 100

                }

            }

        }

    });

}

// ---------- Skills Chart ----------

const skillChart = document.getElementById("skillChart");

if (skillChart) {

    new Chart(skillChart, {

        type: "doughnut",

        data: {

            labels: [

                "Skills",

                "Missing"

            ],

            datasets: [{

                data: [80, 20],

                backgroundColor: [

                    "#2563eb",

                    "#dc2626"

                ]

            }]

        },

        options: {

            responsive: true

        }

    });

}

// ---------- Animated Cards ----------

const cards = document.querySelectorAll(".card");

cards.forEach((card, index) => {

    card.style.opacity = "0";

    card.style.transform = "translateY(30px)";

    setTimeout(() => {

        card.style.transition = ".6s";

        card.style.opacity = "1";

        card.style.transform = "translateY(0)";

    }, index * 150);

});

// ---------- Welcome Message ----------

window.onload = function () {

    console.log("✅ AI Career Dashboard Loaded");

};
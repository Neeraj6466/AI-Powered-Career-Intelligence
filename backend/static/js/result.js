// ========================================
// AI Result Page JavaScript
// ========================================

document.addEventListener("DOMContentLoaded", function () {

    // ==========================
    // Dark / Light Mode
    // ==========================

    const themeBtn = document.getElementById("theme-toggle");

    if (localStorage.getItem("theme") === "dark") {

        document.body.classList.add("dark-mode");

        if (themeBtn) {
            themeBtn.innerHTML = "☀️";
        }

    }

    if (themeBtn) {

        themeBtn.addEventListener("click", function () {

            document.body.classList.toggle("dark-mode");

            if (document.body.classList.contains("dark-mode")) {

                localStorage.setItem("theme", "dark");
                themeBtn.innerHTML = "☀️";

            } else {

                localStorage.setItem("theme", "light");
                themeBtn.innerHTML = "🌙";

            }

        });

    }

    // ==========================
    // Resume Analytics Chart
    // ==========================

    const resumeChart = document.getElementById("resumeChart");

    if (resumeChart) {

        new Chart(resumeChart, {

            type: "bar",

            data: {

                labels: [

                    "Resume",

                    "Skills",

                    "Career",

                    "Courses"

                ],

                datasets: [{

                    label: "AI Analytics",

                    data: [90,80,85,70],

                    backgroundColor: [

                        "#3b82f6",

                        "#22c55e",

                        "#f59e0b",

                        "#8b5cf6"

                    ],

                    borderRadius: 10

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

                        max:100

                    }

                }

            }

        });

    }

    // ==========================
    // Skills Chart
    // ==========================

    const skillChart = document.getElementById("skillChart");

    if(skillChart){

        new Chart(skillChart,{

            type:"doughnut",

            data:{

                labels:[

                    "Skills",

                    "Missing"

                ],

                datasets:[{

                    data:[80,20],

                    backgroundColor:[

                        "#22c55e",

                        "#ef4444"

                    ]

                }]

            },

            options:{

                responsive:true

            }

        });

    }

    // ==========================
    // Card Animation
    // ==========================

    const cards=document.querySelectorAll(".ai-card,.analysis-card");

    cards.forEach((card,index)=>{

        card.style.opacity="0";

        card.style.transform="translateY(40px)";

        setTimeout(()=>{

            card.style.transition=".6s";

            card.style.opacity="1";

            card.style.transform="translateY(0px)";

        },index*150);

    });

    // ==========================
    // Welcome Message
    // ==========================

    console.log("🤖 AI Resume Analysis Loaded Successfully");

});
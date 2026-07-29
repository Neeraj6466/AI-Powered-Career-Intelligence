const editBtn = document.getElementById("editBtn");
const saveSection = document.getElementById("saveSection");

editBtn.addEventListener("click", function () {
    const inputs = document.querySelectorAll("#profileForm input, #profileForm textarea");
    
    inputs.forEach(function(input) {
        input.removeAttribute("readonly");
    });

    saveSection.style.display = "block";
    editBtn.style.display = "none";
});

// Show the selected image immediately
const profileImage = document.getElementById("profileImage");
const profilePreview = document.getElementById("profilePreview");

profileImage.addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            profilePreview.src = e.target.result;
        }
        reader.readAsDataURL(file);
    }
});

// Step 2: Dynamic Add Education functionality
const addEducation = document.getElementById("addEducation");
const educationContainer = document.getElementById("educationContainer");

addEducation.addEventListener("click", function(){
    educationContainer.insertAdjacentHTML("beforeend", `
    <div class="education-card border rounded p-3 mb-3">
        <input type="text" name="college[]" class="form-control mb-2" placeholder="College Name">
        <input type="text" name="degree[]" class="form-control mb-2" placeholder="Degree">
        <input type="text" name="branch[]" class="form-control mb-2" placeholder="Branch">
        <input type="text" name="cgpa[]" class="form-control mb-2" placeholder="CGPA">
        <input type="text" name="start_year[]" class="form-control mb-2" placeholder="Start Year">
        <input type="text" name="end_year[]" class="form-control mb-2" placeholder="End Year">
        <button type="button" class="btn btn-danger removeEducation">Remove</button>
    </div>
    `);
});

// Step 3: Add Remove button support
document.addEventListener("click", function(e){
    if(e.target.classList.contains("removeEducation")){
        e.target.parentElement.remove();
    }
});
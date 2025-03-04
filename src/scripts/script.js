document.getElementById("languages").addEventListener("change", function () {
    let selectedLanguage = this.value;
    let projects = document.getElementsByClassName("card");

    for (let project of projects) {
        let languages = project.dataset.languages.split(',');
        if (selectedLanguage === "all") {
            project.style.display = "block";
        } else if (languages.includes(selectedLanguage)) {
            project.style.display = "block";
        } else {
            project.style.display = "none";
        }
    }
});
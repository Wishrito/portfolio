document.addEventListener("DOMContentLoaded", function () {
    let languageSelect = document.getElementById("language_select");

    if (languageSelect) {
        languageSelect.addEventListener("change", function () {
            let selectedLanguage = this.value;
            let projects = document.getElementsByClassName("card");

            for (let project of projects) {
                let languages = project.dataset.languages.split(', ');
                if (selectedLanguage === "all") {
                    project.style.display = "block";
                } else if (languages.includes(selectedLanguage)) {
                    project.style.display = "block";
                } else {
                    project.style.display = "none";
                }
            }
        });
    } else {
        console.log('L\'élément language_select n\'existe pas');
    }
});

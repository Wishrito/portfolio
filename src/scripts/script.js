document.addEventListener('DOMContentLoaded', function () {
    const languageSelect = document.getElementById('language_select');
    const projectCards = document.querySelectorAll('.col-lg-4');

    if (languageSelect) {
        languageSelect.addEventListener('change', function () {
            const selectedLanguage = this.value.toLowerCase();

            projectCards.forEach(card => {
                const languages = card.dataset.languages.toLowerCase();

                if (selectedLanguage === 'all' || languages.includes(selectedLanguage)) {
                    // Afficher la carte avec une animation
                    card.style.display = 'block';
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';

                    setTimeout(() => {
                        card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 50);
                } else {
                    // Masquer la carte avec une animation
                    card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(-20px)';

                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 400);
                }
            });

            // Mettre à jour le compteur de projets visibles
            setTimeout(() => {
                const visibleProjects = document.querySelectorAll('.col-lg-4[style*="display: block"]').length;
                const projectsCount = document.querySelector('.projects-count');

                if (projectsCount) {
                    projectsCount.textContent = visibleProjects;

                    // Animation du compteur
                    projectsCount.classList.add('pulse');
                    setTimeout(() => {
                        projectsCount.classList.remove('pulse');
                    }, 500);
                }
            }, 450);
        });
    }

    // Ajouter une animation de pulsation pour le compteur
    const style = document.createElement('style');
    style.textContent = `
      @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
      }
      .pulse {
        animation: pulse 0.5s ease-in-out;
      }
    `;
    document.head.appendChild(style);
});
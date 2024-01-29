// Attendre que le DOM soit entièrement chargé
document.addEventListener('DOMContentLoaded', function () {
    // Créer un canvas
    var canvas = document.createElement('canvas');
    var context = canvas.getContext('2d');

    // Définir la taille du canvas
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Capturer l'aperçu de la page
    context.drawWindow(window, 0, 0, window.innerWidth, window.innerHeight, 'rgb(255,255,255)');

    // Convertir le canvas en une URL de données (data URL)
    var imageDataURL = canvas.toDataURL('image/png');

    // Créer la balise meta o:image
    var metaTag = document.createElement('meta');
    metaTag.setAttribute('property', 'og:image');
    metaTag.setAttribute('content', imageDataURL);

    // Insérer la balise meta dans l'en-tête de la page
    document.head.appendChild(metaTag);
});
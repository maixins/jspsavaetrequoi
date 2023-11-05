$(document).ready(function() {
    $('#confirmButton').on('click', function() {
        const inputElement = document.getElementById('inTest');
        var newValue = inputElement.value;

        // Construisez l'URL avec la query string
        var url = '/changePseudo?new=' + newValue;

        $.ajax({
            type: 'POST',  // Utilisez une requête GET
            url: url,     // Utilisez l'URL avec la query string
            success: function(response) {
                console.log('Réponse du serveur :', response);
                  if (response == '200') {
                     window.location.href = '/profil';
                  } else {
                    var modal = document.createElement('div');
                    modal.classList.add('popup');
                    modal.innerHTML = '<p>Ce pseudo est déjà utilisé.</p>';
                    var closeButton = document.createElement('button');
                    closeButton.textContent = 'Fermer';
                    closeButton.addEventListener('click', function() {
                        document.body.removeChild(modal);
                    });
                    modal.appendChild(closeButton);

                    document.body.appendChild(modal);

                  }
            },
            error: function() {
                console.log('Erreur lors de la requête.');
            }
        });
    });
});

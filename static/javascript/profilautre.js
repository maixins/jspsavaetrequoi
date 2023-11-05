$(document).ready(function() {
  function getParameterByName(name, url) {
      if (!url) url = window.location.href;
      name = name.replace(/[[\]]/g, '\\$&');
      var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
          results = regex.exec(url);
      if (!results) return null;
      if (!results[2]) return '';
      return decodeURIComponent(results[2].replace(/\+/g, ' '));
  }

  var friend = getParameterByName('targetuser');

  if (friend) {
      var requestData = {
          friend: friend
      };
  }
    $('#addFriendButton').click(function() {
        $.ajax({
            type: 'POST',
            url: '/addfriend',
            data: requestData,
            success: function(response) {
                console.log('Réponse du serveur :', response);
                window.location.reload();
            },
            error: function() {
                console.log('Erreur lors de la requête.');
            }
        });
    });
});

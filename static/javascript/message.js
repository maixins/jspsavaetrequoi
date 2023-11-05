var compteur = 0;
$(document).ready(function() {
  var socket = io.connect('https://server-web.maixins.repl.co/')

  var middleDiv = document.getElementById('middle');
  middleDiv.scrollTop = middleDiv.scrollHeight;
  socket.on('message', function(data) {

    if (document.hidden) {
      var nomPage = document.title;
      if (localStorage.getItem('compteur')) {
        compteur = parseInt(localStorage.getItem('compteur')) + 1; 
      } else {
        compteur = 1;
      }
      document.title = "Message(s) : " + compteur;
      localStorage.setItem('compteur', compteur);
    }
    var newDiv = document.createElement('div');
    newDiv.classList.add('message-container');
    var profilePicHolder = document.createElement('div');
    profilePicHolder.classList.add('profile-pic-holder');

    var profilePic = document.createElement('img');
    profilePic.classList.add('profile-pic');
    profilePic.src = data.profile_pic;

    var profileLink = document.createElement('a');
    profileLink.href = '/profil?targetuser=' + data.username;
    profileLink.appendChild(profilePic);
    profilePicHolder.appendChild(profileLink); 

    var messageContent = document.createElement('div');
    messageContent.classList.add('message-content');

    var messageParagraph = document.createElement('p');
    messageParagraph.textContent = data.username + ' : ' + data.content;  

    messageContent.appendChild(messageParagraph);

    newDiv.appendChild(profilePicHolder);
    newDiv.appendChild(messageContent);

    var middleDiv = document.getElementById('middle');
    middleDiv.appendChild(newDiv);
    middleDiv.scrollTop = middleDiv.scrollHeight;
  });

  socket.on('clear', function(data) {
    removeAllMessages();
  });

  socket.on('suppr', function(data) {
    removeLastMessage();
  });

  $('#sendBtn').on('click', function () {
    sendMessage();
  });


  $('#myInput').on('keydown', function(event) {
    if (event.key === 'Enter') {
      sendMessage();
      event.preventDefault();
    }
  });

  function sendMessage() {
    var inputVal = $('#myInput').val();
    if (inputVal !== '') {
      socket.emit("message",inputVal);
      $('#myInput').val('');
    }
  }

});

document.addEventListener("DOMContentLoaded", function() {
  var middleDiv = document.getElementById('middle');
  middleDiv.scrollTop = middleDiv.scrollHeight;
});

document.addEventListener("visibilitychange", updateTitle);
function updateTitle() {
    compteur = 0;
    document.title = "Chat";
  localStorage.setItem('compteur', compteur);
}

function removeLastMessage() {
  var middleContainer = document.getElementById("middle");
  var messageContainers = middleContainer.querySelectorAll(".message-container");

  if (messageContainers.length > 0) {
    var lastMessageContainer = messageContainers[messageContainers.length - 1];
    middleContainer.removeChild(lastMessageContainer);
  }
}

function removeAllMessages() {
  var middleContainer = document.getElementById("middle");
  middleContainer.innerHTML = "";
}
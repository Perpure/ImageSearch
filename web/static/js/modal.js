var modalWindow = document.getElementById("modal-window");

var modalImg = document.getElementById("modal-img");
var captionText = document.getElementById("caption");

var images = document.getElementsByClassName("gallery-image");

function showModalWindow(e) {
  modalWindow.style.display = "block";
  modalImg.src = e.target.src
  captionText.innerHTML = e.target.alt;
  modalWindow.addEventListener('click', closeWindow)
}

for(var i = 0; i < images.length; i++) {
  var image = images[i];
  image.addEventListener('click', showModalWindow)
}

function closeWindow(e) {
  if (e.target !== modalImg) {
    modalWindow.style.display = "none";
    modalWindow.removeEventListener('click', closeWindow)
  }
}

/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function dropDownQuantity() {
    document.getElementById("myDropdown").classList.toggle("show");
}

// Opens the link provided
function gotoURL(url) {
  window.open(url, "_self");
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
  if (!event.target.matches('.dropbtn')) {

    var dropdowns = document.getElementsByClassName("dropdown-content");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}

var numPhotos = 0
var numStories = 0
function addPhoto(event) {
    event.preventDefault()
    var photo = 'photo_';
    photo = photo.concat(String(numPhotos + 1));
    numPhotos ++;
  document.getElementById(photo).click();
}
function addStory(event) {
    event.preventDefault()
    var book = 'book_';
    book = book.concat(String(numStories + 1));
    numStories ++;
  document.getElementById(book).click();
}
var loadFile = function(event, output, output_num) {
    var output_id = output.concat(String(output_num));
    var output = document.getElementById(output_id);
    output.src = URL.createObjectURL(event.target.files[0]);
};
$(document).ready(function() {
  var middle = $('.middle');
  var container = $('html, body');
  var isScrolling = false;

  $(window).on('mousewheel', function(event) {
    if (!isScrolling) {
      if (event.originalEvent.deltaY < 0 && middle.scrollTop() > 0) {
        isScrolling = true;
        container.animate({
          scrollTop: middle.offset().top
        }, 400, function() {
          isScrolling = false;
        });
      } else if (event.originalEvent.deltaY > 0 && middle.scrollTop() < middle.prop('scrollHeight') - middle.height()) {
        isScrolling = true;
        container.animate({
          scrollTop: middle.offset().top + middle.prop('scrollHeight') - middle.height()
        }, 400, function() {
          isScrolling = false;
        });
      }
    }
  });
});

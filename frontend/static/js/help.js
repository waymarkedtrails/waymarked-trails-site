$(function() {
  $("[data-role='header'], [data-role='footer']").toolbar();
  $("[data-role='footer-controlgroup']").controlgroup();

  var lang = decodeURI(window.location.search.replace(
               new RegExp("^(?:.*[&\\?]lang(?:\\=([^&]*))?)?.*$", "i"), "$1"));
  if (lang) {
    $('.lang-link').each(function() {
      this.setAttribute('href', this.href + '?lang=' + lang);
    });
  }
});

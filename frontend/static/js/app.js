
function map_move_end(evt) {
  var view = evt.map.getView();
  if (Modernizr.localstorage) {
      localStorage.setItem('location',
                           JSON.stringify({ center: view.getCenter(),
                                            zoom: view.getZoom()}));
  }
}


$(function() {
  var init_view = { center: [950000, 6000000], zoom: 4 };
  if (Modernizr.localstorage && localStorage.getItem('location') !== null) {
    init_view = JSON.parse(localStorage.getItem('location'));
  }
  var map = new ol.Map({
    layers: [
      new ol.layer.Tile({
        source: new ol.source.OSM()
      })
    ],
    controls: ol.control.defaults({ attribution: false }),
    target: 'map',
    view: new ol.View(init_view)
  });
  map.on('moveend', map_move_end);

  $("[data-role='header'], [data-role='footer']").toolbar();
  $("[data-role='footer-controlgroup']").controlgroup();

  $(":mobile-pagecontainer").on("pagecontainershow", function(event, ui) {
    $(".ui-panel", ui.toPage).panel("open");
  });

  $("#searchform").on("submit", function(event) {
    $.mobile.navigate('#search?query=' + encodeURIComponent($("input:first").val()));
    event.preventDefault();
  });
});



function map_param(update_local_storage) {
  var view = map.getView();
  var zoom = view.getZoom()
  var center = ol.proj.transform(view.getCenter(), "EPSG:3857", "EPSG:4326");
  if (update_local_storage && Modernizr.localstorage) {
      localStorage.setItem('location',
                           JSON.stringify({ center: center, zoom: zoom}));
  }

  return "map=" + zoom + '/' +
          (Math.round(center[1] * 10000) / 10000) + '/' +
          (Math.round(center[0] * 10000) / 10000);
}

function map_move_end(evt) {
  var h = window.location.hash || '#';
  if (h.indexOf('?') < 0)
      h = h + '?' + map_param(true);
  else if (h.indexOf('map=') >= 0)
      h = h.replace(new RegExp("map=[^&]*"), map_param(true));
  else
      h = h + '&' + map_param(true);

  window.history.replaceState(window.history.state, document.title, h);
}


$(function() {
  var init_view = { center: [0, 0], zoom: 4 };
  if (Modernizr.localstorage && localStorage.getItem('location') !== null) {
    init_view = JSON.parse(localStorage.getItem('location'));
  }
  var url_view = decodeURI(window.location.hash.replace(new RegExp("^(?:.*[&\\?]map(?:\\=([^&]*))?)?.*$", "i"), "$1"));
  if (url_view) {
    var parts = url_view.split('/');
    if (parts.length === 3) {
        init_view = { zoom : parseInt(parts[0], 10),
                      center : [parseFloat(parts[2]), parseFloat(parts[1])] };
    }
  }

  map = new ol.Map({
    layers: [
      new ol.layer.Tile({
        source: new ol.source.OSM()
      })
    ],
    controls: ol.control.defaults({ attribution: false }),
    target: 'map',
    view: new ol.View({ center: ol.proj.transform(init_view.center, "EPSG:4326", "EPSG:3857"),
                        zoom: init_view.zoom })
  });
  map.on('moveend', map_move_end);

  $("[data-role='header'], [data-role='footer']").toolbar();
  $("[data-role='footer-controlgroup']").controlgroup();

  $(":mobile-pagecontainer").on("pagecontainershow", function(event, ui) {
    $(".ui-panel", ui.toPage).panel("open");
  });

  $("#api-last-update").load("/api/last-update");

  $("#searchform").on("submit", function(event) {
    $.mobile.navigate('#search?' + $(this).serialize());
    event.preventDefault();
  });

  $("#search-panel").on("open", function(event, ui) {
  });
});



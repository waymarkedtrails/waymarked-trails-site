lg = console.log;
API_URL = '/api'

Osgende = {}

Osgende.BaseMapControl = function() {
  var obj = {};

  function map_move_end(evt) {
    var view = evt.map.getView();
    var zoom = view.getZoom()
    var center = ol.proj.transform(view.getCenter(), "EPSG:3857", "EPSG:4326");
    var map_param = "map=" + zoom + '/' +
                    (Math.round(center[1] * 10000) / 10000) + '/' +
                    (Math.round(center[0] * 10000) / 10000);

    var h = window.location.hash || '#';
    if (h.indexOf('?') < 0)
        h = h + '?' + map_param;
    else if (h.indexOf('map=') >= 0)
        h = h.replace(new RegExp("map=[^&]*"), map_param);
    else
        h = h + '&' + map_param;

    window.history.replaceState(window.history.state, document.title, h);

    if (Modernizr.localstorage) {
      localStorage.setItem('location',
                           JSON.stringify({ center: center, zoom: zoom}));
    }
  }

  var init_view = { center: [0, 0], zoom: 4 };
  if (Modernizr.localstorage && localStorage.getItem('location') !== null) {
    init_view = JSON.parse(localStorage.getItem('location'));
  }

  var url_view = decodeURI(window.location.hash.replace(
               new RegExp("^(?:.*[&\\?]map(?:\\=([^&]*))?)?.*$", "i"), "$1"));
  if (url_view) {
    var parts = url_view.split('/');
    if (parts.length === 3) {
      init_view = { zoom : parseInt(parts[0], 10),
                    center : [parseFloat(parts[2]), parseFloat(parts[1])] };
    }
  }

  obj.map = new ol.Map({
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

  obj.map.on('moveend', map_move_end);

  return obj;
}

Osgende.RouteList = function(map, container) {
  var obj = {};

  $(container + " div:first-child")
    .on("panelopen", function() {
      update_list();
      map.on('moveend', update_list);
    })
    .on("panelclose", function() { map.un('moveend', update_list); });

  function update_list() {
    var extent = map.getView().calculateExtent(map.getSize());
    $.getJSON(API_URL + "/list/by-area", {bbox: extent.join()})
       .done(rebuild_list)
       .fail(function( jqxhr, textStatus, error ) {
          var err = textStatus + ", " + error;
          console.log( "Request Failed: " + err );
        });
  }

  function rebuild_list(data) {
    var obj_list = $("#routelist .ui-listview");
    obj_list.empty();
    var rels = data['relations'];
    for (var i = 0; i < rels.length; i++) {
        obj_list.append("<li>" + rels[i]['name'] + "</li>");
    }
  }

  return obj;
}


$(function() {

  $("[data-role='header'], [data-role='footer']").toolbar();
  $("[data-role='footer-controlgroup']").controlgroup();

  $(":mobile-pagecontainer").on("pagecontainershow", function(event, ui) {
    $(".ui-panel", ui.toPage).panel("open");
  });

  $("#api-last-update").load(API_URL + "/last-update");

  $("#searchform").on("submit", function(event) {
    $.mobile.navigate('#search?' + $(this).serialize());
    event.preventDefault();
  });

  $("#search-panel").on("open", function(event, ui) {
  });

  var base = Osgende.BaseMapControl();
  var routelist = Osgende.RouteList(base.map, "#routelist");

});



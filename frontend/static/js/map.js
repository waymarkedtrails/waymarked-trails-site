Osgende.Geolocator = function(map) {
  var obj = {};
  var view = map.getView();

  obj.geolocate = new ol.Geolocation({
      projection: view.getProjection(),
      trackingOptions: {
        enableHighAccuracy: true,
        maximumAge: 0,
        timeout: 7000
      }
  });

  obj.marker = new ol.Feature();
  obj.marker.setStyle(new ol.style.Style({
    image: new ol.style.Icon(({
      anchor: [0.5, 0],
      anchorXUnits: 'fraction',
      anchorYUnits: 'fraction',
      opacity: 0.75,
      src: Osgende.MEDIA_URL + '/contrib/images/marker.png'
    }))
  }));

  obj.geolocate_layer = new ol.layer.Vector({
      source: new ol.source.Vector({
        features: [obj.marker]
      })
  });

  obj.geolocate.on('change', function() {
    var coords = obj.geolocate.getPosition();
    if (coords) {
      obj.marker.setGeometry(new ol.geom.Point(coords));
      view.setCenter(coords);
      if (view.getZoom() < 9)
        view.setZoom(9);
    } else {
      obj.marker.setGeometry(null);
    }
    obj.geolocate.setTracking(false);
  });

  obj.geolocate.on('error', function() {
    // XXX show popup
    obj.geolocate.setTracking(false);
  });


  map.addLayer(obj.geolocate_layer);

  $(".btn-func-location").on("click", function(event) {
    event.preventDefault();
    obj.geolocate.setTracking(true);
  });

  return obj;
}

Osgende.BaseMapControl = function() {
  var obj = {};
  $("#javascript-warning").remove();

  function map_move_end(evt) {
    var view = evt.map.getView();
    var zoom = view.getZoom()
    var center = ol.proj.transform(view.getCenter(), "EPSG:3857", "EPSG:4326");
    var x = (Math.round(center[1] * 10000) / 10000);
    var y = (Math.round(center[0] * 10000) / 10000)
    var map_param = "map=" + zoom + '!' + x + '!' + y;

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

    map_param = "#map=" + zoom + '/' + x + '/' + y;
    $('.osm-map-link').each(function (index) {
      var href = this.href;
      var sepidx = href.indexOf('?');
      if (sepidx == -1) {
          sepidx = href.indexOf('#');
      }
      if (sepidx != -1) {
          href = href.substring(0, sepidx);
      }
      this.href = href + map_param;
    });
  }

  var init_view = { center: [8.6517, 46.6447], zoom: 11 };
  if (Modernizr.localstorage && localStorage.getItem('location') !== null) {
    init_view = JSON.parse(localStorage.getItem('location'));
  }

  var url_view = decodeURI(window.location.hash.replace(
               new RegExp("^(?:.*[&\\?]map(?:\\=([^&]*))?)?.*$", "i"), "$1"));
  if (url_view) {
    var parts = url_view.split('!');
    if (parts.length === 3) {
      init_view = { zoom : parseInt(parts[0], 10),
                    center : [parseFloat(parts[2]), parseFloat(parts[1])] };
    }
  }

  obj.base_layer = new ol.layer.Tile({ source: new ol.source.OSM() });
  obj.route_layer = new ol.layer.Tile({
                            source: new ol.source.XYZ({ url : Osgende.TILE_URL + "/{z}/{x}/{y}.png"})
                    });
  obj.vector_layer = new ol.layer.Vector({source: null, style: null});

  obj.map = new ol.Map({
    layers: [obj.base_layer, obj.route_layer, obj.vector_layer],
    controls: ol.control.defaults({ attribution: false }).extend([
              new ol.control.ScaleLine()
              ]),
    target: 'map',
    view: new ol.View({ center: ol.proj.transform(init_view.center, "EPSG:4326", "EPSG:3857"),
                        zoom: init_view.zoom,
                        maxZoom: 17
                      }),
  });

  var loc = Osgende.Geolocator(obj.map);

  obj.map.on('moveend', map_move_end);

  return obj;
}



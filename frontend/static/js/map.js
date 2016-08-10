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

Osgende.BaseMapControl = function(settings) {
  var obj = {};
  $("#javascript-warning").remove();

  function map_move_end(evt) {
    var view = evt.map.getView();
    var zoom = view.getZoom()
    console.log('Resolution: ' + view.getResolution());
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
      localStorage.setItem('position',
                           JSON.stringify({ center: center, zoom: zoom}));
    }

    $('.maplink').each(function (index) {
      var href = this.href;
      var sepidx = href.indexOf('#');
      if (sepidx == -1) {
        this.href = href + "#?" + map_param;
      } else {
        sepidx = href.indexOf('?', sepidx);
        if (sepidx != -1)
          href = href.substring(0, sepidx);
        this.href = href + "?" + map_param;
      }
    });
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

  var init_view = { center: [-7.9, 34.6], zoom: 3 };
  if (Modernizr.localstorage && localStorage.getItem('position') !== null) {
    init_view = JSON.parse(localStorage.getItem('position'));
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

  if (init_view.center[0] < -180 || init_view.center[0] > 180)
    init_view.center[0] = init_view.center[0] % 180;

  if (init_view.center[1] < -90 || init_view.center[1] > 90)
    init_view.center[1] = init_view.center[1] % 90;

  obj.base_layer = new ol.layer.Tile({ source: new ol.source.OSM(),
                                       opacity: 1.0 });
  obj.route_layer = new ol.layer.Tile({
                            source: new ol.source.XYZ({ url : Osgende.TILE_URL + "/{z}/{x}/{y}.png"}),
                            opacity: 0.8,
                            minResolution: 39 /* zoom 12 */
                    });
  obj.vroute_layer = new ol.layer.VectorTile({
                            source: new ol.source.VectorTile({
                                     format: new ol.format.GeoJSON(),
                                     tileGrid: ol.tilegrid.createXYZ({maxZoom: 22, minZoom: 12}),
                                     url: "/tiles/12/{x}/{y}.json",
                                     tileUrlFunction: function(tilecoord) {
                                       var zoomdiff = tilecoord[0] - 12;
                                       return "/tiles/12/{x}/{y}.json".
                                         replace('{x}', tilecoord[1] >> zoomdiff).
                                         replace('{y}', (-tilecoord[2] - 1) >> zoomdiff);
                                     }
                                    }),
                            style: Osgende.create_network_style(),
                            maxResolution: 39 /* zoom 12 */
  });
  obj.shade_layer = new ol.layer.Tile({
    source: new ol.source.XYZ({ url : Osgende.HILLSHADING_URL + "/{z}/{x}/{-y}.png"}),
                                opacity: 0.0,
                                visible: false,
                                opaque: true
  });
  obj.vector_layer = new ol.layer.Vector({source: null, style: null});
  obj.vector_layer_detailedroute = new ol.layer.Vector({source: null, style: null});

  obj.map = new ol.Map({
    layers: [obj.base_layer, obj.shade_layer, obj.vroute_layer, obj.route_layer, obj.vector_layer, obj.vector_layer_detailedroute],
    controls: ol.control.defaults({ attribution: false }).extend([
              new ol.control.ScaleLine()
              ]),
    interactions: ol.interaction.defaults({ pinchRotate: false, altShiftDragRotate: false }),
    target: 'map',
    view: new ol.View({ center: ol.proj.transform(init_view.center, "EPSG:4326", "EPSG:3857"),
                        zoom: init_view.zoom,
                        maxZoom: 18
                      }),
  });

  $.each(['base', 'route', 'shade'], function(i, s) {
    var lstr = s + '_layer';
    var op;
    if (Modernizr.localstorage && localStorage.getItem('opacity-' + lstr) !== null) {
      op = parseInt(localStorage.getItem('opacity-' + lstr));
      obj[lstr].setOpacity(op/100);
      obj[lstr].setVisible(op > 0);
    } else {
      op = Math.round(obj[lstr].getOpacity() * 100);
      if (Modernizr.localstorage)
        localStorage.setItem('opacity-' + lstr, op);
    }
    $("#slider-" + s)[0].setAttribute('value', op);
  });

  var shade = decodeURI(window.location.hash.replace(
                new RegExp("^(?:.*[&\\?]hill(?:\\=([^&]*))?)?.*$", "i"), "$1"));
  if (shade) {
    shade = parseFloat(shade);
    if (shade > 0 && shade <= 1) {
      obj.shade_layer.setVisible(true);
      obj.shade_layer.setOpacity(shade);
    }
  }

  var loc = Osgende.Geolocator(obj.map);

  obj.map.on('moveend', map_move_end);

  $("div:first-child", settings).on("panelbeforeopen", function() {
    $(".map-opacity-slider").on("change", function(event, ui) {
      obj[$(this).data('map-layer')].setOpacity(this.valueAsNumber/100);
      obj[$(this).data('map-layer')].setVisible(this.valueAsNumber > 0);
      if (Modernizr.localstorage)
        localStorage.setItem('opacity-' + $(this).data('map-layer'), this.value);
    });
  });

  obj.visible_bbox = function() {
    var r1 = $(".ui-subheader")[0].getBoundingClientRect();
    r1 = this.map.getCoordinateFromPixel([r1.left + 3, r1.top + 3]);
    var r2 = $(".ui-panel")[0].getBoundingClientRect();
    r2 = this.map.getCoordinateFromPixel([r2.left - 3, r2.bottom - 3]);
    return [r1[0], r1[1], r2[0], r2[1]];
  }

  return obj;
}



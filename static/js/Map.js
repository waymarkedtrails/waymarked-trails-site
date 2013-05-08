
/* our namespace */
Osgende = { };

/**
 * Class: RouteMapArgParser
 *
 * ArgParser with adapted layer parsing. It expects
 * opacity arguments instead of visibility. If no ar
 */
Osgende.RouteMapArgParser = OpenLayers.Class(OpenLayers.Control.ArgParser, {
    setMap: function(map) {
        OpenLayers.Control.prototype.setMap.apply(this, arguments);

        var args = this.getParameters();
        if (args.lat && args.lon) {
            this.center = new OpenLayers.LonLat(parseFloat(args.lon),
                                                parseFloat(args.lat));
            if (args.zoom) {
                this.zoom = parseInt(args.zoom);
            }

            // when we add a new baselayer to see when we can set the center
            this.map.events.register('changebaselayer', this,
                                     this.setCenter);
            this.setCenter();
        }

        this.opacity = { base : 1.0, hill : 0.0, route : 0.8 };
        if (Modernizr.localstorage) {
            for (var v in this.opacity) {
                if (localStorage.getItem(v + 'Opacity') !== null)
                    this.opacity[v] = parseFloat(localStorage.getItem(v + 'Opacity'));
            }
        }

        for (var v in this.opacity) {
            if (args[v]) {
                this.opacity[v] = parseFloat(args[v]);
            }
        }

        map.events.register('addlayer', this, this.setOpacity);
        for (var lid in map.layers) {
            this.setOpacity(map.layers[lid]);
        }

    },

    setOpacity : function(layer) {
        var lt = layer.layer.layerType;
        if (lt && (typeof this.opacity[lt] !== 'undefined')) {
            layer.layer.setOpacity(this.opacity[lt]);
        }
    },


    CLASS_NAME: "Osgende.RouteMapArgParser"

});

/**
 * Permalink function that produces links that fit the
 * RouteMapArgParser
 *
 * It will also add the map position parameters to any
 * element that is of class 'maplink'.
 */
Osgende.RouteMapPermalink = OpenLayers.Class(OpenLayers.Control.Permalink, {
    argParserClass : Osgende.RouteMapArgParser,

    createParams: function(center, zoom, layers) {
        center = center || this.map.getCenter();

        var params;

        // If there's still no center, map is not initialized yet.
        // Break out of this function, and simply return the params from the
        // base link.
        if (center) {
            params = {};

            //zoom
            params.zoom = zoom || this.map.getZoom();

            //lon,lat
            var lat = center.lat;
            var lon = center.lon;

            if (this.displayProjection) {
                var mapPosition = OpenLayers.Projection.transform(
                  { x: lon, y: lat },
                  this.map.getProjectionObject(),
                  this.displayProjection );
                lon = mapPosition.x;
                lat = mapPosition.y;
            }
            params.lat = Math.round(lat*100000)/100000;
            params.lon = Math.round(lon*100000)/100000;

            //layers
            layers = layers || this.map.layers;
            for (var i=0, len=layers.length; i<len; i++) {
                var layer = layers[i];

                if (layer.layerType == "base" && layer.opacity < 1.0) {
                    params.base = layer.opacity;
                } else if (layer.layerType == "route" && layer.opacity != 0.8) {
                    params.route = layer.opacity;
                } else if (layer.layerType == "hill" && layer.getVisibility()) {
                    params.hill = layer.opacity;
                }
            }

        } else {
            params = OpenLayers.Util.getParameters(this.base);
        }

        return params;
    },

    /**
     * Method: updateLink
     */
    updateLink: function() {
        var href = this.base;
        var sepidx = href.indexOf('?');
        if (sepidx != -1) {
            href = href.substring(0, sepidx);
        }
        var anchor = '';
        var anchoridx = document.URL.indexOf('#');
        if (anchoridx >= 0) {
            anchor = document.URL.substring(anchoridx);
            if (sepidx == -1) {
                href = href.substring(0, anchoridx);
            }
        }

        var params = this.createParams();
        var paramstr = '?' + OpenLayers.Util.getParameterString(params);
        if (paramstr.length > 1) {
            href += paramstr;
            this.element.href = href + anchor;
            var addlinks = $(".maplink");
            for (var i=0; i<addlinks.length; i++) {
                href = addlinks[i].href;
                sepidx = href.indexOf('?');
                if (sepidx == -1) {
                    sepidx = href.indexOf('#');
                }
                if (sepidx != -1) {
                    href = href.substring(0, sepidx);
                }
                addlinks[i].href = href + paramstr;
            }
            paramstr = '?' + OpenLayers.Util.getParameterString({
                        lat : params.lat, lon : params.lon, zoom : params.zoom});
            var addlinks = $(".simplemaplink");
            for (var i=0; i<addlinks.length; i++) {
                href = addlinks[i].href;
                sepidx = href.indexOf('?');
                if (sepidx == -1) {
                    sepidx = href.indexOf('#');
                }
                if (sepidx != -1) {
                    href = href.substring(0, sepidx);
                }
                addlinks[i].href = href + paramstr;
            }
        }
    },


    CLASS_NAME: "Osgende.RouteMapPermalink"
});

/**
 * Extend mouse position to show zoom level as well.
 */
Osgende.RouteMapMousePosition = OpenLayers.Class(OpenLayers.Control.MousePosition, {
    formatOutput: function(lonLat) {
        var digits = parseInt(this.numDigits);
        var newHtml =
            lonLat.lon.toFixed(digits) +
            this.separator +
            lonLat.lat.toFixed(digits) +
            " Zoom " +
            this.map.getZoom();
        return newHtml;
    },

    CLASS_NAME: "Osgende.RouteMapMousePosition"
});

/**
 * Geolocation functionality.
 *
 */
Osgende.Geolocator = function() {

    this.initialize = function(map) {
        this.map = map;
        this.geolocate = new OpenLayers.Control.Geolocate({
              geolocationOptions: {
                  enableHighAccuracy: true,
                  maximumAge: 0,
                  timeout: 7000
              }
        });

        this.geolocate.events.register("locationupdated", this, this.locationFound);
        this.geolocate.events.register("locationfailed", this, this.locationFailed);

        map.addControl(this.geolocate);

        this.geoLocateLayer = new OpenLayers.Layer.Vector('vector');
        map.addLayer(this.geoLocateLayer);

        this.geoLocateUser = function(shouldZoom) {
            this.doZoomAfterGeolocation = shouldZoom;
            this.geoLocateLayer.removeAllFeatures();

            this.geolocate.watch = false;
            this.geolocate.activate();
        };
    };

    this.locationFound = function(e) {
        // Add marker to show location
        var marker = new OpenLayers.Feature.Vector(
            e.point,
            {},
            {   externalGraphic: routemap_mediaurl + "/contrib/openlayers/img/marker-blue.png",
                graphicHeight: 25,
                graphicWidth: 21,
                graphicXOffset: -21/2,
                graphicYOffset: -25
             }
        );
        this.geoLocateLayer.addFeatures([
            marker
            ]);

        this.geolocate.deactivate();

        if (doZoomAfterGeolocation || this.map.getZoom() < 9) {
            this.map.zoomTo(9); // Only zoom on when opening page
            Osgende.RouteMap.updateLocation(); // Call manually since this is done before event is set up
        }
    };

    this.locationFailed = function() {
        noty({text: $('#geolocationErrorMsg').text(), timeout: 3000, type: 'error'});

        // Recreate due to bug in browser or openlayers
        this.map.removeControl(this.geolocate);
        this.geolocate = new OpenLayers.Control.Geolocate({
            geolocationOptions: {
            enableHighAccuracy: true,
            maximumAge: 0,
            timeout: 7000
        }
        });
        this.map.addControl(this.geolocate);
    };

};


/**
 * Extended Map object with our special selection of layers.
 */
Osgende.RouteMap = {

    initialize: function (div) {
        this.createMap(div);

        // Setup what we need for geolocation
        if (Modernizr.geolocation && Osgende.MapConfig.ismobile) {
            this.geolocator = new Osgende.Geolocator();
            this.geolocator.initialize(this.map);
        }

        if (window.location.href.indexOf("?") === -1)
            this.setInitialMapPosition()

        this.map.events.register("moveend", this, this.updateLocation);

        this.initSliders();
    },

    setInitialMapPosition: function() {
        if (Osgende.MapConfig.extent) {
            this.map.zoomToExtent(Osgende.MapConfig.extent);
        } else {
            var bounds = [7, 50, 4];
            if (Modernizr.localstorage) {
                if (localStorage.getItem('location') !== null) {
                    bounds = JSON.parse(localStorage.getItem('location'));
                } else {
                    // Locate before moveend event due to race condition
                    // updateLocation is manually called if location is found
                    if (this.geolocator && Osgende.MapConfig.showroute <= 0
                            && localStorage.getItem('firstVisit') !== null)
                        this.geolocator.geoLocateUser(true);
                }
            }
            this.map.setCenter([bounds[1], bounds[0]], bounds[2]);
        }
    },

    initSliders: function() {
        for (var lid in this.map.layers) {
            var layer = this.map.layers[lid];
            var layertype = layer['layerType'];
            if (layertype) {
                var slider = YAHOO.widget.Slider.getHorizSlider(
                                 layertype + "bg", layertype + "thumb", 0, 200);
                slider.map = this;
                slider.layertype = layertype;
                slider.setValue(Math.round(layer.opacity*200));
                slider.subscribe('change', function (newOffset) {
                    this.map.updateOpacity(this.layertype, this.getValue()/200);
                });
            }
        }
    },

    updateLocation: function() {
        var centre = this.map.getCenter();
        var loc = [ centre.lat, centre.lon, this.map.getZoom()];
        localStorage.setItem('location', JSON.stringify(loc));
    },

    createMap: function(div) {
        var baseLayer = new OpenLayers.Layer.OSM("baseLayer",
                           [ //"http://mull.geofabrik.de/osm2x/${z}/${x}/${y}.png"
                              "http://a.tile.openstreetmap.org/${z}/${x}/${y}.png",
                              "http://b.tile.openstreetmap.org/${z}/${x}/${y}.png",
                              "http://c.tile.openstreetmap.org/${z}/${x}/${y}.png"
                           ],
                           { numZoomLevels: 19,
                             "layerType" : "base"});

        var routeLayer = new OpenLayers.Layer.OSM("routeLayer",
                           Osgende.MapConfig.tileurl + "/${z}/${x}/${y}.png",
                           { numZoomLevels: 19,
                             isBaseLayer: false,
                             transitionEffect: "null",
                             tileOptions : {crossOriginKeyword: null},
                             "layerType": "route"
                           });


        var shadingLayer = new OpenLayers.Layer.OSM(
                            "shadingLayer",
                            "http://tile.waymarkedtrails.org/hillshading/",
                            {
                                type: 'png', alpha: true,
                                getURL: function(bounds) {
                                            var res = this.map.getResolution();
                                            var x = Math.round((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
                                            var y = Math.round((bounds.bottom - this.tileOrigin.lat) / (res * this.tileSize.h));
                                            var z = this.map.getZoom();
                                            var limit = Math.pow(2, z);
                                            if (y < 0 || y >= limit)
                                            {
                                              return null;
                                            }
                                            else
                                            {
                                              return this.url + z + "/" + x + "/" + y + ".png";
                                            }
                                },
                                buffer: 0,
                                isBaseLayer: false,
                                minScale: 3000000,
                                tileOptions : {crossOriginKeyword: null},
                                transparent: true,
                                "layerType" : "hill"
                            });

        var mapcontrols = [ new Osgende.RouteMapPermalink(),
                            new OpenLayers.Control.ScaleLine({geodesic: true})
                          ];

        if (Modernizr.touch) {
            mapcontrols = mapcontrols.concat( [
                       new OpenLayers.Control.TouchNavigation({
                                dragPanOptions: { enableKinetic: true }
                           }),
                       new OpenLayers.Control.Zoom()
                      ]);
        } else {
            mapcontrols = mapcontrols.concat(
                     [ new OpenLayers.Control.Navigation(),
                       new OpenLayers.Control.PanZoomBar({panIcons: false}),
                       new Osgende.RouteMapMousePosition(),
                       new OpenLayers.Control.KeyboardDefaults({observeElement: 'map'})]);
        }

        this.map = new OpenLayers.Map (div, {
            controls: mapcontrols,
            maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,     20037508.34,20037508.34),
            maxResolution: 156543.0399,
            numZoomLevels: 19,
            units: 'm',
            theme: null,
            projection: new OpenLayers.Projection("EPSG:900913"),
            displayProjection: new OpenLayers.Projection("EPSG:4326")
        });

        this.map.addLayers([shadingLayer, baseLayer, routeLayer]);
    },

    updateOpacity : function (layertype, newvalue) {
        for (var lid in this.map.layers) {
            var layer = this.map.layers[lid];
            if (layer['layerType'] === layertype) {
                layer.setOpacity(newvalue);
            }
        }
        if (Modernizr.localstorage)
            localStorage.setItem(layertype + 'Opacity', newvalue);
    },


    zoomToDisplayBbox : function (bbox) {
        var bnds = new OpenLayers.Bounds(bbox[2],bbox[0],bbox[3],bbox[1]);
        bnds.transform(this.displayProjection, this.projection);
        this.zoomToExtent(bnds);
    },

};


/** Initialisation of map object */
$(document).ready(function () {
    $('#map').text('');

    // Make osm link behave as a permalink. Not the best place to do it but it
    // cannot be done in the template because it's inside a translated string.
    $('a[href|="http://www.openstreetmap.org"]').addClass('simplemaplink')

    Osgende.RouteMap.initialize('map');

    //XXX this should go somewhere else
    setupRouteView(Osgende.RouteMap.map);


    if (Osgende.MapConfig.showroute <= 0 && location.hash !== "") {
        var subhash = location.hash.substr(1).split('?', 1)[0];
        if (subhash !== "") {
            WMTSidebar.show(subhash);
            reloadRoutes();
        }
    } else {
        // give focus to map so zooming works
        document.getElementById('map').focus();
    }

    $('.button-locate').click(function () {
            PSgende.RouteMap.geoLocateUser(false);
    });

    $('.button-pref').click(function () {
            WMTSidebar.show('pref');
    });

    $('#select-lang').change(function() {
            document.location.href = $('#select-lang option:selected')[0].value + '#pref';
    });

});

function toggleMapSwitch() {
    $(".mapSwitch").toggleClass('invisible');
};




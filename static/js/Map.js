/* The Map */
var map;

/* our namespace */
Osgende = {};

/**
 * Class: RouteMapArgParser
 *
 * ArgParser with adapted layer parsing. It expects
 * opacity arguments instead of visibility.
 */
Osgende.RouteMapArgParser = OpenLayers.Class(OpenLayers.Control.ArgParser, {
    setMap: function(map) {
        OpenLayers.Control.prototype.setMap.apply(this, arguments);

        var args = this.getParameters();
        // Be careful to set layer first, to not trigger unnecessary layer loads
        if (args.layers) {
            this.layers = args.layers;

            // when we add a new layer, set its visibility
            this.map.events.register('addlayer', this,
                                     this.configureLayers);
            this.configureLayers();
        }
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
        if (args.base || args.hill || args.route) {
            this.baseOpacity = args.base?parseFloat(args.base):1.0;
            this.hillOpacity = args.hill?parseFloat(args.hill):0.0;
            this.routeOpacity = args.route?parseFloat(args.route):0.8;
            this.map.events.register('addlayer', this,
                                     this.setOpacity);
            this.setOpacity();
        }
    },

    setOpacity : function() {
        if (this.map.layers.length >= 4) {
            this.map.events.unregister('addlayer', this, this.setOpacity);
            this.map.layers[0].setVisibility(this.hillOpacity > 0.0);
            this.map.layers[0].setOpacity(this.hillOpacity/2);
            this.map.layers[1].setOpacity(this.baseOpacity);
            this.map.layers[2].setOpacity(this.routeOpacity);
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
            var hill = 0.0;
            for (var i=0, len=layers.length; i<len; i++) {
                var layer = layers[i];

                if (layer.permalink == "base" && layer.opacity < 1.0) {
                    params.base = layer.opacity;
                } else if (layer.permalink == "route" && layer.opacity != 0.8) {
                    params.route = layer.opacity;
                } else if (layer.permalink == "hill" && layer.getVisibility()) {
                    hill += layer.opacity;
                }
            }
            if (hill > 0.0) {
                params.hill = 2*hill;
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
        var separator = this.anchor ? '#' : '?';
        var href = this.base;
        var sepidx = href.indexOf(separator)
        if (sepidx != -1) {
            href = href.substring(0, sepidx);
        }

        var params = this.createParams();
        var paramstr = separator + OpenLayers.Util.getParameterString(params);
        href += paramstr;
        this.element.href = href;
        var addlinks = $(".maplink");
        for (var i=0; i<addlinks.length; i++) {
            href = addlinks[i].href;
            sepidx = href.indexOf(separator);
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
            sepidx = href.indexOf(separator);
            if (sepidx != -1) {
                href = href.substring(0, sepidx);
            }
            addlinks[i].href = href + paramstr;
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
 * Setup YUI-sliders for the MapSwitch
 *
 * Sliders are used to change the opacity of the different layers.
 * They are initialized with the current opacity values
 * from the respective map layers.
 */
function initSliders(map) {
    var baseslider, routeslider, hillslider;
    baseslider = YAHOO.widget.Slider.getHorizSlider("basebg", "basethumb", 0, 200);
    baseslider.setValue(Math.round(map.layers[1].opacity*200));
    baseslider.subscribe('change', function (newOffset) {
            map.layers[1].setOpacity(baseslider.getValue()/200);
            updateLocation();
    });
    routeslider = YAHOO.widget.Slider.getHorizSlider("routebg", "routethumb", 0, 200);
    routeslider.setValue(Math.round(map.layers[2].opacity*200));
    routeslider.subscribe('change', function (newOffset) {
            map.layers[2].setOpacity(routeslider.getValue()/200);
            updateLocation();
    });
    hillslider = YAHOO.widget.Slider.getHorizSlider("hillbg", "hillthumb", 0, 200);
    var hillopacity = 0.0;
    if (map.layers[0].getVisibility()) hillopacity += map.layers[0].opacity;
    hillslider.setValue(Math.round(hillopacity*200));
    hillslider.subscribe('change', function (newOffset) {
            var hillOpacity = hillslider.getValue()/200;
            map.layers[0].setVisibility(hillOpacity > 0.0);
            map.layers[0].setOpacity(hillOpacity);
            updateLocation();
    });
}

function get_tms_url(bounds) {
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
    }

/** Initialisation of map object */
function initMap(tileurl, ismobile) {
    $('#map').text('');

    // Make osm link behave as a permalink. Not the best place to do it but it
    // cannot be done in the template because it's inside a translated string.
    $('a[href|="http://www.openstreetmap.org"]').addClass('simplemaplink')

    mapcontrols = [ new Osgende.RouteMapPermalink(),
                    new OpenLayers.Control.ScaleLine({geodesic: true})
                  ]
    if (ismobile) {
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

    map = new OpenLayers.Map ("map", {
            controls: mapcontrols,
            maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,     20037508.34,20037508.34),
            maxResolution: 156543.0399,
            numZoomLevels: 19,
            units: 'm',
            theme: null,
            projection: new OpenLayers.Projection("EPSG:900913"),
            displayProjection: new OpenLayers.Projection("EPSG:4326")
    });


    /** Original Mapnik map */
    var layerMapnik = new OpenLayers.Layer.OSM("Mapnik",
                           [ //"http://mull.geofabrik.de/osm2x/${z}/${x}/${y}.png"
                              "http://a.tile.openstreetmap.org/${z}/${x}/${y}.png",
                              "http://b.tile.openstreetmap.org/${z}/${x}/${y}.png",
                              "http://c.tile.openstreetmap.org/${z}/${x}/${y}.png"
                           ],
                           { opacity: baseopacity,
                             numZoomLevels: 19,
                             "permalink" : "base"});

    var layerHiking = new OpenLayers.Layer.OSM("Routes Map",
                           tileurl + "/${z}/${x}/${y}.png",
                           { numZoomLevels: 19,
                             isBaseLayer: false,
                             transitionEffect: "null",
                             opacity: routeopacity,
                             tileOptions : {crossOriginKeyword: null},
                             "permalink": "route"
                           });


    var hill = new OpenLayers.Layer.OSM(
        "Hillshading (SRTM3+ASTER)",
        "http://tile.waymarkedtrails.org/hillshading/",
        {
                type: 'png', alpha: true, getURL: get_tms_url,
                buffer: 0,
                isBaseLayer: false, 
                minScale: 3000000,
                             tileOptions : {crossOriginKeyword: null},
transparent: true, "visibility": (hillopacity > 0.0), "permalink" : "hill"
        }
        );
    hill.setOpacity(hillopacity/2);

    map.addLayers([hill, layerMapnik, layerHiking]);

    if (window.location.href.indexOf("?") == -1) {
        var bounds = new OpenLayers.Bounds(minlon, minlat, maxlon, maxlat);
        map.zoomToExtent(bounds);
    }
    
    // Locate before moveend event due to race condition
    // updateLocation is manually called if location is found
    if (ismobile && showroute <= 0) {
        geoLocate();
    }

    map.events.register("moveend", map, updateLocation);
    map.events.register("changelayer", map, updateLocation);

    //XXX this should go somewhere else
    setupRouteView(map);
    initSliders(map);

    if (showroute <= 0 && location.hash !== "") {
        WMTSidebar.show(location.hash.substr(1));
        reloadRoutes();
    } else {
        // give focus to map so zooming works
        document.getElementById('map').focus();
    }


}

function updateLocation() {
    var extent = map.getExtent();
    var expiry = new Date();
    var hillopacity = 0.0;
    if (map.layers[0].getVisibility()) hillopacity += map.layers[0].opacity;

    expiry.setYear(expiry.getFullYear() + 10);
    document.cookie = "_routemap_location=" + extent.left + "|" + extent.bottom + "|" + extent.right + "|" + extent.top + "|" + map.layers[2].opacity + "|" + map.layers[3].opacity + "|" + 2*hillopacity + "; expires=" + expiry.toGMTString() + ";path=/";
}

function toggleMapSwitch() {
    $(".mapSwitch").toggleClass('invisible');
}

function zoomMap(bbox) {
    var bnds = new OpenLayers.Bounds(bbox[2],bbox[0],bbox[3],bbox[1]);
    bnds.transform(
                  map.displayProjection,
                  map.getProjectionObject());
    map.zoomToExtent(bnds);
    
}

var locatedOnce = false; 
function geoLocate() {
    var geolocate = new OpenLayers.Control.Geolocate({
        geolocationOptions: {
            enableHighAccuracy: true,
            maximumAge: 0,
            timeout: 7000
        }
    });
    
    map.addControl(geolocate);
    geolocate.events.register("locationupdated",this,function(e) {
    	geolocate.deactivate();
        if(!locatedOnce) { 
            map.zoomTo(15); // Only zoom on when opening page
            updateLocation(); // Call manually since this is done before event is set up
        }
        locatedOnce = true;
    });
    geolocate.events.register("locationfailed",this,function() {
        // do nothing
    });
    geolocate.watch = false;
    geolocate.activate();
    
}

$('.button-locate').click(function () {
        geoLocate();
});

$('.button-pref').click(function () {
        WMTSidebar.show('pref');
});

$('#select-lang').change(function() {
        document.location.href = $('#select-lang option:selected')[0].value + '#pref';
});

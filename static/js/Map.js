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
            this.map.layers[1].setVisibility(this.hillOpacity > 1.0);
            if (this.hillOpacity < 1.0) {
                this.map.layers[0].setOpacity(this.hillOpacity);
            } else {
                this.map.layers[0].setOpacity(1.0);
                this.map.layers[1].setOpacity(this.hillOpacity - 1.0);
            }
            this.map.layers[2].setOpacity(this.baseOpacity);
            this.map.layers[3].setOpacity(this.routeOpacity);
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
                params.hill = hill;
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

        var params = separator + OpenLayers.Util.getParameterString(this.createParams());
        href += params;
        this.element.href = href;
        var addlinks = $(".maplink");
        for (var i=0; i<addlinks.length; i++) {
            href = addlinks[i].href;
            sepidx = href.indexOf(separator);
            if (sepidx != -1) {
                href = href.substring(0, sepidx);
            }
            addlinks[i].href = href + params;
        }
    },


    CLASS_NAME: "Osgende.RouteMapPermalink"
});

/*
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
 * Function: onImageLoadError
 */
OpenLayers.Util.onImageLoadError = function() {
  this.src = routemap_mediaurl + "/img/empty.png";
};



/* initialisation of map object */
function initMap(tileurl, ismobile) {
    $('#map').text('');

    mapcontrols = [ new Osgende.RouteMapPermalink(),
                    new OpenLayers.Control.ScaleLine({geodesic: true})
                  ]
    if (ismobile) {
        mapcontrols = mapcontrols.concat( [
                       new OpenLayers.Control.TouchNavigation({
                                dragPanOptions: { enableKinetic: true }
                           }),
                       new OpenLayers.Control.ZoomPanel()
                      ]);
    } else {
        mapcontrols = mapcontrols.concat(
                     [ new OpenLayers.Control.Navigation(),
                       new OpenLayers.Control.PanZoomBar({panIcons: false}),
                       new Osgende.RouteMapMousePosition(),
                       new OpenLayers.Control.KeyboardDefaults()]);
    }

    map = new OpenLayers.Map ("map", {
            controls: mapcontrols,
            maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,     20037508.34,20037508.34),
            maxResolution: 156543.0399,
            numZoomLevels: 19,
            units: 'm',
            projection: new OpenLayers.Projection("EPSG:900913"),
            displayProjection: new OpenLayers.Projection("EPSG:4326")
    });


    /** Original Mapnik map */
    var layerMapnik = new OpenLayers.Layer.OSM("Mapnik",
                           [  "http://a.tile.openstreetmap.org/${z}/${x}/${y}.png",
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
                             "permalink": "route"
                           });


    var hill = new OpenLayers.Layer.OSM(
        "Hillshading (NASA SRTM3 v2)",
        "http://toolserver.org/~cmarqu/hill/${z}/${x}/${y}.png",
        {  displayOutsideMaxExtent: true, isBaseLayer: false,
transparent: true, "visibility": (hillopacity > 0.0), "permalink" : "hill"
        }
        );
    if (hillopacity > 0.0) {
        if (hillopacity > 1.0)
           hill.setOpacity(1.0);
        else
           hill.setOpacity(hillopacity);
    }

    var hill2 = new OpenLayers.Layer.OSM(
        "Hillshading (exaggerate)",
        "http://toolserver.org/~cmarqu/hill/${z}/${x}/${y}.png",
        { displayOutsideMaxExtent: true, isBaseLayer: false,
transparent: true, "visibility": (hillopacity > 1.0), "permalink" : "hill"
        }
        );
    if (hillopacity > 1.0)
        hill2.setOpacity(hillopacity - 1.0);


    map.addLayers([hill, hill2, layerMapnik, layerHiking]);

    if (window.location.href.indexOf("?") == -1) {
        var bounds = new OpenLayers.Bounds(minlon, minlat, maxlon, maxlat);
        map.zoomToExtent(bounds);
    }

    map.events.register("moveend", map, updateLocation);
    map.events.register("changelayer", map, updateLocation);

    //XXX this should go somewhere else
    setupRouteView(map);
}

function updateLocation() {
    var extent = map.getExtent();
    var expiry = new Date();
    var hillopacity = 0.0;
    if (map.layers[0].getVisibility()) hillopacity += map.layers[0].opacity;
    if (map.layers[1].getVisibility()) hillopacity += map.layers[1].opacity;

    expiry.setYear(expiry.getFullYear() + 10);
    document.cookie = "_routemap_location=" + extent.left + "|" + extent.bottom + "|" + extent.right + "|" + extent.top + "|" + map.layers[2].opacity + "|" + map.layers[3].opacity + "|" + hillopacity + "; expires=" + expiry.toGMTString() + ";path=/";
}

function toggleMapSwitch() {
    $(".mapSwitch").toggleClass('invisible');
    baseslider.setValue(Math.round(map.layers[2].opacity*200));
    routeslider.setValue(Math.round(map.layers[3].opacity*200));
    var hill = 0.0;
    if (map.layers[0].getVisibility()) hill += map.layers[0].opacity;
    if (map.layers[1].getVisibility()) hill += map.layers[1].opacity;
    hillslider.setValue(Math.round(hill*100));
}

function zoomMap(bbox) {
    var bnds = new OpenLayers.Bounds(bbox[2],bbox[0],bbox[3],bbox[1]);
    bnds.transform(
                  map.displayProjection,
                  map.getProjectionObject());
    map.zoomToExtent(bnds);
    
}

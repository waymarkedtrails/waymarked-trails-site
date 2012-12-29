/*
# This file is part of the Waymarked Trails Map Project
# Copyright (C) 2011-2012 Sarah Hoffmann
#
# This is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# Functions for route sidebar.
*/


function setupRouteView(m) {
    m.events.register('moveend', map, reloadRoutes);
    var myStyles = new OpenLayers.StyleMap({
        "default": new OpenLayers.Style({
            display: "none"
        }),
        "visible": new OpenLayers.Style({
            strokeColor: "#d3ff05",
            strokeWidth: 10,
            strokeOpacity : 0.6,
            graphicZIndex: 1,
            display: true
        }),
        "single": new OpenLayers.Style({
           strokeColor: "#d3ff05",
            strokeWidth: 10,
            strokeOpacity : 0.6,
            graphicZIndex: 1
        })

    });  

    routeLayer = new OpenLayers.Layer.Vector("Route",
                                  { styleMap : myStyles });
    m.addLayer(routeLayer);
    if (showroute >= 0) {
        $('#sidebar').removeClass('invisible');
        showRouteInfo(showroute, loadRoutes);
    } 
    
}


var routeviewcounter = 0;
function loadRoutes() {
    var bounds = map.getExtent();
    bounds.transform(map.projection, map.displayProjection);
    var bbox = bounds.toBBOX();
    $("#sb-routes .route-content").addClass("invisible");
    $('#routeloader').removeClass('invisible');
    routeviewcounter++;
    var sid = routeviewcounter;
    $.get(routeinfo_baseurl +'?bbox=' + bounds.toBBOX(),
            function (data) {
                if (routeviewcounter == sid) {
                    $('#routeloader').addClass('invisible');
                    var div = jQuery("<div>").append(data);
                    $('#sbtitle').html(div.find('.route-list-header').html());
                    $('#routecontent').html(div.find('.route-list-content'));
                    $('#routecontent').removeClass("invisible");
                    var link = div.find('.routelink').attr('href');
                    var styleloader = new OpenLayers.Protocol.HTTP({
                            url: link,
                            format: new OpenLayers.Format.GeoJSON(),
                            callback: function (response) {
                                        if (routeviewcounter == sid) {
                                            routeLayer.style = null;
                                            routeLayer.addFeatures(response.features);
                                        }
                                      }
                        });
                    styleloader.read();
                }
            }
          );
    routeLayer.removeAllFeatures();
  
}


function reloadRoutes(map, mapele) {
    if (! $('#routecontent').hasClass('invisible') && ! $('.sidebar').hasClass('invisible'))
        loadRoutes();
}

function showRouteInfo(osmid, backfunc) {
    $("#sidebar-header .ui-btn").removeClass("invisible");
    $('#routeloader').removeClass('invisible');
    $('#sb-routes .route-content').addClass('invisible');
    $('#sbback').click(backfunc);
    routeviewcounter++;
    var sid = routeviewcounter;
    $.get(routeinfo_baseurl + osmid + '/info',
        function (data) {
            if (routeviewcounter == sid) {
                $('#routeloader').addClass('invisible');
                var div = jQuery("<div>").append(data);
                $('#sbtitle').html(div.find('.route-info-header').html());
                $('#routeinfocontent').html(div.find('.route-info-content'));
                $('#routeinfocontent').removeClass("invisible");
                // Only if elevation profile is turned on
                if(typeof createElevationProfile === 'function')
                    createElevationProfile(osmid); 
                routeLayer.removeAllFeatures();
                var styleloader = new OpenLayers.Protocol.HTTP({
                        url: routeinfo_baseurl + osmid + '/json',
                        format: new OpenLayers.Format.GeoJSON(),
                        callback: function (response) {
                            routeLayer.style = routeLayer.styleMap.styles.single.defaultStyle;
                            routeLayer.addFeatures(response.features);
                          },
                        scope: this
                        });
                styleloader.read();
            }
        });
}

function toggleSmallRouteView() {
    $("#sbsmall .ui-icon").toggleClass('ui-icon-arrow-d ui-icon-arrow-u');
    $("#sidebar").toggleClass("minimized");
    $("#sbback").toggleClass('invisible');
    // XXX TODO switch content of #route-info-title and #sbtitle
}



function highlightRoute(osmid) {
    for(var i=0, len=routeLayer.features.length; i<len; i++) {
        if (routeLayer.features[i].attributes.id == osmid) {
            routeLayer.features[i].renderIntent = 'visible';
            routeLayer.drawFeature(routeLayer.features[i]);
            break;
        }
    }
    routeLayer.redraw();
}

function unhighlightRoute(osmid) {
    for(var i=0, len=routeLayer.features.length; i<len; i++) {
        if (routeLayer.features[i].attributes.id == osmid) {
            routeLayer.features[i].renderIntent = 'default';
            routeLayer.drawFeature(routeLayer.features[i]);
            break;
        }
    }
}



$('#tb-routes').click(function() {
    WMTSidebar.show('routes');
    loadRoutes();
});

$('#sbsmall').click(toggleSmallRouteView);

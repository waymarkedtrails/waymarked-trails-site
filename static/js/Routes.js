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

/* Layer showing position on hover on elevation profile */
var showProfilePositionLayer;

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
        $('.sidebar').removeClass('invisible');
        showRouteInfo(showroute);
    }
    
    showProfilePositionLayer = new OpenLayers.Layer.Vector("ShowPositionInGraph", {
            style: {pointRadius: 5, 
                    fillColor: "blue",
                    strokeColor: "black",
                    strokeWidth: 1,
                    graphicZIndex: 2}
    });

    map.addLayer(showProfilePositionLayer);
    
}

function openRouteView() {
    $('.sbcontent').addClass('invisible');
    $('#routeview').removeClass('invisible');
    $('.sidebarsel').addClass('invisible');
    $('.sidebar').removeClass('invisible');
    loadRoutes();
}

var routeviewcounter = 0;
function loadRoutes() {
    var bounds = map.getExtent();
    bounds.transform(map.projection, map.displayProjection);
    var bbox = bounds.toBBOX();
    $('#routeloader').removeClass('invisible');
    $('#routecontent').html('');
    routeviewcounter++;
    var sid = routeviewcounter;
    $.get(routeinfo_baseurl +'?bbox=' + bounds.toBBOX(),
            function (data) {
                if (routeviewcounter == sid) {
                    $('#routeloader').addClass('invisible');
                    var div = jQuery("<div>").append(data);
                    $('#routecontent').html(div.find('.mainpage'));
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
    if (! $('#routeview').hasClass('invisible') && ! $('.sidebar').hasClass('invisible'))
        loadRoutes();
}

function showRouteInfo(osmid) {
    $('#routeinfoloader').removeClass('invisible');
    $('#routeinfocontent').html('');
    $('#routeinfo .backlink').addClass('invisible');
    $('#routebacklink').removeClass('invisible');
    $('.sbcontent').addClass('invisible');
    $('#routeinfo').removeClass('invisible');
    $('#routeinfocontent').load(routeinfo_baseurl + osmid + 
                              '/info .routewin',
                              function () { 
                                $('#routeinfoloader').addClass('invisible');
                                createElevationProfile(osmid); 
                              });
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

function updatePointInMap(geoJson, pos, plot) {    
    var pointFeature;
    
    showProfilePositionLayer.removeAllFeatures();
    
    var axes = plot.getAxes();
    if (pos.x < axes.xaxis.min || pos.x > axes.xaxis.max ||
        pos.y < axes.yaxis.min || pos.y > axes.yaxis.max)
        return;

    var i, j, dataset = plot.getData();
    for (i = 0; i < dataset.length; ++i) {
        var series = dataset[i];

        // find the nearest points, x-wise
        for (j = 0; j < series.data.length; ++j)
            if (series.data[j][0] > pos.x) 
                break;
        
        // now interpolate
        var y, p1 = series.data[j - 1], p2 = series.data[j];
        if (p1 == null)
            y = p2[1];
        else if (p2 == null)
            y = p1[1];
        else
            y = p1[1] + (p2[1] - p1[1]) * (pos.x - p1[0]) / (p2[0] - p1[0]);
    }
        
    pointFeature = new OpenLayers.Feature.Vector(
        new OpenLayers.Geometry.Point(geoJson[j].geometry.coordinates[0], geoJson[j].geometry.coordinates[1])
    );
    showProfilePositionLayer.addFeatures(pointFeature);
}

function createElevationProfile(osmid) {
    
   
    // Make sure jQuery is loaded
    $(function () {

        $('#elevationProfile').hide();
        $('#elevationProfileErrorText').hide();    
        $('#elevationProfileLoader').show();
    
        var geoJson;
        var plot;

        var graphData = new Array();
        var url = routeinfo_baseurl + osmid  + "/profile/json";
		
		// Get the elevation data
		$.ajax({
          url: url,
          dataType: 'json',
          error: function() {
                $('#elevationProfile').hide();
                $('#elevationProfileLoader').hide();
                $('#elevationProfileErrorText').show();
          },
          success: function(data) {
                geoJson = data.features;
		        // Go through each point
			    $.each(data.features, function(index, value) { 
				    tmp = [value.properties.distance, value.properties.elev];
				    graphData.push(tmp);
			    });
			
			    // Create ticks 
			    var routeLength = data.features[data.features.length-1].properties.distance;
			    var graphStep;
			    if(routeLength<2001)
                    graphStep = 0.5;
                else if(routeLength > 2000 && routeLength<=4000)
                    graphStep = 1;
                else if(routeLength > 4000 && routeLength<6000)
                    graphStep = 2;
                else
                    graphStep = 4;
                steps = 0
                locSteps = 0
                var xTicks = new Array();
                while(locSteps<routeLength) {
                    steps = steps + graphStep;
                    locSteps = locSteps + graphStep*1000;
                    xTicks.push([locSteps, steps + ' km']);
                }
                
                $('#elevationProfileLoader').hide();
	            $("#elevationProfile").show();
                
		        // Add plot to DOM
			    plot = $.plot($("#elevationProfile"),
	                   [ { data: graphData, color: 'blue'}], {
	                   xaxes: [{axisLabel: $("#elevProfileXlabel").text()}],
	                   yaxes: [{axisLabel: $("#elevProfileYlabel").text()}],
	               	   xaxis: {
		               	   show: true,
		               	   ticks: xTicks
		               },
	                   series: {
	                       lines: { show: true },
	                       points: { show: false }
	                   },
	                   crosshair: { mode: "x" },
                       grid: { hoverable: true, autoHighlight: false },
	             });
	             
	             
	             $("#elevationProfile").bind("plothover",  function (event, pos, item) {
                    updatePointInMap(geoJson, pos, plot);
                 });
          }
        });
    });
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



// general close methd for sidebar
// XXX should that be here?

function closeSidebar() {
    routeLayer.removeAllFeatures();
    $('.sidebar').addClass('invisible');
    $('.sidebarsel').removeClass('invisible');
}

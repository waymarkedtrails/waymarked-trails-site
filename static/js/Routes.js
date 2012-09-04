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
        $('.sidebar').removeClass('invisible');
        showRouteInfo(showroute);
    }
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
                              function () { $('#routeinfoloader').addClass('invisible'); }
                              );
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
  
  createElevationProfile(osmid);

}


function createElevationProfile(osmid) {
    
    // Make sure jQuery is loaded
    $(function () {
        var plot;
        var graphData = new Array();
        var url = routeinfo_baseurl + osmid  + "/profile/json";
		
		// Get the elevation data
		$.getJSON(url, function(data) {
		
		    // Go through each point
			$.each(data.features, function(index, value) { 
				//console.log(value.properties.elev);
				//console.log(value.properties.distance);
				
				tmp = [value.properties.distance, value.properties.elev];
				graphData.push(tmp);
				
			});
			
			// Create ticks 
			var routeLength = data.features[data.features.length-1].properties.distance;
			var graphStep;
			if(routeLength<2001)
                graphStep = 0.5;
            else if(routeLength > 2000 && routeLength<4000)
                graphStep = 1;
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
            
		    // Add plot to DOM
			var plot = $.plot($("#elevationProfile"),
	           [ { data: graphData}], {
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
	               grid: { hoverable: true,  clickable: false, backgroundColor: 'white' }
	             });
	
			});
			
			var updateLegendTimeout = null;
            var latestPosition = null;
            
            function updateLegend() {
                updateLegendTimeout = null;
                
                var pos = latestPosition;
                
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

                    //legends.eq(i).text(series.label.replace(/=.*/, "= " + y.toFixed(2)));
                    console.log("Y er: " + y)
                }
            }
            
            $("#elevationProfile").bind("plothover",  function (event, pos, item) {
                latestPosition = pos;
                console.log("Hover");
                if (!updateLegendTimeout)
                    updateLegendTimeout = setTimeout(updateLegend, 50);
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

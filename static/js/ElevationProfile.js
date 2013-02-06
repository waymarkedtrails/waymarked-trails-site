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

var routegraphcounter = 0;
function createElevationProfile(osmid) {

    showProfilePositionLayer = new OpenLayers.Layer.Vector("ShowPositionInGraph", {
            style: {pointRadius: 5, 
                    fillColor: "blue",
                    strokeColor: "black",
                    strokeWidth: 1,
                    graphicZIndex: 2}
    });

    map.addLayer(showProfilePositionLayer);
    
   
    // Make sure jQuery is loaded
    $(function () {
    
        routegraphcounter++;
        var sid = routegraphcounter;

        $('#elevationProfile').hide();
		$('#elevationProfileMetadata').hide();
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
				$('#elevationProfileMetadata').hide();
                $('#elevationProfileLoader').hide();
                $('#elevationProfileErrorText').show();
          },
          success: function(data) {

                $('#elevationprofile-header').removeClass('section-hidden');

			    //Update height meters in info.html
                if(data.properties.accumulatedAscent>0)
			        $('#accumulatedAscent').text(data.properties.accumulatedAscent);
                if(data.properties.accumulatedDescent>0)
			        $('#accumulatedDescent').text(data.properties.accumulatedDescent);

                geoJson = data.features;
                // Go through each point
                $.each(data.features, function(index, value) { 
                    elev = value.properties.elev;
                    // Check for nodata. The graph does not draw null values
                    if(elev < 0) { 
                        elev = null;
                    }
                    tmp = [value.properties.distance, elev];
                    if (routegraphcounter == sid) {
                        graphData.push(tmp);
                    }
                });

                /*
                 Create ticks according to length of route.
                  - routeLenght defines length of route in meter  
                  - graphStep defines how often x-ticks is set on the graph.
                    If graphStep=2, there is 2km between each x-tick on the graph. 
                  Just change the if/else if you want different x-ticks
                */   
                var routeLength = data.features[data.features.length-1].properties.distance;
                var graphStep;
                if(routeLength<2001)
                    graphStep = 0.5;
                else if(routeLength > 2000 && routeLength<=4000)
                    graphStep = 1;
                else if(routeLength > 4000 && routeLength<=6000)
                    graphStep = 2;
                else if(routeLength > 6000 && routeLength<=20000)
                    graphStep = 4;
                else if(routeLength > 20000 && routeLength<=100000)
                    graphStep = 10;
                else if(routeLength > 100000 && routeLength<=150000)
                    graphStep = 20;
                else
                    graphStep = 40;
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
				$('#elevationProfileMetadata').show();
                
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
                       grid: { hoverable: true, autoHighlight: false }
	             });
	             
	             
	             $("#elevationProfile").bind("plothover",  function (event, pos, item) {
                    updatePointInMap(geoJson, pos, plot);
                 });
          }
        });
    });
}

/*
** Show point in map when user hovers elevation profile
*/
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




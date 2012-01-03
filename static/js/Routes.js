/*
# This file is part of Lonvia's Hiking Map
# Copyright (C) 2011 Sarah Hoffmann
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

// if true, routes will be reloaded on map move
var doRouteReload = 0;

function setupRouteView(m) {
    m.events.register('moveend', map, reloadRoutes);
    var myStyles = new OpenLayers.StyleMap({
        "default": new OpenLayers.Style({
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
        $("#routeview").toggleClass('opensidebar closedsidebar');
        showRouteInfo(showroute);
    }
}

function openRouteView() {
    doRouteReload = 1;
    $('.sbcontent').addClass('invisible');
    $('#routeview').removeClass('invisible');
    $('#routeloader').removeClass('invisible');
    $('#routecontent').html('');
    $('.sidebarsel').addClass('invisible');
    $('.sidebar').removeClass('invisible');
    loadRoutes();
}

function loadRoutes() {
    var bounds = map.getExtent();
    bounds.transform(map.projection, map.displayProjection);
    $('#routecontent').load(routeinfo_baseurl +'?bbox=' + bounds.toBBOX() + ' .mainpage',
                            function () { $('#routeloader').addClass('invisible'); }
                            );
    doRouteReload = 1;
    routeLayer.removeAllFeatures();
}

function reloadRoutes(map, mapele) {
    if (doRouteReload)
        loadRoutes();
}

function showRouteGPX(response) {
    routeLayer.addFeatures(response.features);
}

function showRouteInfo(osmid) {
    $('#routecontent').load(routeinfo_baseurl + osmid + 
                              '/info .routewin');
    doRouteReload = 0;
    routeLayer.removeAllFeatures();
    var styleloader = new OpenLayers.Protocol.HTTP({
                url: routeinfo_baseurl + osmid + '/json',
                format: new OpenLayers.Format.GeoJSON(),
                callback: showRouteGPX,
                scope: this
                });
  styleloader.read();

}

// general close methd for sidebar
// XXX should that be here?

function closeSidebar() {
    doRouteReload = 0;
    routeLayer.removeAllFeatures();
    $('.sidebar').addClass('invisible');
    $('.sidebarsel').removeClass('invisible');
}

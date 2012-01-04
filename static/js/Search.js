/*
# This file is part of Lonvia's Hiking Map
# Copyright (C) 2012 Sarah Hoffmann
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
# Functions for search.
*/


function searchTerm(word) {
    closeSidebar();
    $('.sbcontent').addClass('invisible');
    $('#searchview').removeClass('invisible');
    $('.sbloading').removeClass('invisible');
    $('.searchcontent').html('');
    $('.sidebarsel').addClass('invisible');
    $('.sidebar').removeClass('invisible');
    //TODO strip search and don do if empty
    var surl = searchurl + '?term=' + encodeURIComponent(word);
    $('#rsearchcontent').load(surl + ' .mainpage',
                 function () { 
                      $('#rsearchloader').addClass('invisible'); }
                 );
    
    return false;
}

function showSearchInfo(osmid) {
    $('#routeinfoloader').removeClass('invisible');
    $('#routeinfocontent').html('');
    $('#routeinfo .backlink').addClass('invisible');
    $('#searchbacklink').removeClass('invisible');
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
                callback: showRouteGPX,
                scope: this
                });
  styleloader.read();

}

function showSearchResults() {
     $('#routeinfo').addClass('invisible');
     $('#searchview').removeClass('invisible');
}

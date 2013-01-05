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
# Functions for search.
*/

var searchcount = 0; //query serialisation
/* Start a new search */
function searchTerm(word) {
    $('#sb-search .ui-input-search').addClass('invisible');
    word = $.trim(word);
    if (word != '') {
        if (isNaN(Number(word))) {
            WMTSidebar.show('search');
            $('#search-title-term').removeClass('invisible');
            $('#searchterm').html(word);
            searchForWord(word);
        } else {
            document.location.href = basemapurl + 'relation/' + word;
        }
    }
    
    return false;
}

function searchForWord(word) {
    $('#search-results').removeClass('invisible');
    $('.searchcontent').html('');
    routeSearchTerm(word, 10);
    // nominatim search
    var surl = placesearchurl + encodeURIComponent(word);
    surl += '?maxresults=10';
    searchcount++;
    var sid = searchcount;
    $.get(surl, function (data) {
                if (searchcount == sid) {
                  $('#psearchloader').addClass('invisible');
                  $('#psearchcontent').html(jQuery("<div>").append(data).find('.mainpage'));
                }
               }
           );
    return false;
}

/* Start a search from the search form */
function searchForm() {
    WMTSidebar.show('search');
    $('#search-results').addClass('invisible');
    $('#search-title-form').removeClass('invisible');
    $('#sb-search .ui-input-search').removeClass('invisible');
}

/* (re)initiate route search
   Also called when 'more results' is clicked.
 */
var routesearchcount = 0;
function routeSearchTerm(word, numresults) {
    // route search
    $('#rsearchloader').removeClass('invisible');
    var surl = routesearchurl + encodeURIComponent(word);
    surl += '?maxresults=' + numresults;
    surl += '&moreresults=' + (numresults+10);
    routesearchcount++;
    var sid = routesearchcount;
    $.get(surl, function (data) {
                if (routesearchcount == sid) {
                  $('#rsearchloader').addClass('invisible');
                  $('#rsearchcontent').html(jQuery("<div>").append(data).find('.mainpage'));
                }
               }
           );
}    


/* load and show route details after search
   Similar to showing route details in the route window
   but allows to return to search results and zooms in on route.
 */
function showSearchInfo(osmid, xmin, ymin, xmax, ymax) {
    $('.sbcontent').addClass('invisible');
    $('#sb-routes').removeClass('invisible');
    showRouteInfo(osmid, showSearchResults);
    // zoom to route
    var bnds = new OpenLayers.Bounds(xmin, ymin, xmax, ymax);
    map.zoomToExtent(bnds);

}

/* return to search result after inspecting route details */
function showSearchResults() {
    $('.sbcontent').addClass('invisible');
    $('#sb-search').removeClass('invisible');
}


$('#tb-search').click(searchForm);

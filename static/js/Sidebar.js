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
# Base functions for sidebar.
*/

// namespacing
var WMTSidebar = {};

/*
 * Toggle visibility of a certain content page.
 * If the page is already visible, close the sidebar
 * otherwise show the page. 
 */
WMTSidebar.show = function (page) {
    var pageclass = '#sb-' + page;
    // remove old ones
    WMTSidebar.close();
    $('.sbpage').addClass('invisible');
    $('.sbcontent').addClass('invisible');
    $('.sbloading').removeClass('invisible');
    
    // show new content
    $("#sidebar-header .infobtn").addClass("invisible");
    $(pageclass).removeClass('invisible');
    $('.sidebar').removeClass('invisible');

    // add title, if applicable
    $('#' + page + '-title').removeClass('invisible');
}

WMTSidebar.close = function () {
    $('.sidebar').addClass('invisible');
    $('.sidebar').removeClass('minimized');
    $("#sbsmall .ui-icon").addClass('ui-icon-arrow-u');
    $("#sbsmall .ui-icon").removeClass('ui-icon-arrow-d');
}

WMTSidebar.toggleMini = function () {
    $("#sbsmall .ui-icon").toggleClass('ui-icon-arrow-d ui-icon-arrow-u');
    $(".sidebar").toggleClass("minimized");
    $("#sbback").toggleClass('invisible');
}


$("#sbclose").click(WMTSidebar.close);

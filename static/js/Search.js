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
 /*   var cnttxt = $('#routecontent');
    cnttext.html('');
    cnttext.load(searchurl + '?' + encodeURIComponent(word),
                 function () { 
                      $('#routeloader').addClass('sbclosedcontent');
                      $('#routeloader').removeClass('sbopencontent'); }
                 );
   */ 
    return false;
}

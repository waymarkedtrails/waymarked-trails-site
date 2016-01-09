Osgende.FormFill = {

    'text' : function(elem, value) { elem.text(value); },
    'attr-src' : function(elem, value) { elem.attr('src', value); },
    'attr-href' : function(elem, value) { elem.attr('href', value); },

    'osm-url' : function(elem, value, data) {
      elem.empty();
      elem.append($(document.createElement("a"))
                    .attr({href: 'http://www.openstreetmap.org/'
                                  + data.type + "/" + data.id})
                    .text(data.type + ' ' + data.id));
    },

    'length' : function(elem, value, data) {
      if (value < 1000)
        elem.text(value + ' m');
      else if (value < 10000)
        elem.text((value/1000).toFixed(2) + ' km');
      else
        elem.text((value/1000).toFixed() + ' km');
    },

    'api-link' : function(elem, value, data) {
      elem.attr('href', Osgende.API_URL + "details/" + data.type
                          + "/" + data.id + "/" + elem.data('db-api'));
    },

    'tags' : function(elem, value) {
        var tag_keys = [];
        for (var k in value)
            tag_keys.push(k);
        tag_keys.sort(function (a, b) { return a.localeCompare(b); });
        elem.empty();
        $.each(tag_keys, function (i, k) {
            elem.append($(document.createElement("tr"))
                        .append($(document.createElement("td")).text(k))
                        .append($(document.createElement("td")).text(value[k]))
                     );
        });
    },

    'routelist' : function(elem, value, data) {
      $.each(value, function(i, r) {
        var o = $(document.createElement("a"))
                  .attr({ href : '#route?type=' + r.type + '&id=' + r.id })
                  .data({ routeType : r.type })
                  .data({ routeId : r.id });

        if ('symbol_id' in r)
          o.append($(document.createElement("img"))
                   .attr({ src : data.symbol_url + r.symbol_id + '.png',
                           'class' : 'ui-li-icon'}));
        o.append($(document.createElement("h3")).text(r.name));
        if ('local_name' in r)
          o.append($(document.createElement("p")).text(r.local_name));
        elem.append($(document.createElement("li"))
                         .attr({ 'data-icon' : false,
                                 'data-group' : r.group})
                         .append(o));
      });
      $("a", elem[0]).click(function(event) {
        event.preventDefault();
        var onroute = $(":mobile-pagecontainer").pagecontainer("getActivePage")[0].id == 'route';
        $.mobile.navigate("#route?type=" + $(this).data("routeType") + "&id=" + $(this).data("routeId"));
        if (onroute) {
          $("#route .ui-panel").panel("close");
          $("#route .ui-panel").panel("open");
        }
      })
      .hover(function(event) {
              $(this).addClass("list-select");
              var feat = map.vector_layer.getSource().getFeatureById($(this).data("routeType")[0] + $(this).data("routeId"));
              if (feat)
                  feat.setStyle(new ol.style.Style({
                                    stroke: new ol.style.Stroke({
                                            color: [211, 255, 5, 0.6],
                                            width: 10,
                                            }),
                                     zindex: 1
                                }));
             }, function(event) {
              $(this).removeClass("list-select");
              var feat = map.vector_layer.getSource().getFeatureById($(this).data("routeType")[0] + $(this).data("routeId"));
              if (feat)
                  feat.setStyle(null);
             });
    },

   'placelist' : function(elem, data, map) {
     $.each(data, function(i, r) {
       var ext = [
            parseFloat(r.boundingbox[2]),
            parseFloat(r.boundingbox[0]),
            parseFloat(r.boundingbox[3]),
            parseFloat(r.boundingbox[1])];
       ext = ol.proj.transformExtent(ext, "EPSG:4326", "EPSG:3857");
       var o = $(document.createElement("a"))
                  .attr({ href : '#search'})
                  .data({ bbox : ext })
                  .text(r.display_name);
       o.append($(document.createElement("img"))
                  .attr({ src : r.icon, 'class' : 'ui-li-icon'}));
       elem.append($(document.createElement("li"))
                         .attr({ 'data-icon' : false,
                                 'data-group' : r.group})
                         .append(o));
     });
     $("a", elem[0]).on("click", function(event) {
        event.preventDefault();
        map.getView().fit($(this).data('bbox'), map.getSize());
     });
   }

}

Osgende.make_segment_url = function(objs, map) {
  var ids = {};
  $.each(objs, function(i, r) {
    if (r.type in ids)
      ids[r.type] += ',' + r.id;
    else
      ids[r.type] = '' + r.id;
  });
  var extent = map.getView().calculateExtent(map.getSize());
  var segment_url = Osgende.API_URL + "/list/segments?bbox=" + extent;
  $.each(ids, function(k, v) { segment_url += '&' + k + 's=' + v; });

  return segment_url;
}

Osgende.RouteList = function(map, container) {
  $("div:first-child", container)
    .on("panelopen", function() {
      map.map.on('moveend', update_list);
    })
    .on("panelclose", function() { map.map.un('moveend', update_list); })
    .on("refresh", update_list);

  function update_list() {
    var extent = map.map.getView().calculateExtent(map.map.getSize());
    $.getJSON(Osgende.API_URL + "/list/by-area", {bbox: extent.join()})
       .done(function (data) { rebuild_list(data, extent); })
       .fail(function( jqxhr, textStatus, error ) {
          var err = textStatus + ", " + error;
          console.log( "Request Failed: " + err );
        });
  }


  function rebuild_list(data, extent) {
    var obj_list = $(".ui-listview", container);
    obj_list.empty();
    Osgende.FormFill.routelist(obj_list, data['results'], data);
    obj_list.listview({autodividers : true,
                       autodividersSelector : Osgende.group_result_list
    }).listview("refresh");

    map.vector_layer.setSource(new ol.source.Vector({
            url: Osgende.make_segment_url(data['results'], map.map),
            format: new ol.format.GeoJSON()
    }));;


  }
}

Osgende.Search = function(map, container) {
  $("div:first-child", container)
    .on("refresh", function() {
      var q = decodeURI(window.location.hash.replace(
               new RegExp("^(?:.*[&\\?]query(?:\\=([^&]*))?)?.*$", "i"), "$1"));
       if (q)
         start_search(q);
    });

  function start_search(query) {
    $.getJSON(Osgende.API_URL + "/list/search", {query: query, limit: 10})
       .done(function(data) { build_route_list(query, data); } )
       .fail(function( jqxhr, textStatus, error ) {
          var err = textStatus + ", " + error;
          console.log( "Request Failed: " + err );
        });
  }

  function build_route_list(query, data) {
    var obj_list = $(".ui-listview", container);
    obj_list.empty();
    obj_list.append($(document.createElement("li"))
                    .attr({"data-role": "list-divider"})
                    .text('Routes'));
    Osgende.FormFill.routelist(obj_list, data['results'], data);
    obj_list.listview("refresh");

    map.vector_layer.setSource(new ol.source.Vector({
            url: Osgende.make_segment_url(data['results'], map.map),
            format: new ol.format.GeoJSON()
    }));;

    $.getJSON("http://nominatim.openstreetmap.org/search", {q: query, format: 'jsonv2'})
       .done(build_place_list)
       .fail(function( jqxhr, textStatus, error ) {
          var err = textStatus + ", " + error;
          console.log( "Request Failed: " + err );
        });
  }

  function build_place_list(data) {
    var obj_list = $(".ui-listview", container);
    obj_list.append($(document.createElement("li"))
                    .attr({"data-role": "list-divider"})
                    .text('Places'));
    Osgende.FormFill.placelist(obj_list, data, map.map);
    obj_list.listview("refresh");
  }

}

Osgende.RouteDetails = function(map, container) {
  $("div:first-child", container)
    .on("refresh", function() {
       var rid = decodeURI(window.location.hash.replace(
               new RegExp("^(?:.*[&\\?]id(?:\\=([^&]*))?)?.*$", "i"), "$1"));
       var rtype = decodeURI(window.location.hash.replace(
               new RegExp("^(?:.*[&\\?]type(?:\\=([^&]*))?)?.*$", "i"), "$1"));
       if (rid)
           load_route(rtype, rid);
    })
    .on("panelbeforeclose", function() {
        map.vector_layer.setStyle(null);
    });

  $(".zoom-button").on("click", function(event) {
     event.preventDefault();
     map.map.getView().fit($(this).data('bbox'), map.map.getSize());
  });

  $(".gpx-button").on("click", function(event) { event.stopPropagation(); });

  var ele = Osgende.ElevationSection(map, $("#elevation-section")[0]);

  function load_route(type, id) {
    $(".browser.content", container).html("Info");
    $(".sidebar-content", container).hide();
    $.mobile.loader("show");
    $.getJSON(Osgende.API_URL + "/details/" + type + "/" + id)
       .done(rebuild_form)
       .fail(function( jqxhr, textStatus, error ) {
          var err = textStatus + ", " + error;
          $(".sidebar-error", container)
            .html(err)
            .show();
        })
       .always(function() { $.mobile.loader("hide"); });
    map.vector_layer.setStyle(new ol.style.Style({
           stroke: new ol.style.Stroke({
                     color: [211, 255, 5, 0.6],
                     width: 10,

                   }),
           zindex: 1
    }));
    map.vector_layer.setSource(new ol.source.Vector({
            url: Osgende.API_URL + "/details/" + type + "/" + id + '/geometry',
            format: new ol.format.GeoJSON()
    }));
  }

  function rebuild_form(data) {
    ele.reload(data.type, data.id, data.mapped_length);
    $("[data-field]", container).removeClass("has-data");
    $(".data-field-optional").hide();
    $("[data-db-type=routelist]", container).empty();

    $("[data-field]", container).each(function() {
       if ($(this).data('field') in data) {
         Osgende.FormFill[$(this).data('db-type')]($(this), data[$(this).data('field')], data);
         $(this).addClass("has-data");
       }
    });

    $("[data-db-type=routelist]", container).listview("refresh");
    $(".zoom-button").data('bbox', data.bbox);

    $(".data-field-optional").has(".has-data").show();
    $(".sidebar-data", container).show();
  }
}

$(function() {
  // Make osm link behave as a permalink. Not the best place to do it but it
  // cannot be done in the template because it's inside a translated string.
  $('a[href|="http://www.openstreetmap.org"]').addClass('osm-map-link')

  $.mobile.ignoreContentEnabled = true;
  $("[data-role='header'], [data-role='footer']").toolbar();
  $("[data-role='footer-controlgroup']").controlgroup();
  $(".sidebar-loader").loader({ defaults: true });

  $(":mobile-pagecontainer").on("pagecontainershow", function(event, ui) {
    $(".ui-panel", ui.toPage).panel("open");
  });

  $(":mobile-pagecontainer").on("pagecontainerchange", function(event, ui) {
    $(".ui-panel", ui.toPage).trigger("refresh");
  });

  $("#api-last-update").load(Osgende.API_URL + "/last-update");

  $("#searchform").on("submit", function(event) {
    $.mobile.navigate('#search?' + $(this).serialize());
    event.preventDefault();
  });

  var typemaps = { 'img' : 'attr-src',
                   'a' : 'attr-href'
                 }
  $("[data-field]:not([data-db-type])").each(function() {
    $(this).attr('data-db-type', typemaps[this.tagName.toLowerCase()] || 'text');
  });

  map = Osgende.BaseMapControl();
  Osgende.RouteList(map, $("#routelist")[0]);
  Osgende.RouteDetails(map, $("#routes")[0]);
  Osgende.Search(map, $("#search")[0]);
});

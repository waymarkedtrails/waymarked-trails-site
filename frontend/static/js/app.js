Osgende.pendingRequest = null;
Osgende.lang = null;
Osgende.highlight_stroke = new ol.style.Stroke({
                             color: [211, 255, 5, 0.6],
                             width: 10,
                           });

Osgende.FormFill = {

    'text' : function(elem, value) { elem.text(value); },
    'attr-src' : function(elem, value) { elem.attr('src', value); },
    'attr-href' : function(elem, value) { elem.attr('href', value); },

    'osm-url' : function(elem, value, data) {
      elem.empty();
      elem.append($(document.createElement("a"))
                    .attr({href: 'https://www.openstreetmap.org/'
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
      var options = ''
      if (Osgende.lang)
        options += '?lang=' + Osgende.lang;
      elem.attr('href', Osgende.API_URL + "/details/" + data.type
                          + "/" + data.id + "/" + elem.data('db-api') + options);
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

    'routelist' : function(elem, value, data, maxele) {
      if (elem.data('sorted'))
        value.sort(function (a, b) { return a.name.localeCompare(b.name); });
      $.each(value, function(i, r) {
        if (i >= maxele) return;
        var href = '#route?id=' + r.id;
        if (r.type != 'relation')
          href += '&type=' + r.type;
        var o = $(document.createElement("a"))
                  .attr({ href : href })
                  .attr({ title : r.name })
                  .data({ routeType : r.type })
                  .data({ routeId : r.id });

        if ('symbol_id' in r)
          o.append($(document.createElement("img"))
                   .attr({ src : data.symbol_url + r.symbol_id + '.svg',
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
        var href = '#route?id=' + $(this).data("routeId");
        if ($(this).data("routeType") != 'relation')
          href += '&type=' + $(this).data("routeType");
        $.mobile.navigate(href);
        if (onroute) {
          $("#route .ui-panel").panel("close");
          $("#route .ui-panel").panel("open");
        }
      })
      .hover(function(event) {
              map.vector_layer_detailedroute.setStyle(null);
              $(this).addClass("list-select");
              var feat = map.vector_layer.getSource().getFeatureById($(this).data("routeType")[0] + $(this).data("routeId"));
              if (feat)
                  feat.setStyle(new ol.style.Style({
                                    stroke: Osgende.highlight_stroke,
                                    zindex: 1
                                }));
             }, function(event) {
              map.vector_layer_detailedroute.setStyle(new ol.style.Style({
                     stroke: Osgende.highlight_stroke,
                     zindex: 1
              }));
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
       var split = r.display_name.indexOf(',');
       ext = ol.proj.transformExtent(ext, "EPSG:4326", "EPSG:3857");
       var o = $(document.createElement("a"))
                  .attr({ href : '#search',
                          'class' : 'li-search-result'})
                  .data({ bbox : ext });
       if ('icon' in r)
         o.append($(document.createElement("img"))
                    .attr({ src : r.icon, 'class' : 'ui-li-icon'}));
       else
         o.append($(document.createElement("img"))
                    .attr({ src : Osgende.MEDIA_URL + '/img/dot.png', 'class' : 'ui-li-icon'}));
       if (split < 0)
         o.append($(document.createElement("h3")).text(r.display_name));
       else {
         o.append($(document.createElement("h3")).text(r.display_name.substring(0,split)));
         o.append($(document.createElement("p")).text(r.display_name.substring(split + 1)));
       }
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
    .on("refresh", function() {
      var ids = decodeURI(window.location.hash.replace(
        new RegExp("^(?:.*[&\\?]ids(?:\\=([^&]*))?)?.*$", "i"), "$1"));
      update_list(ids);
    });

  function update_list(ids) {
    $(".more-msg").hide();
    if (ids && jQuery.type(ids) == "string") {
      // if ids-parameter is given and is not an ol.MapEvent from the moveend callback
      $.getJSON(Osgende.API_URL + "/list/by-ids", {ids: ids})
         .done(function (data) { rebuild_list(data); })
         .fail(function () { $(container).addClass("sidebar-error-mode"); });
    } else {
      $.getJSON(Osgende.API_URL + "/list/by-area", {bbox: map.visible_bbox().join(),
                                                    limit: 21})
         .done(function (data) { rebuild_list(data); })
         .fail(function () { $(container).addClass("sidebar-error-mode"); });
    }
  }


  function rebuild_list(data) {
    $(container).removeClass("sidebar-error-mode");
    var obj_list = $(".ui-listview", container);
    obj_list.empty();
    Osgende.FormFill.routelist(obj_list, data['results'], data, 20);
    var div_func;
    if (Osgende.GROUP_SHIFT)
      div_func = function(ele) {
         return Osgende.GROUPS[$(ele).data('group') / Osgende.GROUP_SHIFT] || Osgende.GROUPS_DEFAULT;
      };
    else
      div_func = function(ele) {
         return Osgende.GROUPS[$(ele).data('group')] || Osgende.GROUPS_DEFAULT;
      };
    obj_list.listview({autodividers : true,
                       autodividersSelector : div_func
    }).listview("refresh");

    map.vector_layer.setSource(new ol.source.Vector({
            url: Osgende.make_segment_url(data['results'], map.map),
            format: new ol.format.GeoJSON()
    }));

    if (data['results'].length > 20)
      $(".more-msg").show();
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
       .fail(function () { start_place_search(query); });
  }

  function build_route_list(query, data) {
    var obj_list = $(".ui-listview", container);
    obj_list.empty();
    obj_list.append($(document.createElement("li"))
                    .attr({"data-role": "list-divider"})
                    .text('Routes'));
    Osgende.FormFill.routelist(obj_list, data['results'], data, 10);
    obj_list.listview("refresh");

    map.vector_layer.setSource(new ol.source.Vector({
            url: Osgende.make_segment_url(data['results'], map.map),
            format: new ol.format.GeoJSON()
    }));

    start_place_search(query);
  }

  function start_place_search(query) {
    $.getJSON("https://nominatim.openstreetmap.org/search?q=" + query + '&format=jsonv2')
       .done(build_place_list);
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
  lh = window.location.hash;
  if (lh.indexOf('map=') >= 0)
    lh = '';
  $("div:first-child", container)
    .on("panelopen", function() {
      map.map.on('moveend', load_subroutes);
    })
    .on("panelclose", function() { map.map.un('moveend', load_subroutes); })
    .on("refresh", function() {
       var rid = decodeURI(window.location.hash.replace(
               new RegExp("^(?:.*[&\\?]id(?:\\=([^&]*))?)?.*$", "i"), "$1"));
       var rtype = decodeURI(window.location.hash.replace(
               new RegExp("^(?:.*[&\\?]type(?:\\=([^&]*))?)?.*$", "i"), "$1"))
                   || 'relation';
       if (rid)
           load_route(rtype, rid);
    })
    .on("panelbeforeclose", function() {
        map.vector_layer.setStyle(null);
        map.vector_layer_detailedroute.setSource(null);
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
    $.getJSON(Osgende.API_URL + "/details/" + type + "/" + id)
       .done(function(data) {
         load_geometry(type, id);
         rebuild_form(data);
         load_subroutes();
       })
       .fail(function() {
         $(".sidebar-error", container).show(); 
       });
  }

  function load_subroutes() {
    if ($(container).data('routelist').length > 0)
    {
      map.vector_layer.setSource(new ol.source.Vector({
              url: Osgende.make_segment_url($(container).data('routelist'), map.map),
              format: new ol.format.GeoJSON()
      }));
    }
  }

  function load_geometry(type, id) {
    map.vector_layer_detailedroute.setStyle(new ol.style.Style({
           stroke: Osgende.highlight_stroke,
           zindex: 1
    }));
    map.vector_layer_detailedroute.setSource(new ol.source.Vector({
            url: Osgende.API_URL + "/details/" + type + "/" + id + '/geometry',
            format: new ol.format.GeoJSON()
    }));
  }

  function rebuild_form(data) {
    // load geometry in background
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

    routelist = []
    if ('subroutes' in data)
      $.merge(routelist, data['subroutes']);
    if ('superroutes' in data)
      $.merge(routelist, data['superroutes']);
    $(container).data('routelist', routelist);

    if (lh && window.location.hash.indexOf(lh) == 0)
     map.map.getView().fit(data.bbox, map.map.getSize());
    lh = '';
  }
}

$(function() {
  // Make osm link behave as a permalink. Not the best place to do it but it
  // cannot be done in the template because it's inside a translated string.
  $('a[href|="https://www.openstreetmap.org"]').addClass('osm-map-link')

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

  $.get(Osgende.API_URL + "/last-update", function(data) {
    var d = new Date(data);
    $("#api-last-update").text(d.toLocaleString());
  });

  $(".search-form").on("submit", function(event) {
    $.mobile.navigate('#search?' + $(this).serialize());
    event.preventDefault();
  });

  var typemaps = { 'img' : 'attr-src',
                   'a' : 'attr-href'
                 }
  $("[data-field]:not([data-db-type])").each(function() {
    $(this).attr('data-db-type', typemaps[this.tagName.toLowerCase()] || 'text');
  });

  $.ajaxPrefilter(function(options, originalOptions, jqXHR) {
    if (Osgende.pendingRequest)
      Osgende.pendingRequest.abort();
    Osgende.pendingRequest = jqXHR;
    if (Osgende.lang)
      if (options.data)
        options.data += "&lang=" + Osgende.lang;
      else
        options.data = "lang=" + Osgende.lang;
  });

  Osgende.lang = decodeURI(window.location.search.replace(
               new RegExp("^(?:.*[&\\?]lang(?:\\=([^&]*))?)?.*$", "i"), "$1"));
  if (Osgende.lang) {
    $('#language-select option[value=' + Osgende.lang + ']').prop('selected', true);
    $('.lang-link').each(function() {
      this.setAttribute('href', this.href + '?lang=' + Osgende.lang);
    });
  }

  $(window).load(function(){
    $("#language-select").on("change", function(event, ui) {
      var oldloc = location;
      if (this.value)
        oldloc.search = "?lang=" + this.value;
      else
        oldloc.search = ''
      location = oldloc;
    });

    $(".btn-roll-up").on("click", function(event) {
      $(this).parents('.ui-panel').toggleClass('panel-hidden');
      $(this).toggleClass('ui-icon-carat-d ui-icon-carat-u');
      event.preventDefault();
    });
  });

  map = Osgende.BaseMapControl($("#settings")[0]);
  Osgende.RouteList(map, $("#routelist")[0]);
  Osgende.RouteDetails(map, $("#route")[0]);
  Osgende.Search(map, $("#search")[0]);
});

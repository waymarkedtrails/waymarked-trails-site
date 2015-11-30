lg = console.log;
API_URL = '/api';
MEDIA_URL = 'http://marama/wmt-static';
TILE_URL = 'http://marama/tiles/hiking';

Osgende = {}

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
      elem.attr('href', API_URL + "/relation/" + data.id + "/" + elem.data('db-api'));
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
      elem.empty();
      $.each(value, function(i, r) {
        var o = $(document.createElement("a"))
                  .attr({ href : '#route?id=' + r.id })
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
                                 'data-importance' : r.importance})
                         .append(o));
      });
      $("a", elem[0]).on("click", function(event) {
        event.preventDefault();
        var onroute = $(":mobile-pagecontainer").pagecontainer("getActivePage")[0].id == 'route';
        $.mobile.navigate("#route?id=" + $(this).data("routeId"));
        if (onroute) {
          $("#route .ui-panel").panel("close");
          $("#route .ui-panel").panel("open");
        }
      });
      elem.listview("refresh")
    }

}

Osgende.RouteList = function(map, container) {
  $("div:first-child", container)
    .on("panelopen", function() {
      update_list();
      map.map.on('moveend', update_list);
    })
    .on("panelclose", function() { map.map.un('moveend', update_list); });

  function update_list() {
    var extent = map.map.getView().calculateExtent(map.map.getSize());
    $.getJSON(API_URL + "/list/by-area", {bbox: extent.join()})
       .done(rebuild_list)
       .fail(function( jqxhr, textStatus, error ) {
          var err = textStatus + ", " + error;
          console.log( "Request Failed: " + err );
        });
  }


  function rebuild_list(data) {
    var obj_list = $(".ui-listview", container);
    Osgende.FormFill.routelist(obj_list, data['relations'], data);
    obj_list.listview({autodividers : true,
                          autodividersSelector : function(ele) {
                            var imp = $(ele).data("importance");
                            if (imp < 10)
                              return 'international';
                            else if (imp < 20)
                              return 'national'
                            else if (imp < 30)
                              return 'regional';
                            else
                              return 'local';
    }}).listview("refresh");
  }
}

Osgende.RouteDetails = function(map, container) {
  $("div:first-child", container)
    .on("panelbeforeopen", function() {
       var rid = decodeURI(window.location.hash.replace(
               new RegExp("^(?:.*[&\\?]id(?:\\=([^&]*))?)?.*$", "i"), "$1"));
       if (rid)
           load_route(rid);
    })
    .on("panelbeforeclose", function() {
        map.vector_layer.setStyle(null);
    });

  $(".zoom-button").on("click", function(event) {
     event.preventDefault();
     map.map.getView().fit($(this).data('bbox'), map.map.getSize());
  });

  $(".gpx-button").on("click", function(event) { event.stopPropagation(); });

  function load_route(id) {
    $(".browser.content", container).html("Info");
    $(".sidebar-content", container).hide();
    $.mobile.loader("show");
    $.getJSON(API_URL + "/relation/" + id)
       .done(rebuild_form)
       .fail(function( jqxhr, textStatus, error ) {
          var err = textStatus + ", " + error;
          $(".sidebar-error", container)
            .html(err)
            .show();
        })
       .always(function() { $.mobile.loader("hide"); });
    map.vector_layer.setStyle([new ol.style.Style({
           stroke: new ol.style.Stroke({
                     color: [211, 255, 5, 0.6],
                     width: 10,

                   }),
           zindex: 1
    })]);
    map.vector_layer.setSource(new ol.source.Vector({
            url: API_URL + "/relation/" + id + '/geometry',
            format: new ol.format.GeoJSON()
    }));
  }

  function rebuild_form(data) {
    $("[data-field]", container).removeClass("has-data");
    $(".data-field-optional").hide();

    $("[data-field]", container).each(function() {
       if ($(this).data('field') in data) {
         Osgende.FormFill[$(this).data('db-type')]($(this), data[$(this).data('field')], data);
         $(this).addClass("has-data");
       }
    });

    $(".zoom-button").data('bbox', data.bbox);

    $(".data-field-optional").has(".has-data").show();
    $(".sidebar-data", container).show();
  }
}

$(function() {
  $("[data-role='header'], [data-role='footer']").toolbar();
  $("[data-role='footer-controlgroup']").controlgroup();
  $(".sidebar-loader").loader({ defaults: true });

  $(":mobile-pagecontainer").on("pagecontainershow", function(event, ui) {
    $(".ui-panel", ui.toPage).panel("open");
  });

  $("#api-last-update").load(API_URL + "/last-update");

  $("#searchform").on("submit", function(event) {
    $.mobile.navigate('#search?' + $(this).serialize());
    event.preventDefault();
  });

  $("#search-panel").on("open", function(event, ui) {
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
});

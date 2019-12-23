Osgende.GuidePostDetails = function(map, container) {
  lh = window.location.hash;
  if (lh.indexOf('map=') >= 0)
    lh = '';

  $("div:first-child", container)
    .on("refresh", function() {
       var rid = decodeURI(window.location.hash.replace(
               new RegExp("^(?:.*[&\\?]id(?:\\=([^&]*))?)?.*$", "i"), "$1"));
       if (rid)
         load_guidepost(rid);
    })
    .on("panelbeforeclose", function() {
        map.vector_layer_detailedroute.setSource(null);
    });

  $(".zoom-button", container).on("click", function(event) {
    event.preventDefault();
    map.map.getView().fit($(this).data('bbox'), map.map.getSize());
  });

  function load_guidepost(id) {
    $(".sidebar-content", container).hide();
    $("#guidepost-destination-table tbody", container).html("");
    $.getJSON(Osgende.API_URL + "/details/guidepost/" + id)
      .done(function(data) { rebuild_form(data); })
      .fail(function() { $(".sidebar-error", container).show() });
  }

  function rebuild_form(data) {
    // load directions in background now
    $(".destination-content", container).hide();
    $(".destination-loading", container).show();
    $.getJSON(Osgende.GUIDEPOST_URL + "code/generate.pl?nodeid=" + data.id + "&namedroutes&fromarrow&format=json&distunit=m&fast=1")
      .always(function(data) { $(".destination-loading", container).hide(); })
      .done(function(data) { rebuild_destinations(data); })
      .fail(function(data) { $(".destination-error", container).show(); });
    $("[data-field]", container).removeClass("has-data");
    $("[data-field]", container).html("");
    $(".data-field-optional").hide();

    $("[data-field]", container).each(function() {
       if ($(this).data('field') in data) {
         Osgende.FormFill[$(this).data('db-type')]($(this), data[$(this).data('field')], data);
         $(this).addClass("has-data");
       }
    });

    // highlight point
    var pt = new ol.geom.Point([data.x, data.y]);
    map.vector_layer_detailedroute.setStyle(Osgende.highlight_circle);
    var src = new ol.source.Vector();
    src.addFeature(new ol.Feature(new ol.geom.Point([data.x, data.y])));
    map.vector_layer_detailedroute.setSource(src);

    $(".data-field-optional").has(".has-data").show();
    $(".sidebar-data", container).show();

    $(".zoom-button", container).data('bbox', pt);

    if (lh && window.location.hash.indexOf(lh) == 0)
     map.map.getView().fit(pt);
    lh = '';
  }

  function format_distance(d) {
    var dur = '';
    if (d.duration) {
        var parts = d.duration.split(':', 2);
        if (parts.length == 2) {
            var h = parseInt(parts[0], 10);
            var m = parseInt(parts[1], 10);
            if (h < 1) {
                dur = m + "&#8239;min";
            } else {
                dur = h + "&hairsp;h";
                if (m > 0) {
                    dur += '&#8239;' + parts[1];
                }
            }
        }
    }
    if (d.distance) {
        if (dur) {
            dur += ' / ';
        }
        if (d.distance < 1000) {
            dur += d.distance + 'm';
        } else {
            dur += d.distance / 1000 + 'km';
        }
    }

    return dur;
  }

  function rebuild_destinations(data) {
    $(".destination-more-link", container).attr('href', Osgende.GUIDEPOST_URL + "example/index.htm#node=" + data.node);
    var desttab = $("#guidepost-destination-table tbody", container);
    data.data.sort(function(a, b) {
        if (a.dir == b.dir)
            return a.id - b.id;
        return a.dir - b.dir;
    });
    var currel = null;
    var part = 0;
    data.data.forEach(function (d) {
        if (d.id !== currel) {
            part++;
        }
        var arrow = '&#10137;';
        if (d.id) {
            arrow = '<a target="_new" href="https://www.openstreetmap.org/relation/' + d.id + '">&#10137;</a>';
        }
        $("<tr />",
          { "class" : d.id && d.id == currel ? "dest-same-rel" : "dest-new-rel" })
            .addClass(part % 2 == 0 ? "dest-even-rel" : "dest-odd-rel")
            .append($("<td />")
                .append($("<div />", {
                            "class" : "dest-arrow",
                            style: 'transform: rotate(' + d.dir + 'deg)',
                            html : arrow })
                ))
            .append($("<td />")
                .text(d.deststring))
            .append($("<td />", { html : format_distance(d), "class" : "dest-dur" }))
        .appendTo(desttab);

        currel = d.id;
    });

    $(".destination-data", container).show();
  }
}


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
    });

  function load_guidepost(id) {
    $(".sidebar-content", container).hide();
    $("#guidpost-destination-table", container).html("");
    $.getJSON(Osgende.API_URL + "/details/guidepost/" + id)
      .done(function(data) { rebuild_form(data); })
      .fail(function() { $(".sidebar-error", container).show() });
  }

  function rebuild_form(data) {
    // load directions in background now
    $(".destination-content", container).hide();
    $.getJSON("http://osm.mueschelsoft.de/destinationsign/code/generate.pl?nodeid=" + data.id + "&namedroutes&fromarrow&format=json&distunit=km&fast=1")
      .done(function(data) { rebuild_destinations(data); })
      .fail(function(data) { $(".destination-error", container).show() });
    $("[data-field]", container).removeClass("has-data");
    $(".data-field-optional").hide();

    $("[data-field]", container).each(function() {
       if ($(this).data('field') in data) {
         Osgende.FormFill[$(this).data('db-type')]($(this), data[$(this).data('field')], data);
         $(this).addClass("has-data");
       }
    });

    $(".data-field-optional").has(".has-data").show();
    $(".sidebar-data", container).show();

    if (lh && window.location.hash.indexOf(lh) == 0)
     map.map.getView().fit([data.lon - 0.001, data.lat -0.001, data.lon + 0.001, data.lat + 0.001], map.map.getSize());
    lh = '';
  }

  function rebuild_destinations(data) {
    var desttab = $("#guidepost-destination-table", container);
    data.data.forEach(function (d) {
        var ele = $(document.createElement("tr"));

        ele.append($(document.createElement("td")).html());
        ele.append($(document.createElement("td")).text(d.dest));

        desttab.append(ele);
    });

    $(".destination-data", container).show();
  }
}


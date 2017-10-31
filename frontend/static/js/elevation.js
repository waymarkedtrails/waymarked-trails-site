
Osgende.ElevationSection = function(map, container) {
  var current = 0; // make sure we only display the last
  var current_type = '';
  var current_length = 0;
  var obj = {};
  var eledata = null;

  var point_style = new ol.style.Style({
                   image: new ol.style.Circle({
                            radius: 5,
                            fill: null,
                            stroke: new ol.style.Stroke({color: 'black', width: 1})
                          })
  });
  var map_point = new ol.Feature();
  map_point.setStyle(new ol.style.Style({
                            image: new ol.style.Circle({
                                       radius: 5,
                                       fill: new ol.style.Fill({color: '#0000ff'}),
                                       stroke: new ol.style.Stroke({color: '#000', width: 1})
                                   })
                         }));

  map.map.addLayer(new ol.layer.Vector({
                     source: new ol.source.Vector({
                               features: [map_point]
                             })
                   }));


  $(container).mouseleave(function() { map_point.setGeometry(null); });

  $(container).bind("plothover", function (event, pos, item) {
    if (!eledata)
      return;

    var low = 0;
    var up = eledata.length - 1;

    if (pos.x < 0 || pos.x > eledata[up].pos) {
      map_point.setGeometry(null);
      return;
    }

    while (low + 1 < up) {
      var mid = Math.floor((low + up)/2);
      if (pos.x < eledata[mid].pos)
        up = mid;
      else
        low = mid;
    }

    var p1 = eledata[low];

    // interpolate between the points
    map_point.setGeometry(new ol.geom.Point([p1.x, p1.y]));
  });

  $(container).on("collapsibleexpand", function (event, pos, item) {
    if (current > 0) {
      eledata = [];
      draw_plot([], [], 0, 100);

      $(".elevation-loading", container).show();
      $.getJSON(Osgende.API_URL + "/details/" + current_type + "/" + current + '/elevation')
        .always(function(data) { $(".elevation-loading", container).hide(); })
        .done(function(data) {
            if (data.id == current)
                rebuild_graph(data, current_length);
         })
        .fail(function(data) {
            if (data.id == current)
                $(".elevation-error", container).show();
         });
    }
  });

  obj.reload = function(otype, oid, length) {
    $(".elevation-content", container).hide();
    $("#elevation-warning", container).hide();
    $(container).collapsible("collapse");
    current_type = otype;
    current = oid;
    current_length = length;
  };

  function rebuild_graph(data, length) {
    $("[data-field=ascent]", container).text(data.ascent + ' m')
    $("[data-field=descent]", container).text(data.descent + ' m')
    var points = [];
    var minele = 20000;
    var maxele = 0;

    $.each(data.segments, function (i, seg) {
      $.each(seg.elevation, function (i, pt) {
        eledata.push(pt);
        var ele = pt.ele < -100 ? null : pt.ele;
        points.push([pt.pos, ele]);
        if (ele < minele)
          minele = ele;
        if (ele > maxele)
          maxele = ele;
      });
      points.push(null);
    });
    var scale_length = eledata[eledata.length - 1].pos;

    if (data.length && data.length > length * 1.1) {
      $("#elevation-warning").show();
    }
    length = data.length || length;

    // set a sensible scale
    var altdiff = (maxele - minele)/10;
    if (altdiff < 20)
      altdiff = 20;
    minele = Math.round((minele - altdiff)/10)*10;
    if (minele + 200 > maxele)
      maxele = minele + 200;
    else
      maxele = Math.round((maxele + altdiff)/10)*10;

    // manually compute the ticks
    length /= 1000;
    var xticks = [];
    var ticklen = length/scale_length;
    var tickstep = 1000;

    var steps = [ 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500 ];
    var maxstep = length / 5;
    for (var i = 0; i < steps.length; i++) {
      if (steps[i] > maxstep) {
        tickstep = steps[i];
        break;
      }
    }

    var pos = tickstep;
    while (pos < length) {
      xticks.push([pos/ticklen, Math.round(pos*10)/10]);
      pos += tickstep;
    }

    $(".elevation-data", container).show();
    draw_plot(points, xticks, minele, maxele);
  }

  function draw_plot(data, xticks, minele, maxele) {
    plot = $.plot($("#elevation-profile"),
        [{data: data, color: 'blue'}], {
          xaxis: {show: true, ticks: xticks},
          yaxis: {min: minele, max: maxele},
          series: {lines: { show: true }, points: { show: false }},
          crosshair: {mode: "x"},
          grid: {
            hoverable: true,
            autoHighlight: false,
            margin: { top : 0, left: 24, bottom: 0, right: 0 }
          }
        });
  }

  return obj;
};

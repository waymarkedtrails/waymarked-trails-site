
Osgende.ElevationSection = function(map, container) {
  var current = 0; // make sure we only display the last
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

    if (pos.x < 0 || pos.x > eledata.length) {
      map_point.setGeometry(null);
      return;
    }

    var p1 = eledata[Math.floor(pos.x)];
    var p2 = eledata[Math.ceil(pos.x)] || p1;

    var coord = [(p1.x + p2.x)/2, (p1.y + p2.y)/2];

    // interpolate between the points
    map_point.setGeometry(new ol.geom.Point(coord));
  });

  obj.reload = function(oid, length) {
    $(container).addClass("ui-disabled");
    $(container).collapsible("collapse");
    current = oid;
    $.getJSON(API_URL + "/relation/" + oid + '/elevation')
      .done(function(data) { if (data.id == current) rebuild_graph(data, length); });
  };

  function rebuild_graph(data, length) {
    $("[data-field=ascent]", container).text(data.ascent + ' m')
    $("[data-field=descent]", container).text(data.descent + ' m')
    var points = [];
    var minele = 20000;
    var maxele = 0;

    eledata = data.elevation;

    $.each(eledata, function (i, pt) {
      var ele = pt.ele < -100 ? null : pt.ele;
      points.push([i, ele]);
      if (ele < minele)
        minele = ele;
      if (ele > maxele)
        maxele = ele;
    });

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
    var ticklen = length/(data.elevation.length - 1);
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

    $(container).removeClass("ui-disabled");
    draw_plot(points, xticks, minele, maxele);
  }

  function draw_plot(data, xticks, minele, maxele) {
    // ugh, drawing goes horribly wrong when the div for the plot is invisible
    $(container).collapsible("expand");
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
    $(container).collapsible("collapse");
  }

  return obj;
};

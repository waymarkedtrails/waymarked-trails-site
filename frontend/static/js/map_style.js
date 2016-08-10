
Osgende.create_network_style = function () {
  var iwnstroke = new ol.style.Stroke({color: '#b20303', width: 7});
  var iwn = new ol.style.Style({stroke: iwnstroke});
  var nwnstroke = new ol.style.Stroke({color: '#152eec', width: 7});
  var nwn = new ol.style.Style({stroke: nwnstroke});
  var rwnstroke = new ol.style.Stroke({color: '#ffa304', width: 7});
  var rwn = new ol.style.Style({stroke: rwnstroke});
  var lwnstroke = new ol.style.Stroke({color: '#db00db', width: 7});
  var lwn = new ol.style.Style({stroke: lwnstroke});
  var chstroke = new ol.style.Stroke({color: '#d30000', width: 7});
  var ch = new ol.style.Style({stroke: chstroke});


  var iconCache = {};
  function getIcon(iconName) {
    var icon = iconCache[iconName];
    if (!icon) {
      icon = new ol.style.Style({image: new ol.style.Icon({
        src: Osgende.MEDIA_URL + '/symbols/hiking/' +  iconName + '.png'
      })});
      iconCache[iconName] = icon;
    }
    return icon;
  }

  var styles = [];
  return function(feature, resolution) {
    var length = 0;
    var cls = feature.get('class');
    var network = feature.get('network');
    var style = feature.get('style');
    var shields = feature.get('shields');
    // iwn
    if (cls & 0xff000000) {
      if (resolution < 38)
        iwnstroke.setWidth(9);
      else if (cls & 0x00ff0000)
        iwnstroke.setWidth(7);
      else if (cls & 0x0000ff00)
        iwnstroke.setWidth(6);
      else
        iwnstroke.setWidth(7);
      styles[length++] = iwn;
    }
    // nwn
    if (cls & 0x00ff0000) {
      if (resolution < 38)
        nwnstroke.setWidth(6);
      else
        nwnstroke.setWidth(4);
      styles[length++] = nwn;
    }
    // rwn
    if (cls & 0x0000ff00) {
      if (resolution < 38)
        rwnstroke.setWidth(5);
      else
        rwnstroke.setWidth(3);
      if (cls & 0x00ff0000)
        rwnstroke.setLineDash([1,7]);
      else
        rwnstroke.setLineDash(null);
      styles[length++] = rwn;
    }
    // lwn
    if (cls & 0x000000ff) {
      styles[length++] = lwn;
      if (resolution > 38)
        lwnstroke.setWidth(1.5);
      else if (cls == 0x000000ff)
        lwnstroke.setWidth(3);
      else
        lwnstroke.setWidth(2);
      styles[length++] = lwn;
    }
    // Swiss style
    if (network == 'CH') {
      if (resolution > 38)
        chstroke.setWidth(1);
      else
        chstroke.setWidth(1.5);
      if (style == 31)
        chstroke.setLineDash(null);
      else if (style == 32)
        chstroke.setLineDash([6,3]);
      else
        chstroke.setLineDash([1,6]);
      styles[length++] = ch;
    }

    // Shields
    if (shields.length > 0) {
      var geom = feature.getGeometry();
      if (geom instanceof ol.geom.LineString) {
        var icon = getIcon(shields[0]);
        var coord = geom.getCoordinateAt(0.5);
        icon.setGeometry(new ol.geom.Point(coord));
        styles[length++] = icon;
      }
    }
    styles.length = length;
    return styles;
  };
}


Osgende.slope_map = {
 '0' : 'unknown',
 '1' : 'downhill',
 '2' : 'nordic',
 '3' : 'skitour',
 '4' : 'sled',
 '5' : 'hike',
 '6' : 'sleigh'
}

Osgende.group_result_list = function(ele) {
  return Osgende.slope_map[$(ele).data('group')] || '';
};

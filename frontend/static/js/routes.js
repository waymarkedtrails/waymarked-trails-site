Osgende.group_result_list = function(ele) {
  var imp = $(ele).data("group");
  if (imp < 10)
    return 'international';
  else if (imp < 20)
    return 'national'
  else if (imp < 30)
    return 'regional';
  else
    return 'local';
}

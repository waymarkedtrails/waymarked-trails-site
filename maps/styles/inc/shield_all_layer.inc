<Layer maximum-scale-denominator="100000" name="AllShields1" buffer-size="10000">
  <Datasource base="psqlch">
    <Parameter name="table">
      (SELECT geom, shld[i] as fname, i as numshield
          FROM (SELECT geom, array_cat(lshields, inrshields) as shld
                FROM &dbschema;.network_style
                WHERE lshields is not null or inrshields is not null) x,
               lateral generate_subscripts(shld, 1) as i order by fname, st_length(geom) desc) as w
    </Parameter>
    </Datasource>
  <StyleName>Shields</StyleName>
</Layer>

<Layer maximum-scale-denominator="400000" minimum-scale-denominator="100000" name="INRShields1" buffer-size="512" >
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT geom, inrshields[i] as fname, i as numshield FROM &dbschema;.network_style, lateral generate_subscripts(inrshields, 1) as i where inrshields is not null) as w</Parameter>
  </Datasource>

  <StyleName>Shields</StyleName>
</Layer>


<Layer maxzoom="400000" minzoom="100000" name="INRShields1" buffer-size="512">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT geom, inrshields[1] as fname, array_length(inrshields,1) as numshields FROM &dbschema;.defstyle where array_length(inrshields,1) &gt; 0) as w</Parameter>
  </Datasource>
  <StyleName>Shields</StyleName>
</Layer>
<Layer maxzoom="400000" minzoom="100000" name="INRShields2" buffer-size="512">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT geom, inrshields[2] as fname, array_length(inrshields,1) as numshields FROM &dbschema;.defstyle where array_length(inrshields,1) &gt; 1) as w</Parameter>
  </Datasource>
  <StyleName>Shields</StyleName>
</Layer>
<Layer maxzoom="400000" minzoom="100000" name="INRShields3" buffer-size="512">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT geom, inrshields[3] as fname, array_length(inrshields,1) as numshields FROM &dbschema;.defstyle where array_length(inrshields,1) &gt; 2) as w</Parameter>
  </Datasource>
  <StyleName>Shields</StyleName>
</Layer>
<Layer maxzoom="400000" minzoom="100000" name="INRShields4" buffer-size="512">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT geom, inrshields[4] as fname, array_length(inrshields,1) as numshields FROM &dbschema;.defstyle where array_length(inrshields,1) &gt; 3) as w</Parameter>
  </Datasource>
  <StyleName>Shields</StyleName>
</Layer>
<Layer maxzoom="400000" minzoom="100000" name="INRShields5" buffer-size="512">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT geom, inrshields[5] as fname, array_length(inrshields,1) as numshields FROM &dbschema;.defstyle where array_length(inrshields,1) &gt; 4) as w</Parameter>
  </Datasource>
  <StyleName>Shields</StyleName>
</Layer>


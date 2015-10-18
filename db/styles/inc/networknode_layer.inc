<Style name="NetworkNodes">
  <Rule>
    <ShieldSymbolizer base="static" dy="-1" face-name="DejaVu Sans Condensed Bold" file="hikingnode.png" vertical-alignment="middle" horizontal-alignment="middle" allow-overlap="true">[name]</ShieldSymbolizer>
  </Rule>
</Style>

<Layer maximum-scale-denominator="100000" name="NetworkNodes" buffer-size="64">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT name, geom FROM &dbschema;.networknodes) as w</Parameter>
  </Datasource>
  <StyleName>NetworkNodes</StyleName>
</Layer>


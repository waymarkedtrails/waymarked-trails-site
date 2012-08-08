<Style name="Guideposts">
  <Rule>
    <ShieldSymbolizer allow-overlap="true" base="static" dy="11" face-name="DejaVu Sans Oblique" file="guidepost_gray.png" halo-radius="2" name="[name]" size="8" />
    <Filter>[name] != ''</Filter>
    <TextSymbolizer allow-overlap="true" dy="17" face-name="DejaVu Sans Oblique" halo-radius="2" name="[ele]" size="8" />
  </Rule>
  <Rule>
    <ElseFilter />
    <PointSymbolizer allow-overlap="true" base="static" file="guidepost_gray.png" />
  </Rule>
</Style>

<Layer maxzoom="50000" name="Guideposts" buffer-size="64">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT name, ele, geom FROM &dbschema;.guideposts) AS w</Parameter>
  </Datasource>
  <StyleName>Guideposts</StyleName>
</Layer>


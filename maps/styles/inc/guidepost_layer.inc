<Style name="Guideposts">
  <Rule>
    <Filter>[name] != ''</Filter>
    <ShieldSymbolizer allow-overlap="true" base="static" dy="18" face-name="DejaVu Sans Oblique" file="guidepost_gray.png" halo-radius="2" size="8">
      [name]+'&#10;'+[ele]
    </ShieldSymbolizer>
  </Rule>
  <Rule>
    <ElseFilter />
    <PointSymbolizer allow-overlap="true" base="static" file="guidepost_gray.png" />
  </Rule>
</Style>

<Layer maximum-scale-denominator="50000" name="Guideposts" buffer-size="64">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT name, ele, geom FROM &dbschema;.guideposts) AS w</Parameter>
  </Datasource>
  <StyleName>Guideposts</StyleName>
</Layer>


<FontSet name="shield-description">
  <Font face-name="DejaVu Sans Oblique" />
  <Font face-name="Arundina Sans Italic" />
  <Font face-name="TSCu_Paranar Italic" />
  <Font face-name="Mallige NormalItalic" />
  <Font face-name="DejaVu Sans Book" />
  <Font face-name="Arundina Sans Regular" />
  <Font face-name="Padauk Regular" />
  <Font face-name="Khmer OS Metal Chrieng Regular" />
  <Font face-name="Mukti Narrow Regular" />
  <Font face-name="gargi Medium" />
  <Font face-name="TSCu_Paranar Regular" />
  <Font face-name="Tibetan Machine Uni Regular" />
  <Font face-name="Mallige Normal" />
  <Font face-name="Droid Sans Fallback Regular" />
  <Font face-name="Unifont Medium" />
</FontSet>

<Style name="Guideposts">
  <Rule>
    <Filter>[name] != ''</Filter>
    <ShieldSymbolizer allow-overlap="true" base="static" unlock-image="true" dy="18" fontset-name="shield-description" file="guidepost_gray.png" halo-radius="2" size="8">
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


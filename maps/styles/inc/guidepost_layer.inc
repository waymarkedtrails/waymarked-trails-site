<FontSet name="shield-description">
  <Font face-name="DejaVu Sans Oblique" />
  <Font face-name="Noto Sans UI Italic" />
  <Font face-name="Noto Sans UI Regular" />
  <Font face-name="Noto Sans CJK JP Regular" />
  <Font face-name="Noto Sans Armenian Regular" />
  <Font face-name="Noto Sans Bengali UI Regular" />
  <Font face-name="Noto Sans Cham Regular" />
  <Font face-name="Noto Sans Devanagari UI Regular" />
  <Font face-name="Noto Sans Devanagari Regular" />
  <Font face-name="Noto Sans Ethiopic Regular" />
  <Font face-name="Noto Sans Georgian Regular" />
  <Font face-name="Noto Sans Gujarati UI Regular" />
  <Font face-name="Noto Sans Gujarati Regular" />
  <Font face-name="Noto Sans Gurmukhi UI Regular" />
  <Font face-name="Noto Sans Hebrew Regular" />
  <Font face-name="Noto Sans Kannada UI Regular" />
  <Font face-name="Noto Sans Khmer UI Regular" />
  <Font face-name="Noto Sans Lao UI Regular" />
  <Font face-name="Noto Sans Malayalam UI Regular" />
  <Font face-name="Noto Sans Myanmar UI Regular" />
  <Font face-name="Noto Sans Oriya UI Regular" />
  <Font face-name="Noto Sans Oriya Regular" />
  <Font face-name="Noto Sans Sinhala Regular" />
  <Font face-name="Noto Sans Tamil UI Regular" />
  <Font face-name="Noto Sans Telugu UI Regular" />
  <Font face-name="Noto Sans Thaana Regular" />
  <Font face-name="Noto Sans Thai UI Regular" />
  <Font face-name="Noto Sans Tibetan Regular" />
  <Font face-name="Noto Naskh Arabic UI Regular" />
  <Font face-name="DejaVu Sans Book" />
  <Font face-name="Droid Sans Fallback Regular" />
  <Font face-name="Unifont Medium" />
</FontSet>

<Style name="Guideposts">
  <Rule>
    <Filter>[name] != '' or [ele] != ''</Filter>
    <MaxScaleDenominator>25000</MaxScaleDenominator>
    <ShieldSymbolizer allow-overlap="true" base="static" unlock-image="true" dy="18" fontset-name="shield-description" file="guidepost_gray.svg" halo-radius="2" size="8">
      [name]+'&#10;'+[ele]
    </ShieldSymbolizer>
  </Rule>
  <Rule>
    <ElseFilter />
    <PointSymbolizer allow-overlap="true" base="static" file="guidepost_gray.svg" />
  </Rule>
</Style>

<Layer maximum-scale-denominator="50000" name="Guideposts" buffer-size="64">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT name, ele, geom FROM &dbschema;.guideposts) AS w</Parameter>
  </Datasource>
  <StyleName>Guideposts</StyleName>
</Layer>


<FontSet name="shield-description">
  <Font face-name="DejaVu Sans Oblique" />
  <Font face-name="Noto Sans UI Italic" />
  <Font face-name="Noto Sans UI Regular" />
  <Font face-name="Noto Sans CJK JP Regular" />
  <Font face-name="Noto Sans Armenian Regular" />
  <Font face-name="Noto Sans Balinese Regular" />
  <Font face-name="Noto Sans Bamum Regular" />
  <Font face-name="Noto Sans Batak Regular" />
  <Font face-name="Noto Sans Bengali UI Regular" />
  <Font face-name="Noto Sans Buginese Regular" />
  <Font face-name="Noto Sans Buhid Regular" />
  <Font face-name="Noto Sans Canadian Aboriginal Regular" />
  <Font face-name="Noto Sans Cham Regular" />
  <Font face-name="Noto Sans Cherokee Regular" />
  <Font face-name="Noto Sans Coptic Regular" />
  <Font face-name="Noto Sans Devanagari UI Regular" />
  <Font face-name="Noto Sans Devanagari Regular" />
  <Font face-name="Noto Sans Ethiopic Regular" />
  <Font face-name="Noto Sans Georgian Regular" />
  <Font face-name="Noto Sans Gujarati UI Regular" />
  <Font face-name="Noto Sans Gujarati Regular" />
  <Font face-name="Noto Sans Gurmukhi UI Regular" />
  <Font face-name="Noto Sans Hanunoo Regular" />
  <Font face-name="Noto Sans Hebrew Regular" />
  <Font face-name="Noto Sans Javanese Regular" />
  <Font face-name="Noto Sans Kannada UI Regular" />
  <Font face-name="Noto Sans Kayah Li Regular" />
  <Font face-name="Noto Sans Khmer UI Regular" />
  <Font face-name="Noto Sans Lao UI Regular" />
  <Font face-name="Noto Sans Lepcha Regular" />
  <Font face-name="Noto Sans Limbu Regular" />
  <Font face-name="Noto Sans Lisu Regular" />
  <Font face-name="Noto Sans Malayalam UI Regular" />
  <Font face-name="Noto Sans Mandaic Regular" />
  <Font face-name="Noto Sans Mongolian Regular" />
  <Font face-name="Noto Sans Myanmar UI Regular" />
  <Font face-name="Noto Sans New Tai Lue Regular" />
  <Font face-name="Noto Sans NKo Regular" />
  <Font face-name="Noto Sans Ol Chiki Regular" />
  <Font face-name="Noto Sans Oriya UI Regular" />
  <Font face-name="Noto Sans Oriya Regular" />
  <Font face-name="Noto Sans Osmanya Regular" />
  <Font face-name="Noto Sans Samaritan Regular" />
  <Font face-name="Noto Sans Saurashtra Regular" />
  <Font face-name="Noto Sans Shavian Regular" />
  <Font face-name="Noto Sans Sinhala Regular" />
  <Font face-name="Noto Sans Sundanese Regular" />
  <Font face-name="Noto Sans Symbols Regular" />
  <Font face-name="Noto Sans Syriac Eastern Regular" />
  <Font face-name="Noto Sans Syriac Estrangela Regular" />
  <Font face-name="Noto Sans Syriac Western Regular" />
  <Font face-name="Noto Sans Tagalog Regular" />
  <Font face-name="Noto Sans Tagbanwa Regular" />
  <Font face-name="Noto Sans Tai Le Regular" />
  <Font face-name="Noto Sans Tai Tham Regular" />
  <Font face-name="Noto Sans Tai Viet Regular" />
  <Font face-name="Noto Sans Tamil UI Regular" />
  <Font face-name="Noto Sans Telugu UI Regular" />
  <Font face-name="Noto Sans Thaana Regular" />
  <Font face-name="Noto Sans Thai UI Regular" />
  <Font face-name="Noto Sans Tibetan Regular" />
  <Font face-name="Noto Sans Tifinagh Regular" />
  <Font face-name="Noto Sans Vai Regular" />
  <Font face-name="Noto Sans Yi Regular" />
  <Font face-name="Noto Naskh Arabic UI Regular" />
  <Font face-name="DejaVu Sans Book" />
  <Font face-name="Droid Sans Fallback Regular" />
  <Font face-name="Unifont Medium" />
</FontSet>

<Style name="Guideposts">
  <Rule>
    <Filter>[name] != ''</Filter>
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


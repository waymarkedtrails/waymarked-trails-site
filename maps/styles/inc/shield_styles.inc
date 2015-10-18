<Style name="Shields">
  <Rule>
    <Filter>[numshields] = 1</Filter>
    <ShieldSymbolizer base="syms" file="[fname].png" placement="line" spacing="400" face-name="DejaVu Sans Mono Bold" label-position-tolerance="10" minimum-distance="8" minimum-path-length="60" avoid-edges="true" />
  </Rule>
  <Rule>
    <Filter>[numshields] = 2</Filter>
    <ShieldSymbolizer base="syms" file="[fname].png" placement="line" spacing="400" face-name="DejaVu Sans Mono Bold" label-position-tolerance="40" minimum-distance="8" minimum-path-length="60" avoid-edges="true" />
  </Rule>
  <Rule>
    <Filter>[numshields] = 3</Filter>
    <ShieldSymbolizer base="syms" file="[fname].png" placement="line" spacing="400" face-name="DejaVu Sans Mono Bold" label-position-tolerance="70" minimum-distance="8" minimum-path-length="60" avoid-edges="true" />
  </Rule>
  <Rule>
    <Filter>[numshields] = 4</Filter>
    <ShieldSymbolizer base="syms" file="[fname].png" placement="line" spacing="400" face-name="DejaVu Sans Mono Bold" label-position-tolerance="100" minimum-distance="8" minimum-path-length="60" avoid-edges="true" />
  </Rule>
  <Rule>
    <Filter>[numshields] = 5</Filter>
    <ShieldSymbolizer base="syms" file="[fname].png" placement="line" spacing="400" face-name="DejaVu Sans Mono Bold" label-position-tolerance="140" minimum-distance="8" minimum-path-length="60" avoid-edges="true" />
  </Rule>
</Style>

<Style name="ShieldsLowZoom">
  <Rule>
    <ShieldSymbolizer base="syms" file="[fname].png" placement="line" spacing="400" face-name="DejaVu Sans Mono Bold" label-position-tolerance="200" minimum-distance="30" horizontal-alignment="middle" vertical-alignment="middle" minimum-path-length="10" avoid-edges="true" />
  </Rule>
</Style>


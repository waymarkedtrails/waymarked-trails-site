<Style name="NodeNetworkLow">
  <Rule>
    <LineSymbolizer stroke="#cc1f0c" stroke-linecap="round" stroke-linejoin="round" stroke-width="1" />
  </Rule>
</Style>

<Style name="NodeNetworkMid">
  <Rule>
    <LineSymbolizer stroke="#cc1f0c" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.4" />
  </Rule>
</Style>

<Style name="NodeNetworkHigh">
  <Rule>
    <MinScaleDenominator>25000</MinScaleDenominator>
    <Filter>[iwn]</Filter>
    <LineSymbolizer stroke="#00ff00" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" />
    <LineSymbolizer stroke="#ff0000" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" />
  </Rule>
  <Rule>
    <MinScaleDenominator>25000</MinScaleDenominator>
    <Filter>not [iwn]</Filter>
    <LineSymbolizer stroke="#cc1f0c" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.6" />
  </Rule>
  <Rule>
    <MaxScaleDenominator>25000</MaxScaleDenominator>
    <LineSymbolizer stroke="#cc1f0c" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
  </Rule>
</Style>

<Style name="NetworkNodes">
  <Rule>
    <Filter>[len] > 1</Filter>
    <ShieldSymbolizer base="static" dy="-1" face-name="DejaVu Sans Condensed Bold" file="hikingnode.svg" transform="scale([len] 1)" vertical-alignment="middle" horizontal-alignment="middle" allow-overlap="true">[name]</ShieldSymbolizer>
  </Rule>
  <Rule>
    <ElseFilter/>
    <ShieldSymbolizer base="static" dy="-1" face-name="DejaVu Sans Condensed Bold" file="hikingnode.svg" vertical-alignment="middle" horizontal-alignment="middle" allow-overlap="true">[name]</ShieldSymbolizer>
  </Rule>
</Style>

<Layer maximum-scale-denominator="50000" name="NetworkNodes" buffer-size="64">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT name, 0.6 * length(name) as len, geom FROM &dbschema;.networknodes) as w</Parameter>
  </Datasource>
  <StyleName>NetworkNodes</StyleName>
</Layer>


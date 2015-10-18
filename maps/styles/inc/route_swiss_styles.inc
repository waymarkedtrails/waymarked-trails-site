<Style name="SwissWaysLow">
  <Rule>
    <LineSymbolizer stroke="#d30000" stroke-linecap="round" stroke-linejoin="round" />
  </Rule>
</Style>

<Style name="SwissWaysMid">
  <Rule>
    <Filter>[level] = 31</Filter>
    <LineSymbolizer stroke="#d30000" stroke-linecap="round" stroke-linejoin="round" />
  </Rule>
  <Rule>
    <Filter>[level] = 32</Filter>
    <LineSymbolizer stroke="#d30000" stroke-dasharray="6,3" stroke-linecap="round" stroke-linejoin="round" />
  </Rule>
  <Rule>
    <Filter>[level] = 33</Filter>
    <LineSymbolizer stroke="#d30000" stroke-dasharray="2,2" stroke-linecap="round" stroke-linejoin="round" />
  </Rule>
</Style>

<Style name="SwissWaysHigh">
  <Rule>
    <Filter>[level] = 31</Filter>
    <LineSymbolizer stroke="#d30000" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" />
  </Rule>
  <Rule>
    <Filter>[level] = 32</Filter>
    <LineSymbolizer stroke="#d30000" stroke-dasharray="6,3" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" />
  </Rule>
  <Rule>
    <Filter>[level] = 33</Filter>
    <LineSymbolizer stroke="#d30000" stroke-dasharray="1,6" stroke-linecap="round" stroke-linejoin="round" stroke-width="3.0" />
  </Rule>
</Style>


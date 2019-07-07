<Style name="level0-5">
  <Rule>
    <Filter>[level] &gt; 20</Filter>
    <LineSymbolizer stroke="#b20303" stroke-linecap="square" stroke-linejoin="round" stroke-width="1.3" />
  </Rule>
  <Rule>
    <ElseFilter />
    <LineSymbolizer stroke="#152eec" stroke-linecap="square" stroke-linejoin="bevel" />
  </Rule>
</Style>

<Style name="nwn6-8">
  <Rule>
    <LineSymbolizer stroke="#152eec" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.3" />
    <Filter>[noiwn]</Filter>
  </Rule>
  <Rule>
    <ElseFilter />
    <LineSymbolizer stroke="#b20303" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.0" />
  </Rule>
</Style>

<Style name="RWNWays9">
  <Rule>
    <LineSymbolizer stroke="#a76f0f" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" />
    <LineSymbolizer stroke="#ffa304" stroke-linecap="round" stroke-linejoin="round" />
    <Filter>[rwn] and not [nwn] and not [iwn]</Filter>
  </Rule>
</Style>

<Style name="IWNwithNWN">
  <Rule>
    <LineSymbolizer stroke="#b20303" stroke-linecap="square" stroke-linejoin="round" stroke-width="5.5" />
    <Filter>[nwn] and [iwn]</Filter>
  </Rule>
  <Rule>
    <LineSymbolizer stroke="#b20303" stroke-linecap="round" stroke-linejoin="round" stroke-width="4.0" />
    <Filter>[iwn] and not [nwn]</Filter>
  </Rule>
</Style>

<Style name="nwn9">
  <Rule>
    <LineSymbolizer stroke="#152eec" stroke-linecap="square" stroke-linejoin="round" stroke-width="3.0" />
    <Filter>[nwn]</Filter>
  </Rule>
</Style>

<Style name="iwn10">
  <Rule>
    <LineSymbolizer stroke="#b20303" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.0" />
    <Filter>[iwn] and ([rwn] or [nwn])</Filter>
  </Rule>
  <Rule>
    <LineSymbolizer stroke="#b20303" stroke-linecap="round" stroke-linejoin="round" stroke-width="5.0" />
    <Filter>[iwn] and not [rwn] and not [nwn]</Filter>
  </Rule>
</Style>

<Style name="nwn10">
  <Rule>
    <LineSymbolizer stroke="#152eec" stroke-linecap="round" stroke-linejoin="round" stroke-width="4.0" />
    <Filter>[nwn]</Filter>
  </Rule>
</Style>

<Style name="rwn10">
  <Rule>
    <Filter>[rwn] &gt;= 8 and not [nwn]</Filter>
    <LineSymbolizer stroke="#ffa304" stroke-linecap="round" stroke-linejoin="round" stroke-width="3.0" />
  </Rule>
  <Rule>
    <Filter>[rwn] &gt;= 8 and [nwn]</Filter>
    <LineSymbolizer stroke="#ffa304" stroke-dasharray="1,7" stroke-gamma="0.1" stroke-linecap="round" stroke-linejoin="round" stroke-width="3.0" />
    </Rule>
</Style>

<Style name="rwn10lower">
  <Rule>
    <Filter>[rwn] &gt; 0 and [rwn] &lt; 8 and not [nwn]</Filter>
    <LineSymbolizer stroke="#ffa304" stroke-linecap="round" stroke-linejoin="round" />
  </Rule>
</Style>


<Style name="lwn12">
  <Rule>
    <LineSymbolizer stroke="#7d31c6" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" />
    <Filter>[lwn]</Filter>
  </Rule>
</Style>

<Style name="rwn10-12">
  <Rule>
    <LineSymbolizer stroke="#ffa304" stroke-linecap="square" stroke-linejoin="round" />
  </Rule>
</Style>


<Style name="iwn12">
  <Rule>
    <LineSymbolizer stroke="#b20303" stroke-linecap="round" stroke-linejoin="round" stroke-width="6.0" />
    <Filter>[iwn] and [rwn] </Filter>
  </Rule>
  <Rule>
    <LineSymbolizer stroke="#b20303" stroke-linecap="round" stroke-linejoin="round" stroke-width="5.0" />
    <Filter>[iwn] and not [rwn] and not[nwn]</Filter>
  </Rule>
  <Rule>
    <Filter>[iwn] and [nwn]</Filter>
    <LineSymbolizer stroke="#e10404" stroke-linecap="round" stroke-linejoin="round" stroke-width="7.0" />
  </Rule>
</Style>

<Style name="nwn12">
  <Rule>
    <Filter>[nwn]</Filter>
    <LineSymbolizer stroke="#152eec" stroke-linecap="round" stroke-linejoin="round" stroke-width="4.0" />
  </Rule>
</Style>

<Style name="rwn12">
  <Rule>
    <Filter>[rwn] and not [nwn]</Filter>
    <LineSymbolizer stroke="#ffa304" stroke-linecap="round" stroke-linejoin="round" stroke-width="3.0" />
  </Rule>
  <Rule>
    <Filter>[rwn] and [nwn]</Filter>
    <LineSymbolizer stroke="#ffa304" stroke-dasharray="1,7" stroke-linecap="round" stroke-linejoin="round" stroke-width="3.0" />
  </Rule>
</Style>

<Style name="LWNHalo12">
  <Rule>
    <LineSymbolizer stroke="#c19ae6" stroke-linecap="round" stroke-linejoin="round" stroke-width="4.0" />
    </Rule>
</Style>

<Style name="iwnsmall">
  <Rule>
    <Filter>[iwn] and ([rwn] or [nwn])</Filter>
    <LineSymbolizer stroke="#b20303" stroke-linecap="round" stroke-linejoin="round" stroke-width="9.0" />
  </Rule>
  <Rule>
    <Filter>[iwn] and not ([rwn] or [nwn])</Filter>
    <LineSymbolizer stroke="#ae2929" stroke-linecap="round" stroke-linejoin="round" stroke-width="9.0" />
  </Rule>
</Style>

<Style name="nwnsmall">
  <Rule>
    <Filter>[nwn]</Filter>
    <LineSymbolizer stroke="#2b43f8" stroke-linecap="round" stroke-linejoin="round" stroke-width="6.0" />
    </Rule>
</Style>

<Style name="rwnsmall">
  <Rule>
    <Filter>[rwn] and not [nwn] and [lwn]</Filter>
    <LineSymbolizer stroke="#ffcc00" stroke-linecap="round" stroke-linejoin="round" stroke-width="6.0" />
  </Rule>
  <Rule>
    <Filter>[rwn] and not [nwn] and not [lwn]</Filter>
    <LineSymbolizer stroke="#fdb23a" stroke-linecap="round" stroke-linejoin="round" stroke-width="5.0" />
  </Rule>
  <Rule>
    <Filter>[rwn] and [nwn]</Filter>
    <LineSymbolizer stroke="#fdb23a" stroke-dasharray="2,10" stroke-linecap="round" stroke-linejoin="round" stroke-width="5.0" />
  </Rule>
</Style>

<Style name="rwnhalo">
  <Rule>
    <Filter>[rwn] and not [iwn] and not [nwn]</Filter>
    <LineSymbolizer stroke="#a76f0f" stroke-linecap="round" stroke-linejoin="round" stroke-opacity="0.5" stroke-width="6.0" />
  </Rule>
</Style>

<Style name="lwnsmall">
  <Rule>
    <Filter>[lwn] and not [iwn] and not [nwn] and not [rwn]</Filter>
    <LineSymbolizer stroke="#7d31c6" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" />
  </Rule>
  <Rule>
    <Filter>[lwn] and ([nwn] or [iwn] or [rwn])</Filter>
    <LineSymbolizer stroke="#af64f8" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.0" />
  </Rule>
</Style>

<Style name="lwnhalosmall">
  <Rule>
    <LineSymbolizer stroke="#565256" stroke-linecap="round" stroke-linejoin="round" stroke-opacity="0.5" stroke-width="4.0" />
    <Filter>[lwn]</Filter>
    <MaxScaleDenominator>50000</MaxScaleDenominator>
  </Rule>
</Style>


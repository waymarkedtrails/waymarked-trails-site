<Layer maximum-scale-denominator="5000000" minimum-scale-denominator="400000" name="IWNShieldOnly" buffer-size="512">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT geom, symbol as fname FROM &dbschema;.routes WHERE level between 21 and 28 and top and symbol !=  '' order by level desc) AS w</Parameter>
    </Datasource>
  <StyleName>ShieldsLowZoom</StyleName>
</Layer>

<Layer maximum-scale-denominator="1500000" minimum-scale-denominator="400000" name="NWNShieldOnly" buffer-size="512">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT geom, symbol as fname FROM &dbschema;.routes WHERE top and level between 14 and 20 and symbol != '' order by level desc) AS w</Parameter>
  </Datasource>
  <StyleName>ShieldsLowZoom</StyleName>
</Layer>


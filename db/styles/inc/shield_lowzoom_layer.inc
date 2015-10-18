<Layer maximum-scale-denominator="5000000" minimum-scale-denominator="400000" name="IWNShieldOnly" buffer-size="512">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT geom, symbol as fname FROM &dbschema;.routes WHERE level&lt;10 and top and symbol !=  '') AS w</Parameter>
    </Datasource>
  <StyleName>ShieldsLowZoom</StyleName>
</Layer>

<Layer maximum-scale-denominator="1500000" minimum-scale-denominator="400000" name="RWNShieldOnly" buffer-size="512">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT geom, symbol as fname FROM &dbschema;.routes WHERE top and level &gt;= 10 and level &lt; 20 and symbol != '') AS w</Parameter>
  </Datasource>
  <StyleName>ShieldsLowZoom</StyleName>
</Layer>


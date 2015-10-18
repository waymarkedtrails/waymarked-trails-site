<Layer maximum-scale-denominator="100000" name="AllShields1" buffer-size="10000">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT geom, allshields[1] as fname, array_length(allshields,1) as numshields FROM &dbschema;.defstyle where array_length(allshields,1) &gt; 0 order by st_npoints(geom100) desc) as w</Parameter>
    </Datasource>
  <StyleName>Shields</StyleName>
  </Layer>
<Layer maximum-scale-denominator="100000" name="AllShields2" buffer-size="10000">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT geom, allshields[2] as fname, array_length(allshields,1) as numshields FROM &dbschema;.defstyle where array_length(allshields,1) &gt; 1 order by st_npoints(geom100) desc) as w</Parameter>
    </Datasource>
  <StyleName>Shields</StyleName>
  </Layer>
<Layer maximum-scale-denominator="100000" name="AllShields3" buffer-size="10000">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT geom, allshields[3] as fname, array_length(allshields,1) as numshields FROM &dbschema;.defstyle where array_length(allshields,1) &gt; 2 order by st_npoints(geom100) desc) as w</Parameter>
    </Datasource>
  <StyleName>Shields</StyleName>
  </Layer>
<Layer maximum-scale-denominator="100000" name="AllShields4" buffer-size="10000">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT geom, allshields[4] as fname, array_length(allshields,1) as numshields FROM &dbschema;.defstyle where array_length(allshields,1) &gt; 3 order by st_npoints(geom100) desc) as w</Parameter>
    </Datasource>
  <StyleName>Shields</StyleName>
  </Layer>
<Layer maximum-scale-denominator="100000" name="AllShields5" buffer-size="10000">
  <Datasource base="psqlch">
    <Parameter name="table">(SELECT geom, allshields[5] as fname, array_length(allshields,1) as numshields FROM &dbschema;.defstyle where array_length(allshields,1) &gt; 4 order by st_npoints(geom100) desc) as w</Parameter>
    </Datasource>
  <StyleName>Shields</StyleName>
  </Layer>


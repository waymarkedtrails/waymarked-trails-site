.. subpage:: about Om kartet

Dette kartet viser merka sykkelruter rundt om i verden. Det er basert på data fra OpenStreetMap_ (OSM)-prosjektet. OSM er et verdsomspennende prosjekt for å lage og dele frie kartdata som alle som ønsker kan være med å bidra til. Dette betyr at sykkelkartet på ingen måte er komplett, men det betyr også at du kan være med ved å bidra ved å legge inn nye ruter eller rette feil i de eksisterende rutene. Se `Beginner's Guide`_ for å finne ut mer om OpenStreetMap.

Dette kartet består av et lag med sykkelruter. Det er laget med tanke på OpenStreetMap sitt Mapnik-kart som bakgrunnskart, men burde fungere med andre web-baserte kart som bakgrunn også. Vær snill å lese `bruksvilkår`_ før du bruker det på dine egne nettsider.

.. _OpenStreetMap: http://www.openstreetmap.org
.. _`Beginner's Guide`: http://wiki.openstreetmap.org/wiki/Beginners%27_Guide
.. _`bruksvilkår`: copyright

.. subpage:: rendering Framstilling av OSM-data

Sykkelruter bør legges inn i OSM som relasjonar. Hvordan dette fungerer er beskrevet på «`Cycle Routes`_»-sida på OSM-wikien. Dette kartet viser relasjonar som iallfall har følgende «tags»:

::

    type = route|superroute
    route = bicycle

Mountainbike (MTB)-ruter er framstilt på `MTB-kartet`_.

Klassifiseringa (og dermed fargelegginga av ruta på kartet) kommer av ``network``-taggen. Merket på ruta blir laga med utgangspunkt i ref-taggen. Dersom ref-taggen ikke finst, blir merket laga av de store bokstavene i «name»-taggen, og om det ikke lykkes, så av den første bokstaven i «name»-taggen.

Kartet støtter også «`relasjonshierarki`_».

.. _`Cycle Routes`: http://wiki.openstreetmap.org/wiki/Cycle_routes
.. _`localized rendering rules`: rendering/local_rules
.. _`osmc:symbol rendering rules`: rendering/osmc_symbol
.. _`relasjonshierarki`: rendering/hierarchies
.. _Guideposts: http://wiki.openstreetmap.org/wiki/Tag:information%3Dguidepost
.. _`MTB-kartet`: http://mtb.lonvia.de


.. subpage:: rendering/hierarchies Relasjonshierarki

Kartet støtter også relasjoner av relasjoner. Hovedbruken for dette på det nåværende tidspunkt er for å dele opp veldig lange ruter (f.eks. E1_) eller for å unngå dobbeltarbeid der flere ruter følger samme veg. Se for eksempel den sveitsiske `Via Francigena`_ som er del av den europeiske `Via Romea Francigena`_. I det første tilfellet er ikke delrelasjonene ruter i seg selv og blir derfor ikke vist på kartet.

Akkurat hvordan rutene blir vist på kartet avhenger av «network»-taggen:

  * Dersom en overrelasjon og en delrelasjon har samme network-tag så blir delrelasjonen tolka som en etappe i overrelasjonen. Dermed blir delrelasjonen bare vist som del av overrelasjonen, og ikke vist på kartet for seg selv.
  * Dersom network-taggen er ulik på overrelasjonen og delrelasjonen, så blir de tolka som selvstendige. Delrelasjonen går inn som del av overrelasjonen, men begge blir vist på kartet.

*Merknad:* du kan alltid se hva delrelasjoner som inngår i ein overrelasjon i rutelista. Velg overrelasjonen, så blir delrelasjonene vist i ei liste under den.

.. _E1: /route/European%20walking%20route%20E1
.. _`Via Francigena`: /route/Via%20Francigena,%20Swiss%20part
.. _`Via Romea Francigena`: /route/Via%20Romea%20Francigena

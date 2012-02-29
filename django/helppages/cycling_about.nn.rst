.. subpage:: about Om kartet

Dette kartet viser merka sykkelruter rundt om i verda. Det er basert på data frå OpenStreetMap_ (OSM)-prosjektet. OSM er eit verdsomspennande prosjekt for å laga og dela frie kartdata som alle som ynskjer kan vere med å bidra til. Dette betyr at kartet på ingen måte er komplett, men det betyr også at du kan vere med å bidra ved å leggje inn nye ruter eller rette feil i dei eksisterande rutene. Sjå `Beginner's guide`_ for å finne ut meir om OpenStreetMap.

Dette kartet består av eit lag med sykkelruter. Det er laga med tanke på OpenStreetMap sitt Mapnik-kart som bakgrunnskart, men burde fungere med andre web-baserte kart som bakgrunn også. Ver god å lesa `bruksvilkår`_ før du brukar det på dine eigne nettsider.

.. _OpenStreetMap: http://www.openstreetmap.org
.. _`Beginner's guide`: http://wiki.openstreetmap.org/wiki/Beginners%27_Guide
.. _`bruksvilkår`: copyright

.. subpage:: rendering Framstilling av OSM-data

Sykkelruter bør leggjast inn i OSM som relasjonar. Korleis dette fungerar er skildra på «`cycle routes`_»-sida på OSM-wikien. Dette kartet viser relasjonar som iallfall har følgjande «tags»:

::

    type = route|superroute
    route = bicycle

Mountainbike (MTB)-ruter er framstilt på `MTB-kartet`_.

Klassifiseringa (og dermed fargelegginga av ruta på kartet) kjem av ``network``-taggen. Merket på ruta blir laga med utgangspunkt i ref-taggen. Dersom ref-taggen ikkje finst, blir merket laga av dei store bokstavane i «name»-taggen, og om det ikkje lukkast, så av den første bokstaven i «name»-taggen.

Kartet støttar også «`relasjonshierarki`_».

.. _`cycle routes`: http://wiki.openstreetmap.org/wiki/Cycle_routes
.. _`relasjonshierarki`: rendering/hierarchies
.. _`MTB-kartet`: http://mtb.lonvia.de


.. subpage:: rendering/hierarchies Relasjonshierarki

Kartet støttar også relasjonar av relasjonar. Hovudbruken for dette på det noverande tidspunkt er for å dele opp veldig lange ruter (t.d. E1_) eller for å unngå dobbeltarbeid der fleire ruter følgjer same veg. Sjå til dømes den sveitsiske `Via Francigena`_ som er del av den europeiske `Via Romea Francigena`_. I det første tilfellet er ikkje del-relasjonane ruter i seg sjølv og blir difor ikkje viste på kartet.

Akkurat korleis rutene blir vist på kartet avheng av «network»-taggen:

  * Dersom ein overrelasjon og ein delrelasjon har same network-tag så blir delrelasjonen tolka som ein etappe i overrelasjonen. Dermed blir delrelasjonen berre vist som del av overrelasjonen, og ikkje vist på kartet for seg sjølv.
  * Dersom network-taggen er ulik på overrelasjonen og delrelasjonen, så blir dei tolka som sjølvstendige. Delrelasjonen går inn som del av overrelasjonen, men begge blir vist på kartet.

*Merknad:* du kan alltid sjå kva delrelasjonar som inngår i ein overrelasjon i rute-lista. Velg overrelasjonen, så blir delrelasjonane vist i ei liste under den.

.. _E1: /route/European%20walking%20route%20E1
.. _`Via Francigena`: /route/Via%20Francigena,%20Swiss%20part
.. _`Via Romea Francigena`: /route/Via%20Romea%20Francigena

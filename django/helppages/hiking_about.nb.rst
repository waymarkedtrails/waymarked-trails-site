.. subpage:: about Om kartet

Dette kartet viser merka vandreruter rundt om i verden. Det er basert på data fra OpenStreetMap_ (OSM)-prosjektet. OSM er et verdensomspennende prosjekt for å lage og dele frie kartdata som alle som ønsker kan være med å bidra til. Dette betyr at kartet på ingen måte er komplett, men det betyr også at du kan være med å bidra ved å legge inn nye ruter eller rette feil i de eksisterende rutene. Se `Beginner's Guide`_ for å finne ut mer om OpenStreetMap.

Dette kartet består av et lag med vandreruter. Det er laga med tanke på OpenStreetMap sitt Mapnik-kart som bakgrunnskart, men burde fungere med andre web-baserte kart som bakgrunn også. Vær snill å lese `bruksvilkår`_ før du bruker det på dine egne nettsider.

.. _OpenStreetMap: http://www.openstreetmap.org
.. _`Beginner's Guide`: http://wiki.openstreetmap.org/wiki/Beginners%27_Guide
.. _`bruksvilkår`: copyright

.. subpage:: rendering Framstilling av OSM-data

Vandreruter bør legges inn i OSM som relasjoner. Hvordan dette fungerer er beskrevet på «`Walking Routes`_»-sida på OSM-wikien. Dette kartet viser relasjoner som iallfall har følgende «tags»:

::

    type = route|superroute
    route = foot|walking|hiking


Hva verdi en velger for route-taggen gjør ingen forskjell. Klassifiseringa (og dermed fargelegginga av ruta på kartet) kommer av ``network``-taggen. Merket på ruta blir laga med følgende regler:

 1. Sjekk «`localized rendering rules`_».
 2. Prøv å tolke ``osmc:symbol``-taggen. For mer informasjon om hvordan denne taggen blir tolka, se `osmc:symbol rendering rules`_.
 3. Dersom ruta har en ``ref``-tag, så bruk den.
 4. Dersom ruta har en ``name``-tag, så lag et merke satt sammen av de store bokstavene i navnet, eller om det ikke lykkes så første bokstaven i navnet.
    *Til kartleggere: å lage merke av navnet på ruta er i grunnen bare en måte å få fram ruter med mangelfull informasjon. Prøv å få med nummer/merke/ID på ruta så sant det er mulig.*
 5. Gi opp. 

Kartet støtter også `relasjonshierarki`_.

For at vegvisere_ skal vises må de være tagga med følgende:

::

    tourism=information
    information=guidepost
    name=<navn>
    ele=<høyde>

Dersom både ``name`` og ``ele`` mangler så vil vegviseren visest uten navn og gråfarget.

.. _`Walking Routes`: http://wiki.openstreetmap.org/wiki/Walking_Routes
.. _`localized rendering rules`: rendering/local_rules
.. _`osmc:symbol rendering rules`: rendering/osmc_symbol
.. _`relasjonshierarki`: rendering/hierarchies
.. _vegvisere: http://wiki.openstreetmap.org/wiki/Tag:information%3Dguidepost


.. subpage:: rendering/hierarchies Relasjonshierarki

Kartet støtter også relasjoner av relasjoner. Hovedbruken for dette på det nåværende tidspunkt er for å dele opp veldig lange ruter (f.eks. E1_) eller for å unngå dobbeltarbeid der flere ruter følger samme veg. Se for eksempel den sveitsiske `Via Francigena`_ som er del av den europeiske `Via Romea Francigena`_. I det første tilfellet er ikke del-relasjonene ruter i seg selv og blir derfor ikke vist på kartet.

Akkurat hvordan rutene blir vist på kartet avhenger av «network»-taggen:

  * Dersom en overrelasjon og en delrelasjon har samme network-tag så blir delrelasjonen tolka som en etappe i overrelasjonen. Dermed blir delrelasjonen bare vist som del av overrelasjonen, og ikke vist på kartet for seg selv.
  * Dersom network-taggen er ulik på overrelasjonen og delrelasjonen, så blir de tolka som selvstendige. Delrelasjonen går inn som del av overrelasjonen, men begge blir vist på kartet.

*Merk:* du kan alltid se hva delrelasjoner som inngår i en overrelasjon i rute-lista. Velg overrelasjonen, så blir delrelasjonene vist i ei liste under den.

.. _E1: /route/European%20walking%20route%20E1
.. _`Via Francigena`: /route/Via%20Francigena,%20Swiss%20part
.. _`Via Romea Francigena`: /route/Via%20Romea%20Francigena

.. subpage:: rendering/osmc_symbol osmc:symbol-taggen

osmc:symbol-taggen er en måte å beskrive symbola av enkle geometriske figurer som blir brukt i enkelte europeiske land (spesielt Tyskland) på ein maskin-lesbar måte. Vandrekartet støtter et utvalg av symbola som er beskrevet på OpenStreetMap-wikien. For å bli brukt på vandrekartet må taggen ha følgende format:


::

  osmc:symbol=waycolor:background:foreground:text:textcolor

«Waycolor» må være med, men blir ignorert for dette kartet. «Foreground» kan ikke være tom og andre «foreground» er ikke støtta. «Text» og «textcolor» kan sløyfes. Se `liste over forgrunns- og bakgrunnssymbol som blir framstilt`_ for å være sikker på hva som kan brukes.

.. _`liste over forgrunns- og bakgrunnssymbol som blir framstilt`: ../osmc_symbol_legende

.. subpage:: rendering/local Tilpassa framstilling

Det finst mange ulike system for merking av vandreruter. Vi prøver å bruke de mest generelle taggene for å gi ei grei framstilling av kartet, men vil likevel ikke lykkes for enkelte system, særleg nettverk av vandreruter. For å få med disse systema skikkeleg på kartet, kan framstillinga tilpasses for områder der standard framstilling ikke er god nok.

I det følgende finner du en liste over områder som bruker spesielle kart-symbol. Les tipsa på slutten av sida for å få ditt eget område framstilt på en spesiell måte.

Sveits
======

Sveits har et stort nettverk av merka vandreruter over hele landet. Nettverket består av noder av navngitte vegvisere. Alle stiene er konsekvent merka med vanskelighetsgrad. Kartet viser disse stiene med rød farge med egne mønster for hver vanskelighetsgrad:

+----------+-----------------------------------------+------------------------------+
|På kartet | Beskrivelse                             | I OSM                        |
+==========+=========================================+==============================+
||routestd|| *Vandresti*, merka med |diamond|        | ``network=lwn``              |
|          |                                         |                              |
|          | Passer for alle.                        | ``osmc:symbol=yellow:[...]`` |
+----------+-----------------------------------------+------------------------------+
||routemnt|| *Fjellsti*, merka med |whitered|        | ``network=lwn``              |
|          |                                         |                              |
|          | Krever en viss grad av trening          | ``osmc:symbol=red:[...]``    |
|          | og balanse.                             |                              |
|          | Høydeskrekk kan være problematisk.      |                              |
+----------+-----------------------------------------+------------------------------+
||routealp|| *Alpin sti*, markert med |whiteblue|    | ``network=lwn``              |
|          |                                         |                              |
|          | Krever fjellklatreerfaring og           | ``osmc:symbol=blue:[...]``   |
|          | egnet utstyr.                           |                              |
+----------+-----------------------------------------+------------------------------+

Merk at oppå dette nettverket er det en mengde nasjonale og regionale ruter som blir vist på vanlig måte.

For mer informasjon om tagging av turstier i Sveits i OSM, se: `Swiss Hiking Network on the OSM Wiki`_.

Storbritannia og Nord-Irland
============================

Klassifiseringa av `UK long-distance paths`_ (de som er tagga med ``network=uk_ldp``) er avhengig av ``operator``-taggen. Relasjoner med ``operator=National Trails`` blir vist som nasjonale ruter, alle andre relasjoner blir vist som regionale ruter.

Relasjoner med ``network=lwn/rwn/nwn/iwn`` blir behandlet som vanlig.

Tsjekkia
========

Tsjekkia bruker en merkestandard med sju symbol og fire ulike farger. For beskrivelse, se `Czech tagging page`_ (på tsjekkisk).

Når en ``kct_*``-tag er brukt så får han forrang forann eventuell ``osmc:symbol``-tag. I tillegg blir ruta omklassifisert dersom ingen gyldig network-tag er brukt. Ruter med ``kct_red=major`` blir nasjonale ruter, andre ``kct_*=major``-tagga ruter blir klassifisert som regionale.

Merk: Symbola er vektor-grafikk laga av Radomir.cernoch, og kan finnast på OSM-wikien.

Slovakia
========

Slovakia bruker samme merkestandard som Tsjekkia, men tagginga er noe annerledes, se `Slovakian hiking page`_.

Alle ruter med taggen ``operator=KST`` er tagga i samsvar med det systemet. Siden ruter i Slovakia som regel inkluderer en gyldig network-tag, blir det ikke gjort noe omklassifisering.

Tyskland
========

Fränkischer Albverein
---------------------

Nettverket rundt Nuremberg er ganske tjukt, og regionale ruter tagga med ``operator=Fränkischer Albverein`` vises derfor på lavere zoom-nivå enn normalt.

.. |routestd|  image:: {{MEDIA_URL}}/img/route_std.png
.. |routemnt|  image:: {{MEDIA_URL}}/img/route_mnt.png
.. |routealp|  image:: {{MEDIA_URL}}/img/route_alp.png
.. |diamond|   image:: {{MEDIA_URL}}/img/yellow_diamond.png
.. |whitered|  image:: {{MEDIA_URL}}/img/white_red_white.png
.. |whiteblue| image:: {{MEDIA_URL}}/img/white_blue_white.png
.. _`Swiss Hiking Network on the OSM Wiki`: http://wiki.openstreetmap.org/wiki/EN:Switzerland/HikingNetwork
.. _`UK long-distance paths`: http://wiki.openstreetmap.org/wiki/WikiProject_United_Kingdom_Long_Distance_Paths
.. _`Czech tagging page`: http://wiki.openstreetmap.org/wiki/WikiProject_Czech_Republic/Editing_Standards_and_Conventions#Doporu.C4.8Den.C3.A9_typy_cest
.. _`Slovakian hiking page`: http://wiki.openstreetmap.org/wiki/WikiProject_Slovakia/Hiking_routes


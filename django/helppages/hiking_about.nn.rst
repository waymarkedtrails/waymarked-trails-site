.. subpage:: about Om kartet

Dette kartet viser merka vandreruter rundt om i verda. Det er basert på data frå OpenStreetMap_ (OSM)-prosjektet. OSM er eit verdsomspennande prosjekt for å laga og dela frie kartdata som alle som ynskjer kan vere med å bidra til. Dette betyr at kartet på ingen måte er komplett, men det betyr også at du kan vere med å bidra ved å leggje inn nye ruter eller rette feil i dei eksisterande rutene. Sjå `Beginner's Guide`_ for å finne ut meir om OpenStreetMap.

Dette kartet består av eit lag med vandreruter. Det er laga med tanke på OpenStreetMap sitt Mapnik-kart som bakgrunnskart, men burde fungere med andre web-baserte kart som bakgrunn også. Ver god å lesa `bruksvilkår`_ før du brukar det på dine eigne nettsider.

.. _OpenStreetMap: http://www.openstreetmap.org
.. _`Beginner's Guide`: http://wiki.openstreetmap.org/wiki/Beginners%27_Guide
.. _`bruksvilkår`: copyright

.. subpage:: rendering Framstilling av OSM-data

Vandreruter bør leggjast inn i OSM som relasjonar. Korleis dette fungerar er skildra på «`Walking Routes`_»-sida på OSM-wikien. Dette kartet viser relasjonar som iallfall har følgjande «tags»:

::

    type = route|superroute
    route = foot|walking|hiking


Kva verdi ein vel for route-taggen gjer ingen forskjell. Klassifiseringa (og dermed fargelegginga av ruta på kartet) kjem av ``network``-taggen. Merket på ruta blir laga med følgjande reglar:

 1. Sjekk «`localized rendering rules`_».
 2. Prøv å tolke ``osmc:symbol``-taggen. For meir informasjon om korleis denne taggen blir tolka, sjå `osmc:symbol rendering rules`_.
 3. Dersom ruta har ein ``ref``-tag, så bruk den.
 4. Dersom ruta har ein ``name``-tag, så lag merke sett saman av dei store bokstavane i namnet, eller om det ikkje lukkast så første bokstaven i namnet.
    *Til kartleggjarar: å lage merke av namnet på ruta er i grunn berre ein måte å få fram ruter med mangelfull informasjon. Prøv å få med nummer/merke/ID på ruta så sant det er mogleg.*
 5. Gje opp. 

Kartet støttar også `relasjonshierarki`_.

For at vegvisarar_ (/-skilt) skal visast må dei vera tagga med følgjande:

::

    tourism=information
    information=guidepost
    name=<namn>
    ele=<høgd>

Dersom både ``name`` og ``ele`` manglar så vil vegvisaren visast utan namn og gråfarga.

.. _`Walking Routes`: http://wiki.openstreetmap.org/wiki/Walking_Routes
.. _`localized rendering rules`: rendering/local_rules
.. _`osmc:symbol rendering rules`: rendering/osmc_symbol
.. _`relasjonshierarki`: rendering/hierarchies
.. _vegvisarar: http://wiki.openstreetmap.org/wiki/Tag:information%3Dguidepost


.. subpage:: rendering/hierarchies Relasjonshierarki

Kartet støttar også relasjonar av relasjonar. Hovudbruken for dette på det noverande tidspunkt er for å dele opp veldig lange ruter (t.d. E1_) eller for å unngå dobbeltarbeid der fleire ruter følgjer same veg. Sjå til dømes den sveitsiske `Via Francigena`_ som er del av den europeiske `Via Romea Francigena`_. I det første tilfellet er ikkje del-relasjonane ruter i seg sjølv og blir difor ikkje viste på kartet.

Akkurat korleis rutene blir vist på kartet avheng av «network»-taggen:

  * Dersom ein overrelasjon og ein delrelasjon har same network-tag så blir delrelasjonen tolka som ein etappe i overrelasjonen. Dermed blir delrelasjonen berre vist som del av overrelasjonen, og ikkje vist på kartet for seg sjølv.
  * Dersom network-taggen er ulik på overrelasjonen og delrelasjonen, så blir dei tolka som sjølvstendige. Delrelasjonen går inn som del av overrelasjonen, men begge blir vist på kartet.

*Merk:* du kan alltid sjå kva delrelasjonar som inngår i ein overrelasjon i rute-lista. Velg overrelasjonen, så blir delrelasjonane vist i ei liste under den.

.. _E1: /route/European%20walking%20route%20E1
.. _`Via Francigena`: /route/Via%20Francigena,%20Swiss%20part
.. _`Via Romea Francigena`: /route/Via%20Romea%20Francigena

.. subpage:: rendering/osmc_symbol osmc:symbol-taggen

osmc:symbol-taggen er ein måte å skildra symbola av enkle geometriske figurar som blir brukt i enkelte europeiske land (spesielt Tyskland) på ein maskin-lesbar måte. Vandrekartet støttar eit utval av symbola som er skildra på OpenStreetMap-wikien. For å bli brukt på vandrekartet må taggen ha følgjande format:


::

  osmc:symbol=waycolor:background:foreground:text:textcolor

«Waycolor» må vera med, men blir ignorert for dette kartet. «Foreground» kan ikkje vere tom og andre «foreground» er ikkje støtta. «Text» og «textcolor» kan sløyfast. Sjå `liste over framgrunns- og bakgrunnssymbol som blir framstilt`_ for å vere sikker på kva som kan brukast.

.. _`liste over framgrunns- og bakgrunnssymbol som blir framstilt`: ../osmc_symbol_legende

.. subpage:: rendering/local_rules Tilpassa framstilling

Det finst mange ulike system for merking av vandreruter. Vi freistar å nytte dei mest generelle taggane for å gje ei grei framstilling av kartet, men vil likevel ikkje lukkast for enkelte system, særleg nettverk av vandreruter. For å få med desse systema skikkeleg på kartet, kan framstillinga tilpassast for område der standard framstilling ikkje er god nok.

I det følgjande finn du ei liste over område som brukar spesielle kart-symbol. Les tipsa på slutten av sida for å få ditt eige område framstilt på ein spesiell måte.

Sveits
======

Sveits har eit stort nettverk av merka vandreruter over heile landet. Nettverket består av nodar av namngjevne vegvisarar. Alle stiane er konsekvent merka med vanskegrad. Kartet visar desse stiane med raud farge med eigne mønster for kvar vanskegrad:

+----------+-----------------------------------------+------------------------------+
|På kartet | Skildring                               | I OSM                        |
+==========+=========================================+==============================+
||routestd|| *Vandresti*, merka med |diamond|        | ``network=lwn``              |
|          |                                         |                              |
|          | Passar for alle.                        | ``osmc:symbol=yellow:[...]`` |
+----------+-----------------------------------------+------------------------------+
||routemnt|| *Fjellsti*, merka med |whitered|        | ``network=lwn``              |
|          |                                         |                              |
|          | Krev ein viss grad av trening           | ``osmc:symbol=red:[...]``    |
|          | og balanse.                             |                              |
|          | Høgdeskrekk kan vera problematisk.      |                              |
+----------+-----------------------------------------+------------------------------+
||routealp|| *Alpin sti*, markert med |whiteblue|    | ``network=lwn``              |
|          |                                         |                              |
|          | Krev fjellklatreerfaring og             | ``osmc:symbol=blue:[...]``   |
|          | eigna utstyr.                           |                              |
+----------+-----------------------------------------+------------------------------+

Merk at oppå dette nettverket er det ei mengd nasjonale og regionale ruter som blir vist på vanleg måte.

For meir informasjon om tagging av turstiar i Sveits i OSM, sjå: `Swiss Hiking Network on the OSM Wiki`_.

Storbritannia og Nord-Irland
============================

Klassifiseringa av `UK long-distance paths`_ (dei som er tagga med ``network=uk_ldp``) er avhengig av ``operator``-taggen. Relasjonar med ``operator=National Trails`` blir vist som nasjonale ruter, alle andre relasjonar blir vist som regionale ruter.

Relasjonar med ``network=lwn/rwn/nwn/iwn`` blir handsama som vanleg.

Tsjekkia
========

Tsjekkia brukar ein merkestandard med sju symbol og fire ulike fargar. For ei skildring, sjå `Czech tagging page`_ (på tsjekkisk).

Når ein ``kct_*``-tag er brukt så får han forrang føre eventuell ``osmc:symbol``-tag. I tillegg så blir ruta omklassifisert dersom ingen gyldig network-tag er brukt. Ruter med ``kct_red=major`` blir nasjonale ruter, andre ``kct_*=major``-tagga ruter blir klassifisert som regionale.

Merk: Symbola er vektor-grafikk laga av Radomir.cernoch, og kan finnast på OSM-wikien.

Slovakia
========

Slovakia brukar same merkestandard som Tsjekkia, men tagginga er noko annleis, sjå `Slovakian hiking page`_.

Alle ruter med taggen ``operator=KST`` er tagga i samsvar med det systemet. Sidan ruter i Slovakia som regel inkludera ein gyldig network-tag, blir det ikkje gjort noko omklassifisering.

Tyskland
========

Fränkischer Albverein
---------------------

Nettverket rundt Nuremberg er ganske tjukt, og regionale ruter tagga med ``operator=Fränkischer Albverein`` visest difor på lågare zoom-nivå enn normalt.

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


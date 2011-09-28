.. subpage:: about Über die Karte

Diese Karte zeigt eine Übersicht markierter Wanderwege rund um den Erdball. Die Daten stammen vom OpenStreetMap_-Projekt. OSM ist eine von jedem veränderbare Weltkarte, an der eine Reihe Freiwillige arbeiten. Das bedeutet, dass die Daten (noch) nicht vollständig sind, aber es bedeutet auch, dass jeder dabei helfen kann, neue Routen einzutragen oder bestehende zu korrigieren. Mehr über OpenStreetMap und wie man beitragen kann, finden sich im `Beginner's Guide`_.

Die Karte auf dieser Seite stellt nur ein Overlay mit Wanderwegen zur Verfügung, sie benötigt also noch eine Basiskarte als Grundlage. Der Overlay wurde vor allem für die OSM Mapnik-Karte als Basiskarte entwickelt, sollte aber auch mit anderen Online-Karten zusammen funktionieren. Vor der Verwendung auf anderen Seiten sollten jedoch unbedingt die Nutzungsbedingungen_ gelesen werden.

.. _OpenStreetMap: http://www.openstreetmap.org
.. _`Beginner's Guide`: http://wiki.openstreetmap.org/wiki/DE:Beginners_Guide
.. _Nutzungsbedingungen: copyright

.. subpage:: rendering Darstellung der OSM-Daten

Wanderrouten in OSM sollten als Relationen eingetragen werden. Wie das genau funktioniert wird im Detail im Abschnitt Wanderwege_ im OSM-Wiki beschrieben. Auf dieser Karte werden alle Relationen dargestellt, die wenigstens folgende Tags haben:

::

    type = route|superroute
    route = foot|walking|hiking


Welcher Routentyp verwendet wird, spielt keine Rolle.

Die Klassifizierung der Routen (und damit in welcher Farbe und auf welchen Zoomstufen sie dargestellt werden) hängt vom ``network``-Tag ab. Das Symbol wird von den Tags abgeleitet und zwar werden Regeln in dieser Reihenfolge angewendet:

 1. `lokale Darstellungsregeln`_ anwenden.
 2. Auswerten des ``osmc:symbol``-Tags. Details darüber, welches Format erwartet wird, finden sich im Abschnitt `osmc:symbol-Renderregeln`_.
 3. Existiert ein ``ref``-Tag, wird ein Text-Label mit diesem Tag erzeugt.
 4. Existiert ein ``name``-Tag, wird eine Referenz daraus abgeleitet. Dabei wird erst versucht, aus den Grossbuchstaben im Namen eine passende Abkürzung zu erstellen und wenn das nicht funktioniert einfach der Anfang des Namens verwendet.
 5. Aufgeben. 

Die Karte unterstützt auch `verschachtelte Relationen`_.

Wegweiser_ müssen wie folgt getaggt sein:

::

    tourism=information
    information=guidepost
    name=<name>
    ele=<altitude>

``name`` und ``ele`` sind optional. Sollten beide fehlen, wird der Wegweiser als unbenannt gekennzeichnet und taucht in der Karte in grau auf.

.. _Wanderwege: http://wiki.openstreetmap.org/wiki/DE:Wanderweg
.. _`lokale Darstellungsregeln`: rendering/local_rules
.. _`osmc:symbol-Renderregeln`: rendering/osmc_symbol
.. _`verschachtelte Relationen`: rendering/hierarchies
.. _Wegweiser: http://wiki.openstreetmap.org/wiki/Tag:information%3Dguidepost


.. subpage:: rendering/hierarchies Verschachtelte Relationen

Die Karte unterstützt auch Relationshierarchien, also Relationen, die andere Relationen enthalten. Im Augenblick gibt es zwei Hauptanwendungen für Hierarchien bei Wanderwegen in OSM: Zum einen werden sie verwendet, um sehr grosse Relationen in kleinere aufzuspalten (zum Beispiel der E1_) und zum anderen werden sie benutzt, um mehrfache Arbeit zu sparen, wenn zwei oder mehr Routen die gleiche Strecke benutzen (siehe zum Beispiel die Schweizer `Via Francigena`_ die Teil der Europäischen `Via Romea Francigena`_ ist). Im ersten Fall sollten die Teilstrecken nicht extra auf der Karte erscheinen, im zweiten Fall schon.

Wie genau eine Unterrelation behandelt wird, hängt von ``network``-Tag ab:

  * Haben Eltern- und Kindrelation das gleiche ``network``-Tag, wird angenommen, dass es sich bei der Kindrelation nur um eine Etappe handelt. Daher werden die Wege in der Relation zur Elternrelation dazugefügt und die Kindrelation erscheint nicht in der Karte.

  * Haben Eltern- und Kindrelation unterschiedliche ``network``-Tags, werden sie als selbständig betrachtet und beide auf dem Weg, den sie Teilen, dargestellt.

*Hinweis:* es ist immer möglich, Kindrelationen mit Hilfe des Routebrowsers zu finden und zu markieren. Dazu einfach im Browser die Elternrelation anwählen und dann erscheint eine anwählbare Liste der enthaltenen Relationen.

.. _E1: /de/route/European%20walking%20route%20E1
.. _`Via Francigena`: /de/route/Via%20Francigena,%20Swiss%20part
.. _`Via Romea Francigena`: /de/route/Via%20Romea%20Francigena

.. subpage:: rendering/osmc_symbol osmc:symbol-Tag

Das ``osmc:symbol``-Tag erlaubt, Wanderwegmarkierungen, die aus einfachen geometrischen Formen bestehen, in maschinenlesbarer Art und Weise zu beschreiben. Die Wanderkarte unterstützt einen Teil des auf der Wiki-Seite beschriebenen Formats. Um auf der Karte angezeigt zu werden, muss das Tag folgendes Format haben:

::

  osmc:symbol=waycolor:background:foreground:text:textcolor

``waycolor`` muss vorhanden sein, wird aber von der Karte ignoriert. ``foreground`` darf nicht leer sein, ein zweiter Vordergrund wird nicht unterstützt. ``text`` und ``textcolor`` können komplett weggelassen werden. Es gibt eine `Liste von unterstützten Vorder- und Hintergrundwerten`_.

*Hinweis:* die ältere Version der Karte hat auch Tags mit leerem ``foreground`` unterstützt. Um das Bild der Karte ein wenig einheitlicher zu gestalten, werden solche Tags jetzt als normale Text-Labels gerendert. Ausnahmen können eingebaut werden.

.. _`Liste von unterstützten Vorder- und Hintergrundwerten`: ../osmc_symbol_legende

.. subpage:: rendering/local Regionale Besonderheiten

Es gibt viele verschieden Systeme auf der Welt, wie Wanderwege angelegt und markiert werden. Die Karte versucht eine möglichst allgemeingültige Darstellung für alle Systeme zu finden, aber das kann natürlich nicht immer gutgehen. Besonders wo statt einzelner Wanderrouten komplexe Wegenetzwerke existieren, ist die Darstellung nicht immer ideal. Um auch solche und andere exotische Systeme darstellen zu können, kann die Karte den lokalen Gegebenheiten angepasst werden.

Im Folgenden sind die Regionen aufgelistet, für die gesonderte Darstellungsregeln gelten.

Schweiz
=======

Die Schweiz besitzt ein ausgedehntes Netzwerk von markierten Wanderwegen, dass das ganze Land erschliesst. Es handelt sich dabei um ein Knotennetzwerk, wo benannte Wegweiser die Knoten bilden. Die Wege sind konsistent mit den gleichen Symbolen markiert, die zugleich die Schwierigkeit des Weges anzeigen. Auf der Karte erscheinen alle diese Wege in Rot mit unterschiedlichem Linienmuster je nach Schwierigkeitsstufe:

+----------+-----------------------------------------+------------------------------+
|Karte     | Beschreibung                            | In OSM                       |
+==========+=========================================+==============================+
||routestd|| *Wanderweg*, markiert als |diamond|     | ``network=lwn``              |
|          |                                         |                              |
|          | Geeignet für jedermann.                 | ``osmc:symbol=yellow:[...]`` |
+----------+-----------------------------------------+------------------------------+
||routemnt|| *Bergpfad*, markiert als |whitered|     | ``network=lwn``              |
|          |                                         |                              |
|          | Schwindelfreiheit und Trittsicherheit   | ``osmc:symbol=red:[...]``    |
|          | sowie ein ausreichendes Mass an Fitness |                              |
|          | werden vorausgesetzt.                   |                              |
+----------+-----------------------------------------+------------------------------+
||routealp|| *Alpiner Weg*, markiert als |whiteblue| | ``network=lwn``              |
|          |                                         |                              |
|          | Alpine Erfahurng sowie angepasste       | ``osmc:symbol=blue:[...]``   |
|          | Ausrüstung sind unabdingbar.            |                              |
+----------+-----------------------------------------+------------------------------+

Zusätzlich zu diesem lokalen Wegenetz gibt es noch regionale und nationale Wanderrouten, die wie üblich angezeigt werden.

Mehr Informationen zum Tagging Schweizer Wanderwege findet sich im OSM Wiki unter `Swiss Hiking Network`_.

Grossbritanien
==============

Die Darstellung der ``britischen Weitwanderwege`` (also diejenigen, die mit ``network=uk_ldp`` getaggt sind) hängt vom ``operator``-Tag ab. Alle Relationen mit ``operator=National Trails`` werden als nationale Routen gezeichnet, alle anderen als regionale Routen.

Routen mit ``network=lwn/rwn/nwn/iwn`` werden wie üblich dargestellt.


Tschechien
==========

Das Land benutzt ein System von Markierungen, dass auf 7 Standardsymbolen in 4 verschiedenen Farben beruht. Eine Beschreibung findet sich auf der `tschechischen Tagging-Seite`_ (nur in Tschechisch).

Wenn Routen ein ``kct_*`` haben, wird dieses dem ``osmc:symbol``-Tag vorgezogen. Ausserdem werden Routen, die kein gültiges network-Tag haben, nach diesem Tag klassifiziert: ``kct_red=major``-Routen werden zu nationalen und andere ``kct_*=major``-Routen zu regionalen Routen.

Anmerkung: Die Symbole wurden von den Vektorgrafiken von Radomir.cernoch abgeleitet, die im OSM-Wiki zu finden sind.


Slovakei
========

Die Slowakei benutzt das gleiche Markierungsschema für Wanderwege wie die Tschechei, jedoch unterscheidet sich das Tagging leicht. Details finden sich auf der `Slowakischen Seite für Wanderrouten`_.

Alle Routen, die ein ``operator=KST``-Tag haben, werden nach diesem Schema ausgewertet. Da slowakische Routen ein gültiges ``network``-Tag besitzen sollten, werden die Routen nicht neu klassifiziert.

Deutschland
===========

Fränkischer Albverein
---------------------

Da das Netzwerk rund um Nürnberg sehr dicht ist, werden die regionalen Routen dieses Vereins (``operator=Fränkischer Albverein``) erst in höheren Zoomleveln als andere regionale Routen dargestellt.

.. |routestd|  image:: /media/static/img/route_std.png
.. |routemnt|  image:: /media/static/img/route_mnt.png
.. |routealp|  image:: /media/static/img/route_alp.png
.. |diamond|   image:: /media/static/img/yellow_diamond.png
.. |whitered|  image:: /media/static/img/white_red_white.png
.. |whiteblue| image:: /media/static/img/white_blue_white.png
.. _`Swiss Hiking Network`: http://wiki.openstreetmap.org/wiki/DE:Switzerland/HikingNetwork
.. _`britischen Weitwanderwege`: http://wiki.openstreetmap.org/wiki/WikiProject_United_Kingdom_Long_Distance_Paths
.. _`tschechischen Tagging-Seite`: http://wiki.openstreetmap.org/wiki/WikiProject_Czech_Republic/Editing_Standards_and_Conventions#Doporu.C4.8Den.C3.A9_typy_cest
.. _`Slowakischen Seite für Wanderrouten`: http://wiki.openstreetmap.org/wiki/WikiProject_Slovakia/Hiking_routes



.. subpage:: technical Technische Details


Die Wanderwege auf der Karte werden einmal täglich aktualisiert. Das Datum des letzten Updates ist in der oberen linken Ecke ersichtlich. Normalerweise werden alle Beiträge bis 1 Uhr morgens des betreffenden Tages berücksichtigt. (Diese Seite hat keinen Einfluss darauf, wie häufig die darunterliegende Mapnik-Basiskarte aktualisiert wird. Je nach dem wie beschäftigt der Server ist, kann das zwischen wenigen Minuten und einer Woche dauern.)

Der Server läuft auf einem gewöhnlichen Debian Linux und benutzt eine Toolchain aus osmosis_, Postgresql_ und Mapnik_, um die Karte zu rendern. Mit Hilfe von osgene werden die Daten vor dem Rendern vorverarbeitet. Die Webseite basiert auf dem `Django Web-Framework`_. Mehr Informationen dazu auf den Entwicklerseiten_.

.. _osmosis: http://wiki.openstreetmap.org/wiki/Osmosis
.. _Postgresql: http://www.postgresql.org/
.. _Mapnik: http://www.mapnik.org/
.. _`Django Web-Framework`: https://www.djangoproject.com/
.. _`Entwicklerseiten`: http://dev.lonvia.de/trac

.. subpage:: copyright Copyright

Das Wanderwege-Overlay und die GPX-Tracks stehen unter einer `Creative Commons Attribution-Share Alike 3.0 Germany Lizenz`_. Sie dürfen also weiterverwendet und verändert werden, solange das entstehende Werk wiederum unter einer kompatiblen Lizenz steht und sowohl OpenStreetMap als auch diese Seite als Ursprung erwähnt werden.

Nutzungsbedingungen
-------------------

Das Overlay kann in andere Webseiten eingebunden werden, solange die Zugriffsraten moderat sind. Die Tiles sollten so oft wie möglich gecacht werden und der Referer muss korrekt gesetzt sein. Massen-Download von Kartenteilen ist nicht gerne gesehen.

Die GPX-Dateien werden ausschliesslich für Besucher dieser Seite zur Verfügung gestellt. Automatische Downloads oder direkte Links von anderen Seiten werden nicht toleriert.

.. _`Creative Commons Attribution-Share Alike 3.0 Germany Lizenz`: http://creativecommons.org/licenses/by-sa/3.0/de/deed.de

.. subpage:: acknowledgements Danksagungen

Die Kartendaten stammen aus dem OpenStreetMap-Projekt und stehen unter einer `CC-by-SA 2.0 Lizenz`_.

Das Overlay mit dem Höhenprofil wird freundlicherweise von der `Hike & Bike Map`_ zur Verfügung gestellt. Die Karte ist immer einen Besuch wert. Die Daten basieren auf den frei verfügbaren SRTM3 v2-Daten der NASA.

Dank geht auch an Yves Cainaud für die französische Übersetzung, an Oscar Formaggi für die italienische Übersetzung und an partim_ für die grosszügige Unterstützung des Servers.

.. _`CC-by-SA 2.0 Lizenz`: http://creativecommons.org/licenses/by-sa/2.0/deed.de
.. _`Hike & Bike Map`: http://hikebikemap.de/
.. _partim: http://www.partim.de


.. subpage:: contact Kontakt

Fragen und Kommentare können an `lonvia@denofr.de`_ gesendet werden.

Haftungsausschluss
------------------

Es kann weder für die Richtigkeit noch die Vollständigkeit der Karte eine Garantie übernommen werden. Wanderungen sollten nie ohne eine gute Papierkarte und der entsprechenden Ausrüstung unternommen werden. Wer diesem Rat nicht folgt und sich verirrt, ist auf sich selbst gestellt.

Diese Seite enthält Links zu externen Webseiten für deren Inhalt der Autor dieser Webseite keine Kontrolle hat und daher keine Verantwortung übernehmen kann.

.. _`lonvia@denofr.de`: mailto:lonvia@denofr.de

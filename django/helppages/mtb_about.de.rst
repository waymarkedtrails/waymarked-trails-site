.. subpage:: about Über die Karte

Diese Karte zeigt eine Übersicht markierter Mountainbike-Routen rund um den Erdball. Die Daten stammen vom OpenStreetMap_-Projekt. OSM ist eine von jedem veränderbare Weltkarte, an der eine Reihe Freiwillige arbeiten. Das bedeutet, dass die Daten (noch) nicht vollständig sind, aber es bedeutet auch, dass jeder dabei helfen kann, neue Routen einzutragen oder bestehende zu korrigieren. Mehr über OpenStreetMap und wie man beitragen kann, finden sich im `Beginner's Guide`_.

Die Karte auf dieser Seite stellt nur ein Overlay mit Radwegen zur Verfügung, sie benötigt also noch eine Basiskarte als Grundlage. Der Overlay wurde vor allem für die OSM Mapnik-Karte als Basiskarte entwickelt, sollte aber auch mit anderen Online-Karten zusammen funktionieren. Vor der Verwendung auf anderen Seiten sollten jedoch unbedingt die Nutzungsbedingungen_ gelesen werden.

.. _OpenStreetMap: http://www.openstreetmap.org
.. _`Beginner's Guide`: http://wiki.openstreetmap.org/wiki/DE:Beginners_Guide
.. _Nutzungsbedingungen: copyright

.. subpage:: rendering Darstellung der OSM-Daten

Fahrradrouten in OSM sollten als Relationen eingetragen werden. Wie das genau funktioniert wird im Detail im Abschnitt Fahrradrouten_ im OSM-Wiki beschrieben. Auf dieser Karte werden alle Relationen dargestellt, die wenigstens folgende Tags haben:

::

    type = route|superroute
    route = mtb


Routen für normale Fahrräder werden auf einer separaten `Karte für Radrouten`_ angezeigt.

Die Klassifizierung der Routen (und damit in welcher Farbe und auf welchen Zoomstufen sie dargestellt werden) hängt vom ``network``-Tag ab. Das Symbol wird von den Tags abgeleitet und zwar werden Regeln in dieser Reihenfolge angewendet:

 1. Existiert ein ``ref``-Tag, wird ein Text-Label mit diesem Tag erzeugt.
 2. Existiert ein ``name``-Tag, wird eine Referenz daraus abgeleitet. Dabei wird erst versucht, aus den Grossbuchstaben im Namen eine passende Abkürzung zu erstellen und wenn das nicht funktioniert einfach der Anfang des Namens verwendet.
 3. Aufgeben. 

Die Karte unterstützt auch `verschachtelte Relationen`_.

.. _`Karte für Radrouten`: http://cycling.loniva.de/de
.. _Fahrradrouten: http://wiki.openstreetmap.org/wiki/Fahrradroutentagging_Deutschland
.. _`lokale Darstellungsregeln`: rendering/local_rules
.. _`osmc:symbol-Renderregeln`: rendering/osmc_symbol
.. _`verschachtelte Relationen`: rendering/hierarchies


.. subpage:: rendering/hierarchies Verschachtelte Relationen

Die Karte unterstützt auch Relationshierarchien, also Relationen, die andere Relationen enthalten. Im Augenblick gibt es zwei Hauptanwendungen für Hierarchien bei Wanderwegen in OSM: Zum einen werden sie verwendet, um sehr grosse Relationen in kleinere aufzuspalten (zum Beispiel der E1_) und zum anderen werden sie benutzt, um mehrfache Arbeit zu sparen, wenn zwei oder mehr Routen die gleiche Strecke benutzen (siehe zum Beispiel die Schweizer `Via Francigena`_ die Teil der Europäischen `Via Romea Francigena`_ ist). Im ersten Fall sollten die Teilstrecken nicht extra auf der Karte erscheinen, im zweiten Fall schon.

Wie genau eine Unterrelation behandelt wird, hängt von ``network``-Tag ab:

  * Haben Eltern- und Kindrelation das gleiche ``network``-Tag, wird angenommen, dass es sich bei der Kindrelation nur um eine Etappe handelt. Daher werden die Wege in der Relation zur Elternrelation dazugefügt und die Kindrelation erscheint nicht in der Karte.

  * Haben Eltern- und Kindrelation unterschiedliche ``network``-Tags, werden sie als selbständig betrachtet und beide auf dem Weg, den sie Teilen, dargestellt.

*Hinweis:* es ist immer möglich, Kindrelationen mit Hilfe des Routebrowsers zu finden und zu markieren. Dazu einfach im Browser die Elternrelation anwählen und dann erscheint eine anwählbare Liste der enthaltenen Relationen.

.. _E1: /de/route/European%20walking%20route%20E1
.. _`Via Francigena`: /de/route/Via%20Francigena,%20Swiss%20part
.. _`Via Romea Francigena`: /de/route/Via%20Romea%20Francigena


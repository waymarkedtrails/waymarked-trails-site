.. subpage:: about Über die Karte

Diese Karte zeigt eine Übersicht markierter Radrouten rund um den Erdball. Die Daten stammen vom OpenStreetMap_-Projekt. OSM ist eine von jedem veränderbare Weltkarte, an der eine Reihe Freiwillige arbeiten. Das bedeutet, dass die Daten (noch) nicht vollständig sind, aber es bedeutet auch, dass jeder dabei helfen kann, neue Routen einzutragen oder bestehende zu korrigieren. Mehr über OpenStreetMap und wie man beitragen kann, finden sich im `Beginner's Guide`_.

Die Karte auf dieser Seite stellt nur ein Overlay mit Radwegen zur Verfügung, sie benötigt also noch eine Basiskarte als Grundlage. Der Overlay wurde vor allem für die OSM Mapnik-Karte als Basiskarte entwickelt, sollte aber auch mit anderen Online-Karten zusammen funktionieren. Vor der Verwendung auf anderen Seiten sollten jedoch unbedingt die Nutzungsbedingungen_ gelesen werden.

.. _OpenStreetMap: http://www.openstreetmap.org
.. _`Beginner's Guide`: http://wiki.openstreetmap.org/wiki/DE:Beginners_Guide
.. _Nutzungsbedingungen: copyright

.. subpage:: rendering Darstellung der OSM-Daten

Fahrradrouten in OSM sollten als Relationen eingetragen werden. Wie das genau funktioniert wird im Detail im Abschnitt Fahrradrouten_ im OSM-Wiki beschrieben. Auf dieser Karte werden alle Relationen dargestellt, die wenigstens folgende Tags haben:

::

    type = route|superroute
    route = bicycle


MTB-Routen werden zur Zeit noch nicht angezeigt.

Die Klassifizierung der Routen (und damit in welcher Farbe und auf welchen Zoomstufen sie dargestellt werden) hängt vom ``network``-Tag ab. Das Symbol wird von den Tags abgeleitet und zwar werden Regeln in dieser Reihenfolge angewendet:

 1. Existiert ein ``ref``-Tag, wird ein Text-Label mit diesem Tag erzeugt.
 2. Existiert ein ``name``-Tag, wird eine Referenz daraus abgeleitet. Dabei wird erst versucht, aus den Grossbuchstaben im Namen eine passende Abkürzung zu erstellen und wenn das nicht funktioniert einfach der Anfang des Namens verwendet.
    *Hinweis an Mapper: diese Heuristik ist keine allgemein akzeptierte Vorgehensweise, sondern ein Hack auf dieser Seite, um ein Label für möglichst viele Routen zu erhalten. Um auch Kompatibilität mit anderen Anwendungen zu gewährleisten, sollte möglichst immer ein Referenz-Tag hinzugefügt werden.*  
 3. Aufgeben. 

Die Karte unterstützt auch `verschachtelte Relationen`_.

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


.. subpage:: technical Technische Details


Die Radrouten auf der Karte werden einmal täglich aktualisiert. Das Datum des letzten Updates ist in der oberen linken Ecke ersichtlich. Normalerweise werden alle Beiträge bis 1 Uhr morgens des betreffenden Tages berücksichtigt. (Diese Seite hat keinen Einfluss darauf, wie häufig die darunterliegende Mapnik-Basiskarte aktualisiert wird. Je nach dem wie beschäftigt der Server ist, kann das zwischen wenigen Minuten und einer Woche dauern.)

Der Server läuft auf einem gewöhnlichen Debian Linux und benutzt eine Toolchain aus osmosis_, Postgresql_ und Mapnik_, um die Karte zu rendern. Mit Hilfe von osgene werden die Daten vor dem Rendern vorverarbeitet. Die Webseite basiert auf dem `Django Web-Framework`_. Mehr Informationen dazu sowie der Source-Code findet sich auf den Entwicklerseiten_.

.. _osmosis: http://wiki.openstreetmap.org/wiki/Osmosis
.. _Postgresql: http://www.postgresql.org/
.. _Mapnik: http://www.mapnik.org/
.. _`Django Web-Framework`: https://www.djangoproject.com/
.. _`Entwicklerseiten`: http://dev.lonvia.de/trac

.. subpage:: copyright Copyright

Das Radrouten-Overlay und die GPX-Tracks stehen unter einer `Creative Commons Attribution-Share Alike 3.0 Germany Lizenz`_. Sie dürfen also weiterverwendet und verändert werden, solange das entstehende Werk wiederum unter einer kompatiblen Lizenz steht und sowohl OpenStreetMap als auch diese Seite als Ursprung erwähnt werden.

Nutzungsbedingungen
-------------------

Das Overlay kann in andere Webseiten eingebunden werden, solange die Zugriffsraten moderat sind. Die Tiles sollten so oft wie möglich gecacht werden und der Referer muss korrekt gesetzt sein. Massen-Download von Kartenteilen ist nicht gerne gesehen.

.. _`Creative Commons Attribution-Share Alike 3.0 Germany Lizenz`: http://creativecommons.org/licenses/by-sa/3.0/de/deed.de

.. subpage:: acknowledgements Danksagungen

Die Kartendaten stammen aus dem OpenStreetMap-Projekt und stehen unter einer `CC-by-SA 2.0 Lizenz`_.

Das Overlay mit dem Höhenprofil wird freundlicherweise von der `Hike & Bike Map`_ zur Verfügung gestellt. Die Karte ist immer einen Besuch wert. Die Daten basieren auf den frei verfügbaren SRTM3 v2-Daten der NASA.

Dank geht auch an Yves Cainaud für die französische Übersetzung, an Oscar Formaggi für die italienische Übersetzung und an partim_ für die grosszügige Unterstützung des Servers.

.. _`CC-by-SA 2.0 Lizenz`: http://creativecommons.org/licenses/by-sa/2.0/deed.de
.. _`Hike & Bike Map`: http://hikebikemap.de/
.. _partim: http://www.partim.de


.. subpage:: contact Kontakt und Impressum

Fragen und Kommentare können an `lonvia@denofr.de`_ gesendet werden.

Haftungsausschluss
------------------

Es kann weder für die Richtigkeit noch die Vollständigkeit der Karte eine Garantie übernommen werden. Wanderungen sollten nie ohne eine gute Papierkarte und der entsprechenden Ausrüstung unternommen werden. Wer diesem Rat nicht folgt und sich verirrt, ist auf sich selbst gestellt.

Diese Seite enthält Links zu externen Webseiten für deren Inhalt der Autor dieser Webseite keine Kontrolle hat und daher keine Verantwortung übernehmen kann.

Impressum
---------

Diese Seite wird betrieben von:

Sarah Hoffmann
Rigistr. 42
8006 Zürich
Schweiz
`lonvia@denofr.de`_

.. _`lonvia@denofr.de`: mailto:lonvia@denofr.de

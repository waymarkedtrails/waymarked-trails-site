.. subpage:: technical Technische Details


Die Wanderwege auf der Karte werden einmal täglich aktualisiert. Das Datum des letzten Updates ist in der oberen linken Ecke ersichtlich. Normalerweise werden alle Beiträge bis 1 Uhr morgens des betreffenden Tages berücksichtigt. (Diese Seite hat keinen Einfluss darauf, wie häufig die darunterliegende Mapnik-Basiskarte aktualisiert wird. Je nach dem wie beschäftigt der Server ist, kann das zwischen wenigen Minuten und einer Woche dauern.)

Der Server läuft auf einem gewöhnlichen Debian Linux und benutzt eine Toolchain aus osmosis_, Postgresql_ und Mapnik_, um die Karte zu rendern. Mit Hilfe von osgene werden die Daten vor dem Rendern vorverarbeitet. Die Webseite basiert auf dem `Django Web-Framework`_. Mehr Informationen dazu auf der GitHub-Projektseite_.

.. _osmosis: http://wiki.openstreetmap.org/wiki/Osmosis
.. _Postgresql: http://www.postgresql.org/
.. _Mapnik: http://www.mapnik.org/
.. _`Django Web-Framework`: https://www.djangoproject.com/
.. _`GitHub-Projektseite`: https://github.com/lonvia/multiroutemap

.. subpage:: copyright Copyright

Das Wanderwege-Overlay und die GPX-Tracks stehen unter einer `Creative Commons Attribution-Share Alike 3.0 Germany Lizenz`_. Sie dürfen also weiterverwendet und verändert werden, solange das entstehende Werk wiederum unter einer kompatiblen Lizenz steht und sowohl OpenStreetMap als auch diese Seite als Ursprung erwähnt werden.

Nutzungsbedingungen
-------------------

Das Overlay kann in andere Webseiten eingebunden werden, solange die Zugriffsraten moderat sind. Die Tiles sollten so oft wie möglich gecacht werden und der Referer muss korrekt gesetzt sein. Massen-Download von Kartenteilen ist nicht gerne gesehen.

Die GPX-Dateien werden ausschliesslich für Besucher dieser Seite zur Verfügung gestellt. Automatische Downloads oder direkte Links von anderen Seiten werden nicht toleriert.

.. _`Creative Commons Attribution-Share Alike 3.0 Germany Lizenz`: http://creativecommons.org/licenses/by-sa/3.0/de/deed.de

.. subpage:: acknowledgements Danksagungen

Die Kartendaten stammen aus dem OpenStreetMap-Projekt und stehen unter einer `CC BY-SA 2.0 Lizenz`_.

Das Overlay mit dem Höhenprofil wird freundlicherweise von der `Hike & Bike Map`_ zur Verfügung gestellt. Die Karte ist immer einen Besuch wert. Die Daten basieren auf den frei verfügbaren SRTM3 v2-Daten der NASA.

Dank geht auch an `Martin Hoffmann`_ für seine grosszügige Unterstützung des Servers, sowie für die Hilfe bei der Übersetzung an:

  * Yves Cainaud (Französisch)
  * Oscar Formaggi (Italienisch)
  * Gustavo Ramis - `Tuentibiker`_ (Spanisch)
  * `Guttorm Flatabø`_/`TG4NP`_ (Norwegisch bokmål und nynorsk)
  * Mads Lumholt/TG4NP (Dänisch)
  * Magnús Smári Snorrason/TG4NP (Isländisch)
  * Lars Mikaelsson/TG4NP (Schwedisch)
  * Elina Pesonen (Finnisch)

.. _`CC BY-SA 2.0 Lizenz`: http://creativecommons.org/licenses/by-sa/2.0/deed.de
.. _`Hike & Bike Map`: http://hikebikemap.de/
.. _`Tuentibiker`: http://www.blogger.com/profile/12473561703699888751
.. _`Martin Hoffmann`: http://www.partim.de
.. _`Guttorm Flatabø`: http://guttormflatabo.com
.. _`TG4NP`: http://tg4np.eu


.. subpage:: contact Kontakt

Fragen und Kommentare können an `lonvia@denofr.de`_ gesendet werden.

Haftungsausschluss
------------------

Es kann weder für die Richtigkeit noch die Vollständigkeit der Karte eine Garantie übernommen werden. Wanderungen sollten nie ohne eine gute Papierkarte und der entsprechenden Ausrüstung unternommen werden. Wer diesem Rat nicht folgt und sich verirrt, ist auf sich selbst gestellt.

Diese Seite enthält Links zu externen Webseiten für deren Inhalt der Autor dieser Webseite keine Kontrolle hat und daher keine Verantwortung übernehmen kann.

.. _`lonvia@denofr.de`: mailto:lonvia@denofr.de

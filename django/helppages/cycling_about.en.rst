.. subpage:: about About the Map

This map shows sign-posted cycling routes around the world. It is based on data from the OpenStreetMap_ (OSM) project. OSM is a freely editable world map where anybody can participate. That means that this hiking map is by no means complete, but it also means that you can contribute by adding new routes and correcting mistakes in existing ones. To find out more about OpenStreetMap, see the `Beginner's Guide`_.

This map only provides an overlay with the cycling routes. It was designed for the OSM Mapnik map as base map but should work together with other online maps as well. Please, read the `Usage Policy`_ before using it on your own website.

.. _OpenStreetMap: http://www.openstreetmap.org
.. _`Beginner's Guide`: http://wiki.openstreetmap.org/wiki/Beginners%27_Guide
.. _`Usage Policy`: copyright

.. subpage:: rendering Rendering OSM Data

Cycling routes in OSM should be entered as relations. How this works is described in detail on the `Cycle Routes`_ tagging page in the OSM wiki. This map shows all relations that have at least the following tags:

::

    type = route|superroute
    route = bicycle

MTB route are currently not supported. The classification (and therefore the colour of the route in the map) is determined from the ``network`` tag. The label is guessed from the tags in the following order:

 1. If a ``ref`` tag exists, make a text label with the ``ref`` tag.
 2. If a ``name`` tag exists, derive a reference from that, first by using only upper-case letters and failing that by using the first letters of the name. 
    *Note for mapping: guessing a reference from the route name is essentially a hack to show something for incompletely tagged routes. Use an explicit route reference wherever possible.*
 3. Give up. 

The map also supports `relation hierarchies`_.

.. _`Cycle Routes`: http://wiki.openstreetmap.org/wiki/Cycle_routes
.. _`localized rendering rules`: rendering/local_rules
.. _`osmc:symbol rendering rules`: rendering/osmc_symbol
.. _`relation hierarchies`: rendering/hierarchies
.. _Guideposts: http://wiki.openstreetmap.org/wiki/Tag:information%3Dguidepost


.. subpage:: rendering/hierarchies Relation Hierarchies

The map also supports nested relations, i.e. relations that contain relations themselves. At the moment there are two main uses for such relation hierarchies: they are either used to split up very long routes (e.g. E1_) or they are used to avoid duplicated work where two routes go along the same way (see, for example, the Swiss `Via Francigena`_ which is part of the European `Via Romea Francigena`_). In the first case the sub-relations are not complete routes themselves and should therefore not be shown on a map.

How exactly a subrelation is treated by the renderer depends on the network tag:

  * If parent and child relation share the same network tag, the child relation is taken to be just a stage of the parent relation. Thus, its route is added to the parent relation and the child relation is not shown in the map.
  * If the network tag of parent and child relation are different, the relation are assumed to be independent. The route of the child relation is added to the parent and both relations are shown in the map.

*Note:* you can always inspect subrelations via the route browser. Simply select the parent relation and a selectable list of its subrelations is shown.

.. _E1: /route/European%20walking%20route%20E1
.. _`Via Francigena`: /route/Via%20Francigena,%20Swiss%20part
.. _`Via Romea Francigena`: /route/Via%20Romea%20Francigena


.. subpage:: technical Technical Details


The overlay is updated once a day. The date in the upper left corner shows the last update. Normally, contributions until around 1 am are taken into account. (Updates of the underlying Mapnik map are not within this site's control. Depending on the current load of the OSM server they take between a minute and a week.)

The machine runs a standard Debian Linux with a osmosis_/Postgresql_/Mapnik_ toolchain. osgende takes care of some postprocessing on the database before rendering. The website uses the `Django web framework`_. For more information and access to the source code visit the `development pages`_.

Translation Help Wanted
-----------------------

If you would like to help translating the website into your language, please contact `lonvia@denofr.de`_.

.. _osmosis: http://wiki.openstreetmap.org/wiki/Osmosis
.. _Postgresql: http://www.postgresql.org/
.. _Mapnik: http://www.mapnik.org/
.. _`Django web framework`: http://www.djangoproject.com/
.. _`development pages`: http://dev.lonvia.de/trac
.. _`lonvia@denofr.de`: mailto:lonvia@denofr.de

.. subpage:: copyright Copyright

The hiking overlay and the GPX tracks are available under a `Creative Commons Attribution-Share Alike 3.0 Germany License`_. Thus, they maybe reused and changed as long as the resulting work uses a compatible license and OpenStreetMap and this site are mentioned.

Usage Policy
------------

You may use the overlay on other sites as long as access rates are moderate. Please, cache tiles as often as possible and use a correct referrer. Mass download of tiles is strongly discouraged.

.. _`Creative Commons Attribution-Share Alike 3.0 Germany License`: http://creativecommons.org/licenses/by-sa/3.0/de/deed.en

.. subpage:: acknowledgements Acknowledgements

All map data provided by OpenStreetMap and contributors and released under a `CC-by-SA 2.0 license`_.

Hillshading overlay provided by the beautiful `Hike & Bike Map`_ and based on the public-domain NASA SRTM3 v2 dataset.

Thanks go also to Yves Cainaud for the French translation, to Oscar Formaggi for the Italian translation and to partim_ for generously supporting the server.

.. _`CC-by-SA 2.0 license`: http://creativecommons.org/licenses/by-sa/2.0/
.. _`Hike & Bike Map`: http://hikebikemap.de/
.. _partim: http://www.partim.de

.. subpage:: contact Contact

Questions and comments to this site can be sent to: `lonvia@denofr.de`_.

Disclaimer
----------

Neither correctness nor completeness of the map can be guaranteed. If you go out cycling, don't leave your common sense at home.

This site contains links to external websites. The author of this site has no influence on the content of these websites and cannot take any responsibility.

We are also not responsible for last week's earthquake, flat tires and the movement of butterflies.

.. _`lonvia@denofr.de`: mailto:lonvia@denofr.de

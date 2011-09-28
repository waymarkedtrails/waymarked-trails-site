.. subpage:: about About the Map

This map shows sign-posted hiking routes around the world. It is based on data from the OpenStreetMap_ (OSM) project. OSM is a freely editable world map where anybody can participate. That means that this hiking map is by no means complete, but it also means that you can contribute by adding new routes and correcting mistakes in existing ones. To find out more about OpenStreetMap, see the `Beginner's Guide`_.

This map only provides an overlay with the hiking routes. It was designed for the OSM Mapnik map as base map but should work together with other online maps as well. Please, read the `Usage Policy`_ before using it on your own website.

.. _OpenStreetMap: http://www.openstreetmap.org
.. _`Beginner's Guide`: http://wiki.openstreetmap.org/wiki/Beginners%27_Guide
.. _`Usage Policy`: copyright

.. subpage:: rendering Rendering OSM Data

Hiking routes in OSM should be entered as relations. How this works is described in detail on the `Walking Routes`_ tagging page in the OSM wiki. This map shows all relations that have at least the following tags:

::

    type = route|superroute
    route = foot|walking|hiking


Which route type is given makes no difference. The classification (and therefore the colour of the route in the map) is determined from the ``network`` tag. The symbol is guessed from the tags in the following order:

 1. Check for `localized rendering rules`_.
 2. Try to interpret the ``osmc:symbol`` tag. For details about which parts are understood, see `osmc:symbol rendering rules`_.
 3. If a ``ref`` tag exists, make a text label with the ``ref`` tag.
 4. If a ``name`` tag exists, derive a reference from that, first by using only upper-case letters and failing that by using the first letters of the name. 
    *Note for mapping: guessing a reference from the route name is essentially a hack to show something for incompletely tagged routes. Use an explicit route reference wherever possible.*
 5. Give up. 

The map also supports `relation hierarchies`_.

Guideposts_ must have the following tags:

::

    tourism=information
    information=guidepost
    name=<name>
    ele=<altitude>

If both, ``name`` and ``ele``, are missing the guidepost will appear as an unnamed guidepost in gray.  

.. _`Walking Routes`: http://wiki.openstreetmap.org/wiki/Walking_Routes
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

.. subpage:: rendering/osmc_symbol osmc:symbol Tag

The osmc:symbol tag provides a way to describe in a machine-readable way route symbols in simple geometric shapes like they are found in some European countries (and especially in Germany). The hiking map only supports a subset of what is described on the Wiki page. In order to be rendered on the map, the tag must have the following format:


::

  osmc:symbol=waycolor:background:foreground:text:textcolor

Waycolor must be there but is ignored for this map. Foreground may not be empty, a second foreground is not supported. Text and text color can be omitted. There is a `list of foreground and background symbols rendered in this map`_ available.

*Note:* the older version of the map accepted the ``foreground`` part to be empty. This is no longer supported because the ``osmc:symbol`` tag should only be used to describe geometric shapes. Without the foreground shape, the symbol describes a simple reference of the way and, for the sake of clarity will be rendered as such. Local exceptions may be possible. 

.. _`list of foreground and background symbols rendered in this map`: ../osmc_symbol_legende

.. subpage:: rendering/local Localized Rendering

There are a lot of different systems to mark hiking paths out there. While the map attempts to use the most general tags to give them a decent rendering, it is bound to fail for certain systems, especially for networks of hiking paths. To accommodate these systems, the map can be localised for regions where the standard rendering is insufficient.

Below is a list of regions that use special map symbols. In order to have your own region rendered in a special way, read the hints at the end of the page.

Switzerland
===========

Switzerland has a very extensive network of marked hiking paths that is stretched out over the entire country. The network is a node network where named guideposts function as the nodes. All paths are marked consistently according to their difficulty. The map shows these paths in red with the line pattern marking the difficulty:

+----------+-----------------------------------------+------------------------------+
|On Map    | Description                             | In OSM                       |
+==========+=========================================+==============================+
||routestd|| *Hiking path*, marked with |diamond|    | ``network=lwn``              |
|          |                                         |                              |
|          | Suitable for anybody.                   | ``osmc:symbol=yellow:[...]`` |
+----------+-----------------------------------------+------------------------------+
||routemnt|| *Mountain path*, marked with |whitered| | ``network=lwn``              |
|          |                                         |                              |
|          | Requires a resonable level of fitness   | ``osmc:symbol=red:[...]``    |
|          | and surefootedness.                     |                              |
|          | Fear of heights might pose a problem.   |                              |
+----------+-----------------------------------------+------------------------------+
||routealp|| *Alpine path*, marked with |whiteblue|  | ``network=lwn``              |
|          |                                         |                              |
|          | Requires mountaineering experience and  | ``osmc:symbol=blue:[...]``   |
|          | appropriate gear                        |                              |
+----------+-----------------------------------------+------------------------------+

Note that on top of this network there are a number of national and regional routes which are shown in the normal way.

For more information about tagging hiking paths in Switzerland in OSM see: `Swiss Hiking Network on the OSM Wiki`_.

United Kingdom
==============

The classification of `UK long-distance paths`_ (those tagged with ``network=uk_ldp``) depends on the ``operator`` tag. Relations with ``operator=National Trails`` are shown as national trails, all other relations appear as regional routes.

Relations with a ``network=lwn/rwn/nwn/iwn`` tag are handled as usual.

Czech Republic
==============

The country uses a trail marking standard based on a set of 7 symbols in 4 different colors. For a description see the `Czech tagging page`_ (Czech only).

When a ``kct_*`` tag is available it is preferred over any ``osmc:symbol`` tag. In addition, the route is reclassified if no valid network tag can be found. Routes with ``kct_red=major`` become national routes, other ``kct_*=major`` are classified as regional.

Note: Symbols are derived from the excellent vector graphics by Radomir.cernoch as found in the OSM wiki.

Slovakia
========

Slovakia uses the same trail marking standard as the Czech Republic. However, the tagging schema is slightly different, see the `Slovakian hiking page`_.

All routes with a tag ``operator=KST`` are tagged according to that schema. As routes in Slovakia should come with a valid network tag, there is no reclassification performed.

Germany
=======

Fränkischer Albverein
---------------------

The network around Nuremberg is quite dense, therefore regional routes tagged with ``operator=Fränkischer Albverein`` will appear on zoom levels lower than usual.

.. |routestd|  image:: /media/static/img/route_std.png
.. |routemnt|  image:: /media/static/img/route_mnt.png
.. |routealp|  image:: /media/static/img/route_alp.png
.. |diamond|   image:: /media/static/img/yellow_diamond.png
.. |whitered|  image:: /media/static/img/white_red_white.png
.. |whiteblue| image:: /media/static/img/white_blue_white.png
.. _`Swiss Hiking Network on the OSM Wiki`: http://wiki.openstreetmap.org/wiki/EN:Switzerland/HikingNetwork
.. _`UK long-distance paths`: http://wiki.openstreetmap.org/wiki/WikiProject_United_Kingdom_Long_Distance_Paths
.. _`Czech tagging page`: http://wiki.openstreetmap.org/wiki/WikiProject_Czech_Republic/Editing_Standards_and_Conventions#Doporu.C4.8Den.C3.A9_typy_cest
.. _`Slovakian hiking page`: http://wiki.openstreetmap.org/wiki/WikiProject_Slovakia/Hiking_routes



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

GPX tracks are provided for the convenience of visitors of this site. Automatic downloads and direct linking from other sites is not ok.

.. _`Creative Commons Attribution-Share Alike 3.0 Germany License`: http://creativecommons.org/licenses/by-sa/3.0/de/deed.en

.. subpage:: acknowledgements Acknowledgements

All map data provided by OpenStreetMap and contributors and released under a `CC-by-SA 2.0 license`_.

Hillshading overlay provided by the beautiful `Hike & Bike Map`_ and based on the public-domain NASA SRTM3 v2 dataset.

Thanks go also to Yves Cainaud for the French translation, Oscar Formaggi for the Italian translation and to partim_ for generously supporting the server.

.. _`CC-by-SA 2.0 license`: http://creativecommons.org/licenses/by-sa/2.0/
.. _`Hike & Bike Map`: http://hikebikemap.de/
.. _partim: http://www.partim.de

.. subpage:: contact Contact

Questions and comments to this site can be sent to: `lonvia@denofr.de`_.

Disclaimer
----------

Neither correctness nor completeness of the map can be guaranteed. If you go out for a hike, get a decent paper map, appropriate gear and don't leave your common sense at home. Nature can be as ruthless as it is beautiful.

This site contains links to external websites. The author of this site has no influence on the content of these websites and cannot take any responsibility.

We are also not responsible for tomorrow's weather, last weekend's lottery numbers and the state of the cat.

.. _`lonvia@denofr.de`: mailto:lonvia@denofr.de

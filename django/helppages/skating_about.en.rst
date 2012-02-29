.. subpage:: about About the map

This map shows sign-posted inline skating routes around the world. It is based on data from the OpenStreetMap_ (OSM) project. OSM is a freely editable world map where anybody can participate. That means that this hiking map is by no means complete, but it also means that you can contribute by adding new routes and correcting mistakes in existing ones. To find out more about OpenStreetMap, see the `Beginner's guide`_.

This map only provides an overlay with the inline skating routes. It was designed for the OSM Mapnik map as base map but should work together with other online maps as well. Please, read the `Usage policy`_ before using it on your own website.

.. _OpenStreetMap: http://www.openstreetmap.org
.. _`Beginner's guide`: http://wiki.openstreetmap.org/wiki/Beginners%27_Guide
.. _`Usage policy`: copyright

.. subpage:: rendering Rendering OSM data

Skating routes in OSM should be entered as relations. For the tagging understood by this map, have a look at the `wiki page about swiss inline skating routes`_ . This map shows all relations that have at least the following tags:

::

    type = route|superroute
    route = incline_skates

The classification (and therefore the colour of the route in the map) is determined from the ``network`` tag. The label is guessed from the tags in the following order:

 1. If a ``ref`` tag exists, make a text label with the ``ref`` tag.
 2. If a ``name`` tag exists, derive a reference from that, first by using only upper-case letters and failing that by using the first letters of the name. 
    *Note for mapping: guessing a reference from the route name is essentially a hack to show something for incompletely tagged routes. Use an explicit route reference wherever possible.*
 3. Give up. 

The map also supports `relation hierarchies`_.

.. _`wiki page about swiss inline skating routes`: http://wiki.openstreetmap.org/wiki/EN:Switzerland/InlineNetwork
.. _`relation hierarchies`: rendering/hierarchies


.. subpage:: rendering/hierarchies Relation hierarchies

The map also supports nested relations, i.e. relations that contain relations themselves. At the moment there are two main uses for such relation hierarchies: they are either used to split up very long routes (e.g. E1_) or they are used to avoid duplicated work where two routes go along the same way (see, for example, the Swiss `Via Francigena`_ which is part of the European `Via Romea Francigena`_). In the first case the sub-relations are not complete routes themselves and should therefore not be shown on a map.

How exactly a subrelation is treated by the renderer depends on the network tag:

  * If parent and child relation share the same network tag, the child relation is taken to be just a stage of the parent relation. Thus, its route is added to the parent relation and the child relation is not shown in the map.
  * If the network tag of parent and child relation are different, the relation are assumed to be independent. The route of the child relation is added to the parent and both relations are shown in the map.

*Note:* you can always inspect subrelations via the route browser. Simply select the parent relation and a selectable list of its subrelations is shown.

.. _E1: /route/European%20walking%20route%20E1
.. _`Via Francigena`: /route/Via%20Francigena,%20Swiss%20part
.. _`Via Romea Francigena`: /route/Via%20Romea%20Francigena

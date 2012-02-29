.. subpage:: about About the map

This map shows sign-posted cycling routes around the world. It is based on data from the OpenStreetMap_ (OSM) project. OSM is a freely editable world map where anybody can participate. That means that this cycling map is by no means complete, but it also means that you can contribute by adding new routes and correcting mistakes in existing ones. To find out more about OpenStreetMap, see the `Beginner's guide`_.

This map only provides an overlay with the cycling routes. It was designed for the OSM Mapnik map as base map but should work together with other online maps as well. Please, read the `Usage policy`_ before using it on your own website.

.. _OpenStreetMap: http://www.openstreetmap.org
.. _`Beginner's guide`: http://wiki.openstreetmap.org/wiki/Beginners%27_Guide
.. _`Usage policy`: copyright

.. subpage:: rendering Rendering OSM data

Cycling routes in OSM should be entered as relations. How this works is described in detail on the `cycle routes`_ tagging page in the OSM wiki. This map shows all relations that have at least the following tags:

::

    type = route|superroute
    route = bicycle

MTB routes can be found on their own map, the `MTB route map`_.

The classification (and therefore the colour of the route in the map) is determined from the ``network`` tag. The label is guessed from the tags in the following order:

 1. If a ``ref`` tag exists, make a text label with the ``ref`` tag.
 2. If a ``name`` tag exists, derive a reference from that, first by using only upper-case letters and failing that by using the first letters of the name. 
 3. Give up. 

The map also supports `relation hierarchies`_.

.. _`cycle routes`: http://wiki.openstreetmap.org/wiki/Cycle_routes
.. _`relation hierarchies`: rendering/hierarchies
.. _`MTB route map`: http://mtb.lonvia.de


.. subpage:: rendering/hierarchies Relation hierarchies

The map also supports nested relations, i.e. relations that contain relations themselves. At the moment there are two main uses for such relation hierarchies: they are either used to split up very long routes (e.g. E1_) or they are used to avoid duplicated work where several routes follow the same way. See, for example, the Swiss `Via Francigena`_ which is part of the European `Via Romea Francigena`_. In the first case the sub-relations are not complete routes themselves and should therefore not be shown on a map.

How exactly a subrelation is treated by the renderer depends on the network tag:

  * If parent and child relation share the same network tag, the child relation is taken to be just a stage of the parent relation. Thus, its route is added to the parent relation and the child relation is not shown in the map.
  * If the network tag of parent and child relation are different, the relation are assumed to be independent. The route of the child relation is added to the parent and both relations are shown in the map.

*Note:* you can always inspect subrelations via the route browser. Simply select the parent relation and a selectable list of its subrelations is shown.

.. _E1: /route/European%20walking%20route%20E1
.. _`Via Francigena`: /route/Via%20Francigena,%20Swiss%20part
.. _`Via Romea Francigena`: /route/Via%20Romea%20Francigena

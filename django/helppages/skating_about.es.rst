.. subpage:: about About the Map

Este mapa muestra las rutas para patín en línea señalizadas alrededor del mundo. Se basa en los datos del proyecto `OpenStreetMap`_ (OSM). OSM es un mapa mundial que se puede modificar libremente donde cualquiera puede participar. Eso significa que este mapa para bicicletas no está completo, y también significa que usted puede contribuir mediante la adición de nuevas rutas y la corrección de errores en las existentes. Para obtener más información acerca de OpenStreetMap, consulte la `Guía del principiante`_.

Este mapa sólo proporciona una capa superpuesta con las rutas en bicicleta. Fue diseñado para el mapa de OSM Mapnik como mapa base, pero debería trabajar junto con otros mapas en línea. Por favor, lea la `Política de uso`_ antes de usarlo en su propio website.

.. _OpenStreetMap: http://www.openstreetmap.org
.. _`Guía del principiante`: http://wiki.openstreetmap.org/wiki/ES:Beginners%27_Guide
.. _`Política de uso`: copyright

.. subpage:: rendering Representación de datos del OSM

Las rutas para patín en línea en el OSM deben ingresarse como relaciones. Cómo funciona esto se describe en detalle en la página de etiquetas (tags) de la wiki del OSM sobre `Rutas Suizas de Patín en línea`_ (en inglés). Este mapa muestra todas las relaciones que tienen por lo menos las siguientes etiquetas: 

::

    type = route|superroute
    route = inline_skates

La clasificación (y por lo tanto el color de la ruta en el mapa) se determina a partir de la etiqueta de ``red``. 

La etiqueta o sigla en este mapa es estimada a partir de las etiquetas del OSM en el siguiente orden:

  1. Si una etiqueta ``ref`` existe, hace una etiqueta de texto en este mapa con los datos de la etiqueta ref.
  2. Si una etiqueta ``name`` existe, obtiene una referencia de allí, primero utilizando sólo las letras mayúsculas y en su defecto mediante el uso de las primeras letras del nombre.
     *Tenga en cuenta al mapear: adivinar una referencia por el nombre de la ruta es básicamente un truco para mostrar algo en las rutas mal etiquetadas. Utilizar una referencia de ruta explícita siempre que sea posible.*
  3. Darse por vencido.

El mapa también es compatible con `relaciones jerárquicas`_.

.. _`Rutas Suizas de Patín en línea`: http://wiki.openstreetmap.org/wiki/EN:Switzerland/InlineNetwork
.. _`relaciones jerárquicas`: rendering/hierarchies


.. subpage:: rendering/hierarchies Relaciones Jerárquicas

El mapa también soporta relaciones anidadas, p.ej. relaciones que a su vez contienen relaciones. En este momento hay dos usos principales para las relaciones jerárquicas: son utilizadas para dividir las rutas muy largas (p.ej. E1_) o se utilizan para evitar la duplicación del trabajo en el que dos rutas van por el mismo camino (véase, por ejemplo, la suiza `Via Francigena`_ que forma parte de la Europea `Via Romea Francigena`_). En el primer caso las sub-relaciones no son rutas completas en sí mismas y no deben por lo tanto, aparecer en el mapa.

Cómo es tratada exactamente una subrelación para el procesado, depende de la etiqueta de la red:

  * Si la relación madre e hija comparten la misma etiqueta de red, la relación hija se considera que es sólo una etapa de la relación madre. Por lo tanto, su ruta se añade a la relación madre y la relación hija no se muestra en el mapa.
  * Si la etiqueta de red de una relación madre e hija son diferentes, las relaciones se supone que son independientes. La ruta de la relación hija se añade a la relación madre y las dos relaciones se muestran en el mapa.

*Nota:* siempre se puede inspeccionar subrelaciones a través del navegador. Sólo tiene que seleccionar la relación madre y una lista seleccionable de subrelaciones es mostrada.

.. _E1: /route/European%20walking%20route%20E1
.. _`Via Francigena`: /route/Via%20Francigena,%20Swiss%20part
.. _`Via Romea Francigena`: /route/Via%20Romea%20Francigena

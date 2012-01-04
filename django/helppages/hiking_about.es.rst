.. subpage:: about About the Map

El mapa muestra rutas señalizadas de senderismo de todo el mundo. Se basa en los datos del proyecto OpenStreetMap_ (OSM). OSM es un mapamundi libremente editable donde cualquiera puede participar. Esto significa que este mapa de rutas no está absolutamente completo, pero también significa que usted puede contribuir mediante la adición de nuevas rutas y la corrección de errores en las existentes. Para obtener más información acerca de OpenStreetMap, vea la `Guía del principiante`_.

Este mapa sólo ofrece una plantilla con las rutas de senderismo. Fue diseñado para el mapa OSM Mapnik como mapa base pero debería trabajar junto con otros mapas en línea también. Por favor, lea la `política de uso`_ antes de utilizarlo en su propio sitio web.

.. _OpenStreetMap: http://www.openstreetmap.org
.. _`Guía del principiante`: http://wiki.openstreetmap.org/wiki/ES:Beginners%27_Guide
.. _`política de uso`: copyright

.. subpage:: rendering Representación de datos del OSM

Las rutas para senderismo en el OSM deben ingresarse como relaciones. Cómo funciona esto se describe en detalle en la página de etiquetas (tags) de la wiki del OSM sobre `Walking Routes`_ . Este mapa muestra todas las relaciones que tienen por lo menos las siguientes etiquetas: 

::

    type = route|superroute
    route = foot|walking|hiking


No hace diferencia qué tipo ruta es dada. La clasificación (y por lo tanto el color de la ruta en el mapa) se determina a partir de la etiqueta de la "red". La etiqueta o sigla en este mapa es estimada a partir de las etiquetas del OSM en el siguiente orden:

 1. Comprueba `reglas locales de renderizado`_.
 2. Tratar de interpretar la etiqueta ``osmc: symbol``. Para obtener más información acerca de qué partes son comprendidas, véase `osmc:symbol reglas de renderizado`_.
 3. Si una etiqueta ``ref`` existe, hace una etiqueta de texto en este mapa con los datos de la etiqueta ref.
 4. Si una etiqueta ``name`` existe, obtiene una referencia de allí, primero utilizando sólo las letras mayúsculas y en su defecto mediante el uso de las primeras letras del nombre.
     *Tenga en cuenta al mapear: adivinar una referencia por el nombre de la ruta es básicamente un truco para mostrar algo en las rutas mal etiquetadas. Utilizar una referencia de ruta explícita siempre que sea posible.*
 5. Darse por vencido. 

El mapa también es compatible con `relaciones jerárquicas`_.

Hitos_ o postes indicadores deben tener las siguientes etiquetas:

::

    tourism=information
    information=guidepost
    name=<nombre>
    ele=<altitud>

Si ambos, ``name`` y ``ele``, no están el hito aparecerá sin nombre y grisado.  

.. _`Walking Routes`: http://wiki.openstreetmap.org/wiki/Walking_Routes
.. _`reglas locales de renderizado`: rendering/local
.. _`osmc:symbol reglas de renderizado`: rendering/osmc_symbol
.. _`relaciones jerárquicas`: rendering/hierarchies
.. _Hitos: http://wiki.openstreetmap.org/wiki/Tag:information%3Dguidepost


.. subpage:: rendering/hierarchies Relaciones Jerárquicas

El mapa también soporta relaciones anidadas, p.ej. relaciones que a su vez contienen relaciones. En este momento hay dos usos principales para las relaciones jerárquicas: son utilizadas para dividir las rutas muy largas (p.ej. E1_) o se utilizan para evitar la duplicación del trabajo en el que dos rutas van por el mismo camino (véase, por ejemplo, la suiza `Via Francigena`_ que forma parte de la Europea `Via Romea Francigena`_). En el primer caso las sub-relaciones no son rutas completas en sí mismas y no deben por lo tanto, aparecer en el mapa.

Cómo es tratada exactamente una subrelación para el procesado, depende de la etiqueta de la red:

  * Si la relación madre e hija comparten la misma etiqueta de red, la relación hija se considera que es sólo una etapa de la relación madre. Por lo tanto, su ruta se añade a la relación madre y la relación hija no se muestra en el mapa.
  * Si la etiqueta de red de una relación madre e hija son diferentes, las relaciones se supone que son independientes. La ruta de la relación hija se añade a la relación madre y las dos relaciones se muestran en el mapa.

*Nota:* siempre se puede inspeccionar subrelaciones a través del navegador. Sólo tiene que seleccionar la relación madre y una lista seleccionable de subrelaciones es mostrada.

.. _E1: /route/European%20walking%20route%20E1
.. _`Via Francigena`: /route/Via%20Francigena,%20Swiss%20part
.. _`Via Romea Francigena`: /route/Via%20Romea%20Francigena

.. subpage:: rendering/osmc_symbol La etiqueta osmc:symbol

La etiqueta osmc:symbol proporciona una manera de describir en una forma legible por el programa, símbolos en formas geométricas simples, como se encuentran en algunos países europeos (y especialmente en Alemania). El mapa de senderismo sólo admite un subconjunto de lo que se describe en la página de Wiki. Con el fin de que se represente en el mapa, la etiqueta debe tener el siguiente formato:


::

  osmc:symbol=waycolor:background:foreground:text:textcolor

Waycolor debe estar allí, pero se ignora para este mapa. Foreground no puede estar vacío, un segundo primer plano no es compatible. Text y text color pueden ser omitidos. Hay disponible un `listado de los símbolos de primer plano (foreground) y de fondo (background) dibujados en este mapa`_.

*Nota:* la versión más antigua del mapa aceptaba el foreground vacío. Esto ya no es compatible porque la etiqueta osmc:symbol sólo debe ser usada para describir formas geométricas. Sin la forma en foreground, el symbol describe una simple referencia del camino y, en aras de la claridad, será mostrado como tal. Excepciones a nivel local pueden ser posibles.

.. _`listado de los símbolos de primer plano (foreground) y de fondo (background) dibujados en este mapa`: ../osmc_symbol_legende

.. subpage:: rendering/local Renderizado Local

Hay un montón de sistemas diferentes para marcar rutas de senderismo en varios países. Mientras el mapa intenta utilizar las etiquetas más generales, para darles una renderizado digno, está condenado al fracaso para ciertos sistemas, especialmente para las redes de rutas de senderismo. Para acomodarse a estos sistemas, el mapa se puede adaptar para los países donde la representación estándar es insuficiente.

A continuación se muestra una lista de países que utilizan mapas con símbolos especiales. Con el fin de tener su propio país representado de una manera especial, visite los enlaces y lea los consejos al final de cada uno.


Suiza
=====

Suiza cuenta con una extensa red de senderos demarcados que se extiende a lo largo de todo el país. La red es una red de nodos, donde hitos guías determinados funcionan como nodos. Todas las rutas están marcadas consistentemente de acuerdo a su dificultad. El mapa muestra esos senderos en rojo con un patrón de líneas que marca la dificultad:

+----------+---------------------------------------------+------------------------------+
|En Mapa   | Descripción                                 | Etiqueta en OSM              |
+==========+=============================================+==============================+
||routestd|| *Sendero*, marcado con |diamond|            | ``network=lwn``              |
|          |                                             |                              |
|          | Apto para cualquier persona.                | ``osmc:symbol=yellow:[...]`` |
+----------+---------------------------------------------+------------------------------+
||routemnt|| *Sendero montañoso*, marcado con |whitered| | ``network=lwn``              |
|          |                                             |                              |
|          | Requiere un nivel razonable de estado físico| ``osmc:symbol=red:[...]``    |
|          | y pisada.                                   |                              |
|          | Miedo a las alturas puede ser un problema.  |                              |
+----------+---------------------------------------------+------------------------------+
||routealp|| *Sendero Alpino*, marcado con |whiteblue|   | ``network=lwn``              |
|          |                                             |                              |
|          | Requiere experiencia en montañismo y        | ``osmc:symbol=blue:[...]``   |
|          | el equipo adecuado                          |                              |
+----------+---------------------------------------------+------------------------------+

Tenga en cuenta que sobre esta red hay una serie de rutas nacionales y regionales que se muestran en la forma habitual.

Para más información sobre etiquetado de rutas de senderismo en Suiza en OSM ver: `Red de Senderos de Suiza en el Wiki de OSM`_.


Reino Unido
===========

La clasificación para `senderos de larga distancia en el Reino Unido`_ (los etiquetados con network=uk_ldp) depende de la etiqueta del operador. Las relaciones con operator=National Trails se muestran como caminos nacionales, todas las demás relaciones aparecen como rutas regionales.

Relaciones con la etiqueta ``network=lwn/rwn/nwn/iwn`` se manejan como de costumbre.


República Checa
===============

El país utiliza un estándar de señalización de caminos sobre la base de un conjunto de 7 símbolos en 4 colores diferentes. Para una descripción vea la `página de etiquetado Checa`_ (Sólo en Checo).

Cuando una etiqueta ``kct_*`` está disponible se prefiere sobre cualquier etiqueta ``osmc:symbol``. Además, la ruta es reclasificada si no hay una etiqueta de red válida que se pueda encontrar. Rutas con la etiqueta ``kct_red=major`` son consideradas rutas nacionales, otras etiquetas ``kct_*=major`` son clasificadas como regionales.

Nota: Los símbolos se derivan de los excelentes gráficos vectoriales de Radomir.cernoch como se encuentran en la wiki de OSM.


Eslovaquia
==========

Eslovaquia utiliza el mismo sendero estándar de marcas que la República Checa. Sin embargo el esquema de etiquetado es ligeramente diferente, vea la `página Eslovaca de senderismo`_.

Todas las rutas con la etiqueta ``operator=KST`` son marcadas de acuerdo a ese esquema. Como las rutas en Eslovaquia deben venir con una etiqueta de red válida, no hay reclasificación realizada.


Alemania
========

Fränkischer Albverein
---------------------

La red en los alrededores de Núremberg es bastante densa, por lo tanto, las rutas regionales marcadas con ``operator=Fränkischer Albverein`` van a aparecer en niveles de zoom inferiores al habitual.


.. |routestd|  image:: {{MEDIA_URL}}/img/route_std.png
.. |routemnt|  image:: {{MEDIA_URL}}/img/route_mnt.png
.. |routealp|  image:: {{MEDIA_URL}}/img/route_alp.png
.. |diamond|   image:: {{MEDIA_URL}}/img/yellow_diamond.png
.. |whitered|  image:: {{MEDIA_URL}}/img/white_red_white.png
.. |whiteblue| image:: {{MEDIA_URL}}/img/white_blue_white.png
.. _`Red de Senderos de Suiza en el Wiki de OSM`: http://wiki.openstreetmap.org/wiki/EN:Switzerland/HikingNetwork
.. _`senderos de larga distancia en el Reino Unido`: http://wiki.openstreetmap.org/wiki/WikiProject_United_Kingdom_Long_Distance_Paths
.. _`página de etiquetado Checa`: http://wiki.openstreetmap.org/wiki/WikiProject_Czech_Republic/Editing_Standards_and_Conventions#Doporu.C4.8Den.C3.A9_typy_cest
.. _`página Eslovaca de senderismo`: http://wiki.openstreetmap.org/wiki/WikiProject_Slovakia/Hiking_routes


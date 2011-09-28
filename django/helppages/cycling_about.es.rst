.. subpage:: about Sobre el mapa

Este mapa muestra las rutas en bicicleta señalizadas alrededor del mundo. Se basa en los datos del proyecto OpenStreetMap_ (OSM). OSM es un mapa mundial que se puede modificar libremente donde cualquiera puede participar. Eso significa que este mapa para bicicletas no está completo, y también significa que usted puede contribuir mediante la adición de nuevas rutas y la corrección de errores en las existentes. Para obtener más información acerca de OpenStreetMap, consulte la `Guía del principiante`_.

Este mapa sólo proporciona una capa superpuesta con las rutas en bicicleta. Fue diseñado para el mapa de OSM Mapnik como mapa base, pero debería trabajar junto con otros mapas en línea. Por favor, lea la `Política de uso`_ antes de usarlo en su propio website.

.. _OpenStreetMap: http://www.openstreetmap.org
.. _`Guía del principiante`: http://wiki.openstreetmap.org/wiki/ES:Beginners%27_Guide
.. _`Política de uso`: copyright

.. subpage:: rendering Representación de datos del OSM

Las rutas para bicicletas en el OSM deben ingresarse como relaciones. Cómo funciona esto se describe en detalle en la página de etiquetas (tags) de la wiki del OSM sobre `Rutas Ciclistas`_ (en inglés). Este mapa muestra todas las relaciones que tienen por lo menos las siguientes etiquetas: 

::

    type = route|superroute
    route = bicycle

Las rutas para MTB actualmente no son mostradas. La clasificación (y por lo tanto el color de la ruta en el mapa) se determina a partir de la etiqueta de la red. La etiqueta o sigla en este mapa es adivinada a partir de las etiquetas del OSM en el siguiente orden:

  1. Si una etiqueta ``ref`` existe, hace una etiqueta de texto en este mapa con los datos de la etiqueta ref.
  2. Si una etiqueta ``name`` existe, obtiene una referencia de allí, primero utilizando sólo las letras mayúsculas y en su defecto mediante el uso de las primeras letras del nombre.
     *Tenga en cuenta al mapear: adivinar una referencia por el nombre de la ruta es básicamente un truco para mostrar algo en las rutas mal etiquetadas. Utilizar una referencia de ruta explícita siempre que sea posible.*
  3. Darse por vencido.

El mapa también es compatible con `relaciones jerárquicas`_.

.. _`Rutas Ciclistas`: http://wiki.openstreetmap.org/wiki/Cycle_routes
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


.. subpage:: technical Detalles Técnicos

La capa se actualiza una vez al día. La fecha en la esquina superior izquierda muestra la última actualización. Normalmente, las contribuciones hasta alrededor de la 1 a.m. se tienen en cuenta. (Actualizaciones del mapa base Mapnik no están bajo el control de este sitio. Dependiendo de la carga actual del servidor de OSM pueden tomar entre un minuto y una semana.)

La máquina corre con Debian Linux con una cadena de herramientas osmosis_/Postgresql_/Mapnik_. osgende se ocupa de algo de post procesamiento de la base de datos antes de presentarla. El sitio web usa el `Django web framework`_. Para más información y acceso al código fuente visite las `páginas de desarrollo`_ (en inglés).

.. _osmosis: http://wiki.openstreetmap.org/wiki/Osmosis
.. _Postgresql: http://www.postgresql.org/
.. _Mapnik: http://www.mapnik.org/
.. _`Django web framework`: http://www.djangoproject.com/
.. _`páginas de desarrollo`: http://dev.lonvia.de/trac

.. subpage:: copyright Copyright

La capa de rutas para bicicletas y las pistas GPX están disponibles bajo una licencia `Creative Commons Attribution-Share Alike 3.0 Germany License`_. De este modo, pueden ser reutilizados y modificados, siempre que el trabajo resultante use una licencia compatible y OpenStreetMap y este sitio sean mencionados.


Política de uso
---------------

Usted puede usar la capa en otros sitios, siempre y cuando las tasas de acceso sean moderadas. Por favor, haga caché tan a menudo como sea posible y utilice un referente correcto. Descargas masivas de la capa están fuertemente desaconsejadas.

.. _`Creative Commons Attribution-Share Alike 3.0 Germany License`: http://creativecommons.org/licenses/by-sa/3.0/de/deed.es

.. subpage:: acknowledgements Reconocimientos

Todos los datos de los mapas proporcionados por OpenStreetMap y colaboradores y publicado bajo una licencia `CC-by-SA 2.0`_.

Capa de relieve proporcionada por el bello `Hike & Bike Map`_ y basada en el set de datos de dominio público NASA SRTM3 v2.

Nuestro agradecimiento también a Gustavo Ramis (Tuentibiker) por la traducción al español, a Yves Cainaud por la traducción al francés, a Oscar Formaggi por la traducción al italiano y a `Martin Hoffmann`_ por su generoso apoyo para el servidor.

.. _`CC-by-SA 2.0`: http://creativecommons.org/licenses/by-sa/2.0/deed.es
.. _`Hike & Bike Map`: http://hikebikemap.de/
.. _`Martin Hoffmann`: http://www.partim.de

.. subpage:: contact Contacto

Preguntas y comentarios a este sitio pueden ser enviados a `lonvia@denofr.de`_.

Descargo
--------

Ni la exactitud ni la integridad del mapa pueden ser garantizadas. Si usted va a salir en bicicleta, no deje su sentido común en casa.

Este sitio contiene enlaces a sitios web externos. El autor de este sitio no tiene ninguna influencia sobre el contenido de esas páginas y no puede asumir ninguna responsabilidad.

.. _`lonvia@denofr.de`: mailto:lonvia@denofr.de

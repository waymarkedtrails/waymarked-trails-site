from django.contrib.gis.db import models
import routemap.common.routemodels

class HikingRoutes(routemap.common.routemodels.RouteTableModel):
    """Table with information about hiking routes.
    """
    
    symbol = models.TextField(null=True)
    country = models.CharField(max_length=3, null=True)
    network = models.CharField(max_length=2, null=True)
    level = models.IntegerField()
    top = models.BooleanField()

    objects = models.GeoManager()

    class Meta:
        db_table = u'routes'
        db_tablespace = u'hiking'


from django.contrib.gis.db import models
import routemap.common.routemodels

class CyclingRoutes(routemap.common.routemodels.RouteTableModel):
    """Table with information about cycling routes.
    """
    
    symbol = models.TextField(null=True)
    network = models.CharField(max_length=2, null=True)
    level = models.IntegerField()
    top = models.BooleanField()

    objects = models.GeoManager()

    class Meta:
        db_table = u'routes'
        db_tablespace = u'cycling'



# This file is part of the Waymarked Trails Map Project
# Copyright (C) 2011-2012 Sarah Hoffmann
#
# This is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from collections import defaultdict
from shapely.geometry import Point, LineString
from Queue import PriorityQueue


class ProfileSegment(object):
    """ An edge within a route graph.
    """

    def __init__(self, segid, ways, geom, firstpnt, lastpnt):
        # Directional way: 0 - both, 1, forward only, -1 - backward only
        self.direction = 0
        # data from segment
        self.segid = segid
        self.ways = ways
        # geometry
        self.geom = geom
        self.firstpnt = firstpnt
        self.lastpnt = lastpnt
        # graph
        self.connection = []

    def reverse(self):
        """ Reverse direction of way and also switch
            forward and backward connections.
        """
        self.direction = -self.direction
        self.geom.reverse()


class WayPoint(object):
    """ A node within the route graph.
        The OSM node representing this graph node is `nodeid`.
    """
    def __init__(self, nodeid, coords):
        self.subnet = -1
        self.nodeid = nodeid
        self.coords = Point(coords)
        self.edges = []
        # next nodes as ids
        self.neighbours = []

    def distance_to(self, point):
        return self.coords.distance(point)



class WayProfile(object):
    """A directed graph of a route.
    """

    def __init__(self):
        # the starting point
        self.firstSegment = None
        # nodes and their edges 
        self.nodes = {}
        self.segments = []
        
    def add_segment(self, segment):
        """Add a new segment. 
           This can only be done during built-up of the profile.
        """
        self.segments.add(segment)
        self.add_segment_to_node(startpoint, segment.coords[0], endpoint, segment)
        self.add_segment_to_node(endppoint, segments.coords[-1], startpoint, segment)


    def add_segment_to_node(self, nid, geom, targetid, segment):
        """ Make a connection between node and segment.
        """
        if nid in nodes:
            node = self.nodes[nid]
        else:
            node = WayPoint(nid, geom)
            self.nodes[nid] = node

        node.edges.append(segment)
        node.neighbours.append(targetid)


    def build_directed_graph(self):
        """ Make a directed graph out of the collection of segments.
        """
        endpoints = self._mark_subgraphs(self)
        if len(endpoints) > 1:
            danglings = self._connect_subgraphs(endpoints)
        else:
            danglings = endpoints[0]

        if len(danglings) == 0:
            # TODO special case: circular way
            pass
        elif len(danglings) == 1:
            # TODO special case: circular way with dangling string
        elif len(danglings) == 1:
            # TODO special case: good route
        else:
            self._compute_main_route(danglings)


    def _compute_main_route(self, startpoints):
        """ Makes the undirected graph directed and
            computes the main route.

            Spagetti-Algorithm:
            do a Dikstra-like forward search (for the shortest path)
            up to the point where all the starting points meet. Then
            take the two longest of the paths and use that as the
            main path.
        """
        # todolist. Entries are (dist, startnode, nextpoint)
        todo = PriorityQueue()
        # initial fill
        for s in startpoints:
            todo.put((0, s, self.nodes[s]))

        # initialise the point store on the nodes
        for n in self.nodes.itervalues():
            n.dikstra = [None for x in range(len(startpoints))]

        centerpoint = None
        while not todo.empty():
            dist, startnode, currentpt = todo.get()

            for nxt in currentpt.neighbours:
                nxtpt = self.nodes[nxt]
                newdst = nxtpt.distnace_to(currentpt)
                if nxtpt.dikstra[startnode] is None or nxtpt.dikstra[startnode][1] > newdst:
                    # found a better solution, queue
                    nxtpt.dikstra[startnode] = (newdst, currentpt)
                    todo.put((newdst, startnode, nxtpt))
                if not None in nxtpt.dikstra:
                    # we have finally met in a point, stop here
                    centerpoint = nxtpt
                    break
            if centerpoint is not None:
                break

         if centerpoint is None:
            

        

    def _connect_subgraphs(self, endpoints):
        """Find the shortest connections between unconnected subgraphs.

           This algorithm leaves circular parts dangeling.
        """
        zeropnts = filter(lambda x : x, endpoints)
        netids = range(len(zeropnts))
        finalendpoints = set(endpoints)
        # compute all possible connections
        connections = []
        for frmnet in range(len(zeropnts)):
            for tonet in range(len(zeropnts)):
                conn = [frmnet, None, tonet, None, float("inf")]
                if frmnet != tonet:
                    for frmpnt in zeropnts[frmnet]:
                        for topnt in zeropnts[tonet]:
                            pdist = frmpnt.distance_to(topnt)
                            if pdist < conn[4]:
                                conn[1] = frmpnt
                                conn[3] = topnt
                                conn[4] = pdist
                connections.append(conn)
        # sort by distance
        connections.sort(cmp=lambda x,y: cmp(x[4], y[4]),reverse=True)

        # now keep connecting until we have a single graph
        for (frmnet, frmpt, tonet, topt, dist) in connections:
            # add the virtual connection
            geom = LineString(frmpt.coords, topt.coords)
            segment = ProfileSegment(-1, [], geom, frmpt.nodeid, topt.nodeid)
            frmpt.edges.append(segment)
            frmpt.neighbours.append(topt.nodeid)
            topt.edges.append(segment)
            topt.neighbours.append(frmpt.nodeid)
            # remove final points
            finalendpoints.remove(topt.nodeid)
            finalendpoints.remove(frmpt.nodeid)
            # and join the nets
            oldsubid = netids[tonet]
            newsubid = netids[frmnet]
            if oldsubid != newsubid:
                netids = [newsubid if x == oldsubid else x for x in netids]

            # are we done yet?
            if len(filter(lambda x: x == netids[0], netids)) == len(netids):
                break
                            
        return finalendpoints


    def _mark_subgraphs(self):
        """Go through the net and mahr for each point to which subgraph
           it belongs. Returns all points that are end points.
        """
        subnet = 0
        endpoints = []
        subnetendpoints = []
        for pnt in self.nodes:
            if len(pnt.edges) == 1:
                subnetendpoints.append(pnt) 
            if pnt.subnet < 0:
                todo = set(pnt)
                while todo:
                    nxt = todo.pop()
                    nxt.subnet = subnet
                    todo.update(nxt.neighbours)
                subnet += 1
                endpoints.append(subnetendpoints)
                subnetendpoints = []
                
        return endpoints

import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
class ConsolidatedVoronoi():
    def __init__(self, points):
        vor = Voronoi(points)
        self.points = vor.points
        self.vertices = vor.vertices
        self.ridge_points = vor.ridge_points
        self.ridge_vertices = vor.ridge_vertices
        self.regions = vor.regions
        self.point_region = vor.point_region
        self.furthest_site = vor.furthest_site
        self.consolidate()
    def consolidate(self):
        consolidated_vertices = []
        for vertex in self.vertices:
            inserted = False
            for vertex_2 in self.vertices:
                if np.linalg.norm(vertex-vertex_2)> 0 and np.linalg.norm(vertex-vertex_2) < 20:
                    #print("consolidating vertix: " + str(vertex) + " and: "+ str(vertex_2))
                    consolidated_vertices.append((vertex+vertex_2)/2)
                    inserted = True
                    break
            if not inserted:
                consolidated_vertices.append(vertex)
        self.vertices = np.asarray(consolidated_vertices)
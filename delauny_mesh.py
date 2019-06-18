"""
Mesh functions
"""

from copy import copy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import path
from scipy.spatial import qhull


def _isinside(point, polygon, tolerance=0):
    if isinstance(polygon, (list, np.ndarray)):
        poly = path.Path(polygon)
        return poly.contains_point(point, radius=tolerance)
    raise ValueError("wrong function input")


def _areinside(points, polygon, tolerance=0):
    if isinstance(polygon, (list, np.ndarray)):
        poly = path.Path(polygon)
        return poly.contains_points(points, radius=tolerance)
    raise ValueError("wrong function input")


def _points_inside(outer_boundary, trimming_boundaries, mesh_size):
    xmin, ymin = np.amin(outer_boundary, axis=0)
    xmax, ymax = np.amax(outer_boundary, axis=0)
    dx = abs(xmax - xmin)
    dy = abs(ymax - ymin)
    x = np.linspace(xmin, xmax, dx / mesh_size + 1)
    y = np.linspace(ymin, ymax, dy / mesh_size + 1)
    X, Y = np.meshgrid(x, y)
    grid = np.column_stack((X.flatten(), Y.flatten()))
    indices = _areinside(
        grid, outer_boundary, -mesh_size
    )  # TODO: check the tolerance sign values...
    if trimming_boundaries is not None:
        for bound in trimming_boundaries:
            indices *= ~_areinside(grid, bound, -mesh_size) * ~_areinside(grid, bound, -mesh_size)
    return grid[indices]


def _edge_points(outer_boundary, trimming_boundaries, mesh_size):
    outer_polygon = copy(outer_boundary)
    outer_polygon.append(outer_polygon[0])
    diffs = np.abs(np.diff(outer_polygon, axis=0))
    no_points = np.amax(diffs, axis=1) / mesh_size + 1
    points = list()
    for i in range(len(outer_polygon[:-1])):
        points.extend(np.linspace(outer_polygon[i], outer_polygon[i + 1], no_points[i]).tolist())
    if trimming_boundaries is not None:
        for bound in trimming_boundaries:
            poly = copy(bound)
            poly.append(poly[0])
            diffs = np.abs(np.diff(poly, axis=0))
            no_points = np.amax(diffs, axis=1) / mesh_size + 1
            for i in range(len(poly[:-1])):
                points.extend(np.linspace(poly[i], poly[i + 1], no_points[i]).tolist())
    return np.unique(points, axis=0)


def _delauny_triangulate(outer_boundary, trimming_boundaries, inner_points, edge_points):
    tri = qhull.Delaunay(np.row_stack((inner_points, edge_points)))
    midpoints = np.mean(tri.points[tri.simplices], axis=1)
    indices = _areinside(midpoints, outer_boundary)
    if trimming_boundaries is not None:
        for bound in trimming_boundaries:
            indices *= ~_areinside(midpoints, bound)
    return tri.points, tri.simplices[indices]


def triangulate(outer_boundary, mesh_size, trimming_boundaries=None):
    """
    triangulation function

    Parameters
    ----------
    outer_boundary : array_like
        nx2 list or np.ndarray
    mesh_sizse : float
        background grid size
    trimming_boundaries : array_like
        OPTIONAL, list of (nx2 list or np.ndarray)
    """
    inner_points = _points_inside(outer_boundary, trimming_boundaries, mesh_size)
    edge_points = _edge_points(outer_boundary, trimming_boundaries, mesh_size)
    return _delauny_triangulate(outer_boundary, trimming_boundaries, inner_points, edge_points)


def plot(outer_boundary, points, triangulation_indices, trimming_boundaries=None, plot_trim=True):
    """
    plot the triangulation
    """
    fig = plt.figure()
    axes = fig.add_subplot(111)
    outer_boundary.append(outer_boundary[0])
    npouter_boundary = np.array(outer_boundary)
    axes.plot(npouter_boundary[:, 0], npouter_boundary[:, 1], lw=2, color="black")
    if trimming_boundaries is not None and plot_trim:
        for bound in trimming_boundaries:
            bound.append(bound[0])
            npbound = np.array(bound)
            axes.plot(npbound[:, 0], npbound[:, 1], lw=2, color="red")
    axes.triplot(points[:, 0], points[:, 1], triangulation_indices)
    plt.show()

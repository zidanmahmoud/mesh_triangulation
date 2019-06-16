from delauny_mesh import triangulate, plot

bckgrnd = [
    [0, 0],
    [20, 0],
    [20, 10],
    [0, 10]
]
trm1 = [
    [2.5, 0],
    [2.5, 8],
    [8, 4],
    [12, 4],
    [17.5, 8],
    [17.5, 0],
]
trm2 = [
    [2.5, 10],
    [10, 5],
    [17.5, 10],
]
mesh_size = 0.5

shape = bckgrnd
trimm = [trm1, trm2]

points, triangulation_indices = triangulate(shape, mesh_size, trimm)
plot(shape, points, triangulation_indices, trimm, False)
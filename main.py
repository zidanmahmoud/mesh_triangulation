from delauny_mesh import triangulate, plot

nonconvex = [[0, 0], [0, 10], [20, 10], [20, 0], [10, -10], [10, 0]]
trimming_bound = [[12.25, 7.25], [17.25, 7.25], [17.25, 2.25], [12.25, 2.25]]
mesh_size = 0.5

shape = nonconvex
trimm = [trimming_bound]

points, triangulation_indices = triangulate(shape, mesh_size, trimm)
plot(shape, points, triangulation_indices, trimm, True)

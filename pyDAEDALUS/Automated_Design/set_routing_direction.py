import numpy as np
from networkx.algorithms.simple_paths import all_simple_paths


def pick_longest_path(paths):
    return max(list(paths), key=len)


def dereference_pseudonodes_in_path(path_with_pseudonodes, pseudo_vert):
    path_with_only_real_nodes = []
    for node in path_with_pseudonodes:
        dereferenced = pseudo_vert[node]
        path_with_only_real_nodes.append(dereferenced)
    return path_with_only_real_nodes


def check_direction(route_real, vert_to_face, faces):
    """
        Since faces are originally given in counterclockwise order, comparing
    a sure-to-be-face-part-of-a-face's order to an arbitrary face will let you
    know if the current ordering is clockwise or counterclockwise.  Return
    False if the former and True if the latter.
    """

    # every face has at least three nodes and three is enough to detect
    # direction, so only grab first three
    first_face_route = np.array(route_real[0:3])

    # should just have one overlapping face
    vtf_1 = vert_to_face[first_face_route[0]]
    vtf_2 = vert_to_face[first_face_route[1]]
    vtf_3 = vert_to_face[first_face_route[2]]
    first_face_ID = set(vtf_1)\
        .intersection(set(vtf_2))\
        .intersection(set(vtf_3)).pop()

    first_face = faces[first_face_ID]

    check_cycle = first_face + first_face
    correct_direction = 0
    for check in range(len(first_face)):  # faces were given initially as
        excerpt_to_check = check_cycle[check:(check + 3)]
        distance = np.linalg.norm(first_face_route - excerpt_to_check)
        if distance == 0:  # that is, if there is a match
            correct_direction = correct_direction + 1

    # 0->wrong direction.  1->right direction. 2 or more -> should never
    assert correct_direction < 2

    if correct_direction == 0:  # routing is clockwise, wrong direction
        return False
    else:
        return True


def set_routing_direction(edge_type_mat_allNodes, num_vert, pseudo_vert,
                          faces, vert_to_face):
    """
    Sets routing direction for traversing scaffold route path

    Parameters
    ----------
    edge_type_mat_allNodes : networkx.classes.digraph.DiGraph
        Network representation including link types.  Link types have the
        following possible values:
            -1 is half of a non-spanning tree edge (one side of scaffold
            crossover)
            2 is spanning tree edge: DX edge with 0 scaffold crossovers
    num_vert : int
        number of vertices, V
    pseudo_vert : list
        row vector where value j at index i indicate that
        vertex i corresponds to vertex j, one of the V real vertices
    faces : list
        List of lists.  The first dimension represents the face.  The
        second dimension holds the index all nodes creating that face.
    vert_to_face : list
        List of lists.  The first dimension represents the node.  The
        second dimension holds the index of all faces that node is a part of.

    Returns
    -------
    route_real
        row vector of vertices listed in visitation order (only real vertex
        IDs)
    route_vals
        row vector of edge types, where the value at index j in route_vals is
        the edge type of the edge between the vertices route_real(j:j+1),
        wrapping around at end
    """

    # Choose a starting connected node (arbitrary start position).
    # Vertices #1-#V (V = number of vertices) are no longer connected in the
    # graph network
    start_node = 2*num_vert+2  # this node is a pseudo-node at Vertex 1

    next_nodes = edge_type_mat_allNodes.neighbors(start_node)  # you'll have 2
    # TODO: Convert to generator, since you only need to make the second
    # path if the first is the wrong direction?
    for next_node in next_nodes:
        paths = all_simple_paths(
            edge_type_mat_allNodes, start_node, next_node)

        # you'll have one 1-length path because they're neighbors.  You want
        # the other path that includes all the other nodes:
        path = pick_longest_path(paths)

        route_real = path
        temp_route_real = route_real + [route_real[0]]
        route_vals = [edge_type_mat_allNodes
                      [temp_route_real[i]][temp_route_real[i+1]]['type']
                      for i in range(len(route_real))]

        dereferenced_path = dereference_pseudonodes_in_path(path, pseudo_vert)
        route_real = dereferenced_path

        # TODO: Review that this code is really no longer needed given how I'm
        # picking start node / generating the paths.

        # Does this differ from previous 'magic' number that picks first vert?
        # # # For consistency, start routing at a tree edge (route_vals = 2)
        # # # with Vertex 1 upstream (route_real = 1)
        # start_route = (i for i in range(len(route_real)) \
        #     if route_real[i] == 1 and route_vals[i] == 2)
        # start_route = intersect(find(route_real == 1), find(route_vals == 2))
        # start_route = start_route(1) # in case there are multiple choices
        #
        # # # Shift route_real and route_vals to start at start_route
        # route_real = [route_real[start_route:end], route_real[0:start_route]]
        # route_vals = [route_vals(start_route:end), \
        #     route_vals(1:start_route-1)]

        if check_direction(route_real, vert_to_face, faces):
            return [route_real, route_vals]

    raise Exception("one of the two above should have returned")

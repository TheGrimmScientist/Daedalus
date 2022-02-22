def split_edge(edge_type_mat):
    """
    Add two nodes for each nontree edge to implement scaffold crossovers.
    Added nodes (pseudo-vertices) have a reference vertex (one of the V real
    vertices) to maintain relative spatial coordinates among all
    vertices.

    Parameters
    ----------
    edge_type_mat : networkx.classes.digraph.DiGraph
        sparse matrix where
            1 is non-spanning tree edge: DX edge with 1 scaffold crossover
            2 is spanning tree edge: DX edge with 0 scaffold crossovers
    Returns
    -------
    edge_type_mat_wHalfs
        VxV sparse matrix where
            -1 is half of a non-spanning tree edge (one side of scaffold
            crossover)
            2 is spanning tree edge: DX edge with 0 scaffold crossovers
    pseudo_vert
        row vector where value j at index i indicate that vertex i corresponds
        to vertex j, one of the V real vertices
    """
    # # Initialize output variables. These will be augmented from input vars
    edge_type_mat_wHalfs = edge_type_mat.copy()

    # Start with known nodes.  Pseudo nodes added to graph as needed.
    pseudo_vert = edge_type_mat_wHalfs.nodes()

    non_tree_edges = [edge for edge in edge_type_mat.edges(data=True)
                      if edge[2]['type'] == 1]

    # # ID non-tree edges (value 1), replace with 2 half-edges (value = -1)
    # edges = edge_type_mat.edges()
    # for i in range(num_vert):
    #     for j in range(num_vert):
    #         if (i, j) in edges:
    #             properties = edge_type_mat[i][j]
    #             if properties['type'] == 1:
    # !! replace the next two lines with the above 6 if you want an exact
    # match with the matlab code.  (else, order of pseudonodes not assured)
    for edge in non_tree_edges:
        i, j, properties = edge
        # `i` is the node that stays. `j` is cut off and replaced by pseudo
        # vert.  Since this digraph was built from a graph, a link from 2, 3
        # will also have a link from 3, 2.  Meaning in the 2, 3 case, you'll
        # keep 2 and replace 3.  And in teh 3, 2 case, you'll keep 3 and
        # replace 2.

        index_of_new_vert = len(pseudo_vert)
        properties['type'] = -1

        pseudo_vert.append(j)  # vert_list[new_node_id] = original_node_id
        edge_type_mat_wHalfs.remove_edge(i, j)

        edge_type_mat_wHalfs.add_node(index_of_new_vert)
        edge_type_mat_wHalfs.add_edge(i, index_of_new_vert,
                                      attr_dict=properties)
        edge_type_mat_wHalfs.add_edge(index_of_new_vert, i,
                                      attr_dict=properties)

    return edge_type_mat_wHalfs, pseudo_vert

# Since we're not using this class at the moment but I was finished writing
# it so I'm keeping it in this separate module for now in case we ever want
# it back.


class TaxCalcErrorChecker(object):
    """
    Class used for checking labels for errors with use of a directed graph.
    Some thing to do in future: set np.allclose as local.
    """

    def __init__(self, exp_results, totaldf, graph_file):
        # set up the DFs for comparison
        self.gold_std = exp_results
        self.reshape_len = len(exp_results)
        self.new_results = totaldf

        # read in network graph
        from networkx.readwrite import json_graph
        import json
        json_data = json.load(open(graph_file))
        self.Graph = json_graph.node_link_graph(json_data)

        # set up related node lookup functions
        self.ancestors = self.look_up_relatives(nx.ancestors)
        self.descendants = self.look_up_relatives(nx.descendants)

    def __contains__(self, label):
        return self.Graph.has_node(label)

    def check_for_errors(self, label, tol=1e-02):
        '''Checks a particular label for errors against the setup used to
        initiate the class.
        Naturally expects some label as argument. Optionally accepts custom
        tolerance cutoff value.
        '''
        if not self.check_match(label, tol):
            ancestors = self.ancestors(label, True, tol=tol)
            descendants = self.descendants(label, True, tol=tol)
            raise TaxCalcMismatchError(label, ancestors, descendants)

    def check_match(self, label, tol=1e-02):
        '''Function checks if values for a label in the gold standard
        match those in a new set of results within the tolerance threshold
        set by tol.
        '''
        lhs = self.gold_std[label].values.reshape(self.reshape_len)
        rhs = self.new_results[label].values.reshape(self.reshape_len)
        return np.allclose(lhs, rhs, atol=tol)

    def look_up_relatives(self, method):
        '''This function simply sets up a way to lookup relatives of a node
        in a graph.
        It currrently accepts any valid networkx tree traversal method
        such as networkx.ancestors or networkx.descendants
        '''

        def lookup_inner(label, original=False, tol=1e-02):
            '''This function actually does the work of recursively searching
            the graph and building a list of related nodes.
            '''
            if original:
                relatives = []
                match = False
            else:
                match = self.check_match(label, tol)
                if match:
                    return []
                else:
                    relatives = [match]

            if not match:
                for rel_lbl in method(self.Graph, label):
                    relatives += self.lookup_inner(rel_lbl, tol=tol)

            return relatives

        return lookup_inner

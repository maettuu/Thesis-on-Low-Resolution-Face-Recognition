####################################################
#                                                  #
#                 Global Variables                 #
#                                                  #
####################################################

# define categories
rank_list_comparison = ["mueller2010", "mueller2013", "schroff", "kendall", "scipy_kendall", "weighted_kendall",
                        "spearman", "wartmann_parametric"]
standardization_comparison = ["braycurtis", "canberra", "chebyshev", "cityblock", "cosine", "euclidean",
                              "minkowski", "sqeuclidean"]


####################################################
#                                                  #
#                  Helper Methods                  #
#                                                  #
####################################################

# used to assign category
def get_category(comparison_method):
    if comparison_method in rank_list_comparison:
        return "rank-list-comparison"
    elif comparison_method in standardization_comparison:
        return "standardization_comparison"
    else:
        return ""

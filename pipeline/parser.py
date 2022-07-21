####################################################
#                                                  #
#                     Imports                      #
#                                                  #
####################################################

import argparse
from helpers.categories import get_rank_list_comparison, get_standardization_comparison

####################################################
#                                                  #
#               Parser Definition                  #
#                                                  #
####################################################

# define choices for arguments
# available_protocols = ["close", "medium", "far", "combined", "IR"]
available_protocols = ["close", "medium", "far", "all"]
available_methods = ["baseline", "mueller2010", "mueller2013", "schroff", "wartmann", "kendall", "scipy_kendall",
                     "weighted_kendall", "spearman", "braycurtis", "canberra", "chebyshev", "cityblock", "cosine",
                     "euclidean", "minkowski", "sqeuclidean", "rank_list_comparison",
                     "standardization_comparison", "all"]
available_standardization = ["standardize", "subtract_mean", "omitted"]

# used to filter non-existent methods
categorical_arguments = ["rank_list_comparison", "standardization_comparison", "all"]


def parse_input():
    # initiate parser to record arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Calculate recognition rate given a database'
    )

    # add arguments
    parser.add_argument("--comparison_method", "-c",
                        default="all",
                        choices=available_methods,
                        help="Select the comparison method"
                        )
    parser.add_argument("--protocol", "-p",
                        default="all",
                        choices=available_protocols,
                        help="Select the protocol used for the comparison"
                        )
    parser.add_argument("--standardization_method", "-s",
                        default="standardize",
                        choices=available_standardization,
                        help="Select the standardization method (if standardization_comparison is chosen)"
                        )
    parser.add_argument("--enable_bigger_cohort", "-bc",
                        action='store_true',
                        help="Include to use bigger cohort"
                        )
    parser.set_defaults(enable_bigger_cohort=False)
    parser.add_argument("--record_output", "-r",
                        action='store_true',
                        help="Include to record scores"
                        )
    parser.set_defaults(record_output=False)

    # extract arguments from parser
    args = parser.parse_args()

    return args.comparison_method, args.protocol, args.standardization_method, \
           args.enable_bigger_cohort, args.record_output


####################################################
#                                                  #
#                  Helper Methods                  #
#                                                  #
####################################################

# used to filter methods
def filter_methods(methods, methods_to_filter):
    return [method for method in methods if method not in methods_to_filter]


# used to create list of chosen protocol and method
def generate_lists(comparison_method, protocol):
    if comparison_method not in categorical_arguments:
        comparison_methods = [comparison_method]
    else:
        # filter out categories and "all"
        comparison_methods = filter_methods(available_methods, categorical_arguments)
        # filter out all standardization methods
        if comparison_method == "rank_list_comparison":
            comparison_methods = filter_methods(comparison_methods, get_standardization_comparison())
        # filter out all rank list methods
        elif comparison_method == "standardization_comparison":
            comparison_methods = filter_methods(comparison_methods, get_rank_list_comparison())

    if protocol == "all":
        available_protocols.remove("all")
        protocols = available_protocols
    else:
        protocols = [protocol]

    return comparison_methods, protocols

####################################################
#                                                  #
#                     Imports                      #
#                                                  #
####################################################

import argparse


####################################################
#                                                  #
#               Parser Definition                  #
#                                                  #
####################################################

# define choices for arguments
# available_protocols = ["close", "medium", "far", "combined", "IR"]
available_protocols = ["close", "medium", "far", "all"]
available_methods = ["baseline", "mueller2010", "mueller2013", "schroff", "kendall", "scipy_kendall",
                     "weighted_kendall", "spearman", "wartmann_parametric", "braycurtis", "canberra", "chebyshev",
                     "cityblock", "correlation", "cosine", "euclidean", "minkowski", "sqeuclidean", "all"]


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
    parser.add_argument("--record_output", "-r",
                        action='store_true',
                        help="Include to record scores"
                        )
    parser.set_defaults(record_output=False)

    # extract arguments from parser
    args = parser.parse_args()

    return args.comparison_method, args.protocol, args.record_output


# used to create list of chosen protocol and method
def generate_lists(comparison_method, protocol):
    if comparison_method == "all":
        available_methods.remove("all")
        comparison_methods = available_methods
    else:
        comparison_methods = [comparison_method]

    if protocol == "all":
        available_protocols.remove("all")
        protocols = available_protocols
    else:
        protocols = [protocol]

    return comparison_methods, protocols

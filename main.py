####################################################
#                                                  #
#                     Imports                      #
#                                                  #
####################################################

import argparse
from setup import start_comparison

####################################################
#                                                  #
#               Parser Definition                  #
#                                                  #
####################################################

# initiate parser to record arguments
parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description='Calculate recognition rate given a database'
)

# define choices for arguments
# available_protocols = ["close", "medium", "far", "combined", "IR"]
available_protocols = ["close", "medium", "far", "all"]
available_methods = ["baseline",
                     "mueller2010", "mueller2013", "schroff",
                     "kendall", "scipy_kendall", "weighted_kendall", "spearman",
                     "wartmann_parametric",
                     "braycurtis", "canberra", "chebyshev", "cityblock",
                     "correlation", "cosine", "euclidean",
                     "minkowski", "sqeuclidean",
                     "all"]

# define categories
rank_list_approach = ["mueller2010", "mueller2013", "schroff",
                      "kendall", "scipy_kendall", "weighted_kendall", "spearman",
                      "wartmann_parametric"]
mean_shifted_approach = ["braycurtis", "canberra", "chebyshev", "cityblock",
                         "correlation", "cosine", "euclidean",
                         "minkowski", "sqeuclidean"]

# add arguments
parser.add_argument("--protocol", "-p",
                    default="all",
                    choices=available_protocols,
                    help="Select the protocol used for the comparison"
                    )
parser.add_argument("--comparison_method", "-c",
                    default="all",
                    choices=available_methods,
                    help="Select the comparison method"
                    )
parser.add_argument("--record_output", "-r",
                    action='store_true',
                    help="Include to record scores"
                    )
parser.set_defaults(record_output=False)

# extract arguments from parser
args = parser.parse_args()


####################################################
#                                                  #
#                  Helper Methods                  #
#                                                  #
####################################################

# used to assign category
def set_category(curr_comparison_method):
    if curr_comparison_method in rank_list_approach:
        return "rank-list"
    elif curr_comparison_method in mean_shifted_approach:
        return "mean-shifted"
    else:
        return ""


####################################################
#                                                  #
#              Command Line Execution              #
#                                                  #
####################################################

# read chosen protocol and recognition method from parser
protocol = args.protocol
comparison_method = args.comparison_method
record_output = args.record_output

# assign protocol as list argument
protocol_args = [protocol]

if protocol == "all":
    # remove "all" from options to avoid running non-existent protocol
    available_protocols.remove("all")
    protocol_args = available_protocols

if comparison_method == "all":
    # remove "all" from options to avoid running non-existent method
    available_methods.remove("all")

    # start comparison for each method
    for method in available_methods:
        category = set_category(method)
        start_comparison(method, record_output, category, *protocol_args)


else:
    category = set_category(comparison_method)
    start_comparison(comparison_method, record_output, category, *protocol_args)

####################################################
#                                                  #
#                Helpful Commands                  #
#                                                  #
####################################################

# bin/python main.py -c baseline -r
# bin/bob bio pipelines vanilla-biometrics scface-close iresnet100 -c --group eval
# bin/bob bio pipelines vanilla-biometrics scface-close iresnet100 -vvv -o example_result -c
# bin/bob bio roc -v -o medium.pdf -ts "results medium protocol" -lg baseline,mueller2010,mueller2013,schroff,wartmann medium-baseline.csv medium-mueller2010.csv medium-mueller2013.csv medium-schroff.csv medium-wartmann_parametric.csv
# bin/bob bio pipelines vanilla-biometrics scface-close ./simple_pipe.py -vvv -o samples_pipe_all -c --group eval
# bin/bob bio evaluate ./results/scores-dev.csv
# open hdf5 files using terminal "h5dump -y file.hdf5"

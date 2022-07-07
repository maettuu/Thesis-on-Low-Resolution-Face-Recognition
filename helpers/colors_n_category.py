####################################################
#                                                  #
#                   Color Class                    #
#                                                  #
####################################################

# used to color output text
class Colors:
    CRED = '\33[31m'
    CCYAN = '\33[36m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


####################################################
#                                                  #
#                 Global Variables                 #
#                                                  #
####################################################

# define categories
rank_list_comparison = ["mueller2010", "mueller2013", "schroff", "kendall", "scipy_kendall", "weighted_kendall",
                        "spearman", "wartmann_parametric"]
mean_shifted_comparison = ["braycurtis", "canberra", "chebyshev", "cityblock", "cosine", "euclidean",
                           "minkowski", "sqeuclidean"]


####################################################
#                                                  #
#                  Helper Methods                  #
#                                                  #
####################################################

# used to output beginning of new comparison
def print_start(category, comparison_method, protocol):
    msg = f"Currently running {Colors.BOLD}{Colors.CRED}[" + category + "]" + comparison_method + \
          f"{Colors.ENDC} with protocol {Colors.CCYAN}" + protocol + f"{Colors.ENDC} ..."
    print(f'{Colors.BOLD}INFO: {Colors.ENDC}{msg:{115}}', end='', flush=True)


# used to assign category
def get_category(comparison_method):
    if comparison_method in rank_list_comparison:
        return "rank-list-comparison"
    elif comparison_method in mean_shifted_comparison:
        return "mean-shifted-comparison"
    else:
        return ""

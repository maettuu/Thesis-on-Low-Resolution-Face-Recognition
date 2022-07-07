####################################################
#                                                  #
#                     Imports                      #
#                                                  #
####################################################

from parser import parse_input, generate_lists
from helper import get_category, print_start
from preprocessing import run_preprocessing
from comparison import run_comparison


####################################################
#                                                  #
#                   Execution                      #
#                                                  #
####################################################

if __name__ == '__main__':
    comparison_methods, protocols, record_output = parse_input()
    comparison_methods, protocols = generate_lists(comparison_methods, protocols)

    for comparison_method in comparison_methods:
        category = get_category(comparison_method)
        for protocol in protocols:
            print_start(category, comparison_method, protocol)
            probe_samples, reference_samples = run_preprocessing(category, protocol)
            run_comparison(probe_samples, reference_samples, category, comparison_method, protocol, record_output)
            print("DONE!")


####################################################
#                                                  #
#                Helpful Commands                  #
#                                                  #
####################################################

# bin/python main.py -c baseline -p close -r
# bin/bob bio roc -v -o results.pdf baseline.csv
# bin/bob bio pipelines vanilla-biometrics scface-close ./simple_pipe.py -vvv -o samples_pipe_all -c --group eval
# bin/bob bio evaluate ./results/scores-dev.csv
# h5dump -y file.h5

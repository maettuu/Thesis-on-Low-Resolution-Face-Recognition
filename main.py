####################################################
#                                                  #
#                     Imports                      #
#                                                  #
####################################################

from pipeline.parser import parse_input, generate_lists
from pipeline.preprocessing import run_preprocessing
from pipeline.comparison import run_comparison
from helpers.colors import print_colorful_start
from helpers.categories import get_category


####################################################
#                                                  #
#                   Execution                      #
#                                                  #
####################################################

if __name__ == '__main__':
    comparison_methods, protocols, standardization_method, enable_larger_cohort, record_output = parse_input()
    comparison_methods, protocols = generate_lists(comparison_methods, protocols)

    for comparison_method in comparison_methods:
        category = get_category(comparison_method)
        for protocol in protocols:
            print_colorful_start(category, comparison_method, protocol, enable_larger_cohort)
            probe_samples, gallery_samples = run_preprocessing(
                category, protocol, standardization_method, enable_larger_cohort
            )
            run_comparison(probe_samples, gallery_samples, category, comparison_method, protocol, record_output)
            print("DONE!")


####################################################
#                                                  #
#                Helpful Commands                  #
#                                                  #
####################################################

# bin/python main.py -c baseline -p close -r
# bin/bob bio roc -v -o results.pdf baseline.csv
# bin/bob bio pipelines vanilla-biometrics scface-close ./simple_pipe.py -vvv -o samples_pipe_all -c --group eval
# bin/bob bio pipelines vanilla-biometrics scface-close iresnet100
# bin/bob bio evaluate ./results/scores-dev.csv
# h5dump -y file.h5

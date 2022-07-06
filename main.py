from parser import parse_input, generate_list

if __name__ == '__main__':
    # parse command line input
    protocols, comparison_methods, record_output = parse_input()
    protocols, comparison_methods = generate_list(protocols, comparison_methods)

    # for comparison_method in comparison_methods:



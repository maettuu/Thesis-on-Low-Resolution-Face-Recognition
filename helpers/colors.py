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
#                  Helper Methods                  #
#                                                  #
####################################################

# used to output beginning of new comparison
def print_colorful_start(category, comparison_method, protocol):
    msg = f"Currently running {Colors.BOLD}{Colors.CRED}[" + category + "]" + comparison_method + \
          f"{Colors.ENDC} with protocol {Colors.CCYAN}" + protocol + f"{Colors.ENDC} ..."
    print(f'{Colors.BOLD}INFO: {Colors.ENDC}{msg:{115}}', end='', flush=True)

####################################################
#                                                  #
#                   Color Class                    #
#                                                  #
####################################################

# used to color output text
class Colors:
    CRED = '\33[31m'
    CCYAN = '\33[36m'
    YELLOW = '\33[33m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


####################################################
#                                                  #
#                  Helper Methods                  #
#                                                  #
####################################################

# used to output beginning of new comparison
def print_colorful_start(category, comparison_method, protocol, enable_larger_cohort):
    msg = f"Currently running {Colors.BOLD}{Colors.CRED}[" + category + "]" + comparison_method + \
          f"{Colors.ENDC} with protocol {Colors.CCYAN}" + protocol + f"{Colors.ENDC} on "
    if enable_larger_cohort:
        msg = msg + f"{Colors.YELLOW}large{Colors.ENDC} cohort ..."
        print(f'{Colors.BOLD}INFO: {Colors.ENDC}{msg:{145}}', end='', flush=True)
    else:
        msg = msg + f"{Colors.YELLOW}small{Colors.ENDC} cohort ..."
        print(f'{Colors.BOLD}INFO: {Colors.ENDC}{msg:{145}}', end='', flush=True)

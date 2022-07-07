####################################################
#                                                  #
#                     Imports                      #
#                                                  #
####################################################

import csv
import pathlib


####################################################
#                                                  #
#                 Global Variables                 #
#                                                  #
####################################################

scores_dev = None
scores_writer = None
recognition_file = None


####################################################
#                                                  #
#                   File Writing                   #
#                                                  #
####################################################

# used to create data files
def file_creation(comparison_method, protocol, record_output):
    # initialize file helpers
    global scores_dev
    global scores_writer
    global recognition_file

    if record_output:
        # create output directory
        pathlib.Path("output").mkdir(exist_ok=True)

        # filename consists of protocol and comparison method (e.g. close-baseline.csv)
        filename = protocol + "-" + comparison_method + ".csv"
        scores_dev = open("output/" + filename, 'w')
        scores_writer = csv.writer(scores_dev)
        scores_header = ['probe_reference_id', 'probe_subject_id',
                         'bio_ref_reference_id', 'bio_ref_subject_id', 'score']
        # add header
        scores_writer.writerow(scores_header)

        # file for recognition rates and runtime, create if non-existent
        recognition_file = open("output/recognition-rates-and-runtime.txt", 'a+')
        # seek to beginning of file and check for content
        recognition_file.seek(0)

        # add header if file is empty (i.e. was newly created),
        # otherwise close and re-open to set cursor to end of file
        if not recognition_file.readlines():
            recognition_file.write(f'{"comparison_method":{20}} {"close_recog_rate":{20}} {"medium_recog_rate":{20}}'
                                   f' {"far_recog_rate":{20}} {"runtime"}\n')
        else:
            recognition_file.close()
            recognition_file = open("output/recognition-rates-and-runtime.txt", 'a')


# used to save similarity scores from each comparison
def save_scores(data):
    if scores_writer:
        scores_writer.writerow(data)


# used to print recognition rate and runtime of close protocol
def close(comparison_method, recognition_rate, runtime):
    if recognition_file:
        recognition_file.write(f'{comparison_method:{20}} {recognition_rate:{20}} {"":{20}} {"":{20}} {runtime}\n')


# used to print recognition rate and runtime of medium protocol
def medium(comparison_method, recognition_rate, runtime):
    if recognition_file:
        recognition_file.write(f'{comparison_method:{20}} {"":{20}} {recognition_rate:{20}} {"":{20}} {runtime}\n')


# used to print recognition rate and runtime of far protocol
def far(comparison_method, recognition_rate, runtime):
    if recognition_file:
        recognition_file.write(f'{comparison_method:{20}} {"":{20}} {"":{20}} {recognition_rate:{20}} {runtime}\n')


# used to extract protocol and print at correct position
def save_results(comparison_method, protocol, recognition_rate, runtime):
    format_type = eval(protocol)
    format_type(comparison_method, recognition_rate, runtime)


# used to close all files
def close_files():
    global scores_dev
    global recognition_file
    if scores_dev:
        scores_dev.close()
    if recognition_file:
        recognition_file.close()

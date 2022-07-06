####################################################
#                                                  #
#                     Imports                      #
#                                                  #
####################################################

import csv
import pathlib


####################################################
#                                                  #
#                   File Writing                   #
#                                                  #
####################################################

# used to create data files
def file_creation(protocol, chosen_method, record_output):
    # initialize file helpers
    scores_dev = None
    scores_writer = None
    recognition_file = None

    if record_output:
        # create output directory
        pathlib.Path("output").mkdir(exist_ok=True)

        # filename consists of protocol and comparison method (e.g. close-baseline.csv)
        filename = protocol + "-" + chosen_method + ".csv"
        scores_dev = open("output/" + filename, 'w')
        scores_writer = csv.writer(scores_dev)
        scores_header = ['probe_reference_id', 'probe_subject_id', 'bio_ref_reference_id', 'bio_ref_subject_id', 'score']
        # add header
        scores_writer.writerow(scores_header)

        # file for recognition rates and runtime, create if non-existent
        recognition_file = open("output/recognition-rates-and-runtime.txt", 'a+')
        # seek to beginning of file and check for content
        recognition_file.seek(0)

        # add header if file is empty (i.e. was newly created), otherwise close and re-open to set cursor to end of file
        if not recognition_file.readlines():
            recognition_file.write(f'{"comparison_method":{20}} {"close_recog_rate":{20}} {"medium_recog_rate":{20}} {"far_recog_rate":{20}} {"runtime"}\n')
        else:
            recognition_file.close()
            recognition_file = open("output/recognition-rates-and-runtime.txt", 'a')

    return scores_dev, scores_writer, recognition_file


# used to print recognition rate and runtime of close protocol
def close(recognition_file, comparison_method, recognition_rate, runtime):
    recognition_file.write(f'{comparison_method:{20}} {recognition_rate:{20}} {"":{20}} {"":{20}} {runtime}\n')


# used to print recognition rate and runtime of medium protocol
def medium(recognition_file, comparison_method, recognition_rate, runtime):
    recognition_file.write(f'{comparison_method:{20}} {"":{20}} {recognition_rate:{20}} {"":{20}} {runtime}\n')


# used to print recognition rate and runtime of far protocol
def far(recognition_file, comparison_method, recognition_rate, runtime):
    recognition_file.write(f'{comparison_method:{20}} {"":{20}} {"":{20}} {recognition_rate:{20}} {runtime}\n')


# used to extract protocol and print at correct position
def save_recognition_and_runtime(recognition_file, comparison_method, recognition_rate, runtime, protocol):
    format_type = eval(protocol)
    format_type(recognition_file, comparison_method, recognition_rate, runtime)

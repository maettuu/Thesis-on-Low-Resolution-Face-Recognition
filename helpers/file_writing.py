####################################################
#                                                  #
#                     Imports                      #
#                                                  #
####################################################

import csv
import pathlib


####################################################
#                                                  #
#                    Data Class                    #
#                                                  #
####################################################

# used to keep track of rates of same comparison method
class RecognitionItem:
    def __init__(self, close_rate="", medium_rate="", far_rate="",
                 close_runtime=None, medium_runtime=None, far_runtime=None):
        self.close_rate = close_rate
        self.medium_rate = medium_rate
        self.far_rate = far_rate
        self.close_runtime = close_runtime
        self.medium_runtime = medium_runtime
        self.far_runtime = far_runtime

    def get_average_runtime(self):
        if self.close_runtime and self.medium_runtime and self.far_runtime:
            return (self.close_runtime + self.medium_runtime + self.far_runtime) / 3
        elif self.close_runtime and self.medium_runtime:
            return (self.close_runtime + self.medium_runtime) / 2
        elif self.medium_runtime:
            return self.medium_runtime
        elif self.far_runtime:
            return self.far_runtime


####################################################
#                                                  #
#                 Global Variables                 #
#                                                  #
####################################################

scores_dev = None
scores_writer = None
recognition_file = None
current_recognition = RecognitionItem()


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


# used to turn runtime into string
def to_string_runtime(runtime):
    return ("{:.4f}".format(runtime * 1000)) + " ms"


# used to print recognition rate and runtime of close protocol
def close(comparison_method, recognition_rate, runtime):
    if recognition_file:
        global current_recognition
        current_recognition.close_rate = recognition_rate
        current_recognition.close_runtime = runtime
        runtime = to_string_runtime(runtime)
        recognition_file.write(f'{comparison_method:{20}} {recognition_rate:{20}} {"":{20}} {"":{20}} {runtime}\n')


# used to print recognition rate and runtime of medium protocol
def medium(comparison_method, recognition_rate, runtime):
    if recognition_file:
        global current_recognition
        current_recognition.medium_rate = recognition_rate
        current_recognition.medium_runtime = runtime
        average_runtime = to_string_runtime(current_recognition.get_average_runtime())
        recognition_file.write(f'{comparison_method:{20}} {current_recognition.close_rate:{20}} '
                               f'{recognition_rate:{20}} {"":{20}} {average_runtime}\n')


# used to print recognition rate and runtime of far protocol
def far(comparison_method, recognition_rate, runtime):
    if recognition_file:
        global current_recognition
        current_recognition.far_rate = recognition_rate
        current_recognition.far_runtime = runtime
        average_runtime = to_string_runtime(current_recognition.get_average_runtime())
        recognition_file.write(f'{comparison_method:{20}} {current_recognition.close_rate:{20}} '
                               f'{current_recognition.medium_rate:{20}} {recognition_rate:{20}} {average_runtime}\n')
        current_recognition = RecognitionItem()


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

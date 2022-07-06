####################################################
#                                                  #
#                     Imports                      #
#                                                  #
####################################################

import bob.bio.face
import bob.io.base
import bob.extension
from comparison import run_comparison
import numpy as np
import scipy.spatial
import pathlib


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
#                 Path Declaration                 #
#                                                  #
####################################################

# used to combine with sample keys and load features
file_path = str(pathlib.Path().resolve())
directory_path = file_path + "/samples_pipe_all/samplewrapper-2/"

# used to define original_directory
bob.extension.rc["bob.bio.face.scface.directory"] = directory_path

# used for mean shifted lists of cosine distances
reference_theta = 1
probe_theta = 1


####################################################
#                                                  #
#                Data Preprocessing                #
#                                                  #
####################################################

# used to split cohort samples into cohort probes and cohort references
def split_cohort(cohort_samples, protocol):
    # instantiate lists for cohort probes and cohort references
    cohort_probes = []
    cohort_references = {}

    for sample in cohort_samples:
        # extract the 'capture' attribute
        curr_capture = sample.capture

        # check capture to distinguish between probes and references
        if str(curr_capture) == 'surveillance':
            # check for the protocol used when defining the database
            if str(sample.distance) == protocol:
                cohort_probes.append(sample)
        elif str(curr_capture) == 'mugshot':
            cohort_references[sample.subject_id] = sample.features

    return cohort_probes, cohort_references


# used to take the average of all features from samples with the same subject_id
def average_features_with_same_subject_id(cohort_probes):

    # instantiate dictionary for subjects with several features
    subjects_with_several_features = {}

    # loop through samples and extract features of all samples with the same subject_id
    for sample in cohort_probes:
        curr_subject_id = sample.subject_id
        # add entry if subject_id is not yet in dictionary, else extract already recorded features and add current ones
        if curr_subject_id not in subjects_with_several_features:
            subjects_with_several_features[curr_subject_id] = [sample.features]
        else:
            subjects_with_several_features.get(curr_subject_id).append(sample.features)

    # instantiate dictionary for subjects w/ averaged features
    averaged_features = {}

    # loop through subjects with several features to calculate the average
    for subject_id, features in subjects_with_several_features.items():
        # calculate the average of all features
        curr_average_features = np.mean(features, axis=0)
        # add average to dictionary
        averaged_features[subject_id] = curr_average_features

    return averaged_features


# used to preprocess the cohort samples (splitting samples and taking average of features)
def preprocess_cohort(cohort_samples, protocol):
    cohort_probes, cohort_reference = split_cohort(cohort_samples, protocol)
    cohort_averaged_features = average_features_with_same_subject_id(cohort_probes)

    return cohort_averaged_features, cohort_reference


####################################################
#                                                  #
#                  Helper Methods                  #
#                                                  #
####################################################

# load features of single sample
def load_features(sample):
    sample_key = sample.key
    # add file extension to key
    new_sample_key = sample_key + ".h5"
    # try loading from destination
    try:
        sample_features = bob.io.base.load(directory_path + new_sample_key)
        sample.features = sample_features
    # switch to back-up if file not found
    except RuntimeError:
        print(f"\n{Colors.BOLD}{Colors.CRED}WARNING:{Colors.ENDC} File '%s' not found!\n\n{Colors.BOLD}{Colors.CRED}PROCESS TERMINATED{Colors.ENDC}" % new_sample_key)
        exit()

    return sample


# used to loop through samples and assign each with its features
def assign_sample_features(image_set, including_set=True):
    if including_set:
        for sample_set in image_set:
            for sample in sample_set:
                load_features(sample)
    else:
        for sample in image_set:
            load_features(sample)

    return image_set


# used to extract samples for sample sets
def extract_samples(image_set, collected_samples):
    for sample_set in image_set:
        if len(sample_set) > 1:
            print(f"{Colors.BOLD}{Colors.CRED}WARNING:{Colors.ENDC} More than one sample in '%s'!" % sample_set)
        for sample in sample_set:
            collected_samples.append(sample)


# used to extract probes, references and cohort from database
def run_extraction(extraction_protocol):
    # define database using chosen protocol
    database = bob.bio.face.database.SCFaceDatabase(extraction_protocol)

    # several samples pointing to same reference_id, but must be looked at separately
    # extract probes, references and cohorts from database
    extracted_probes = database.probes()
    # probes = database.probes(group="eval")

    extracted_references = database.references()
    # references = database.references(group="eval")

    extracted_cohort = database.background_model_samples()
    # cohort = database.references(group="dev") + database.probes(group="dev")

    return extracted_probes, extracted_references, extracted_cohort


# used to assign features and extract samples from sample sets
def run_preprocessing(probes_to_process, references_to_process, cohort_to_process, category, protocol):
    # assign features for probe and reference samples
    processed_probes = assign_sample_features(probes_to_process)
    processed_references = assign_sample_features(references_to_process)
    all_cohort_samples = assign_sample_features(cohort_to_process, including_set=False)

    # extract and save samples (cohort does not include sets, therefore this step is omitted)
    all_probe_samples = []
    all_reference_samples = []
    extract_samples(processed_probes, all_probe_samples)
    extract_samples(processed_references, all_reference_samples)

    # used to differentiate between calculation approach
    run_baseline = True

    # preprocess cohort and generate rank lists/cosine distances
    if category:
        run_baseline = False
        cohort_averaged_features, cohort_reference = preprocess_cohort(all_cohort_samples, protocol)
        if category == "rank-list":
            generate_rank_list(all_probe_samples, cohort_averaged_features)
            generate_rank_list(all_reference_samples, cohort_reference)
        elif category == "mean-shifted":
            # loop through probes and get cosine distances to cohort, from which the mean is subtracted
            for probe_sample in all_probe_samples:
                cosine_distances = get_cosine_distances(probe_sample, cohort_averaged_features)
                probe_sample.cosine_distances = np.divide(np.subtract(cosine_distances, np.mean(cosine_distances)),
                                                          probe_theta)
            # loop through references and get cosine distances to cohort, from which the mean is subtracted
            for reference_sample in all_reference_samples:
                cosine_distances = get_cosine_distances(reference_sample, cohort_reference)
                reference_sample.cosine_distances = np.divide(
                    np.subtract(cosine_distances, np.mean(cosine_distances)), reference_theta)

    return all_probe_samples, all_reference_samples, all_cohort_samples, run_baseline


# used to calculate cosine distances between one probe and all references (used for cohort)
def get_cosine_distances(probe_sample, reference_samples):
    # instantiate list for calculated cosine distances between probe sample and all reference samples
    cosine_distances = []

    for key in sorted(reference_samples.keys()):
        # calculate and save cosine distance between probe and current reference sample
        cosine_distances.append(
            scipy.spatial.distance.cosine(probe_sample.features, reference_samples[key])
        )

    return np.array(cosine_distances)


# used to convert cosine distances into rank lists
def generate_rank_list(probe_samples, reference_samples):
    for probe_sample in probe_samples:
        cosine_distances = get_cosine_distances(probe_sample, reference_samples)
        # use argsort to convert into array of orders
        order = np.argsort(cosine_distances)
        # use argsort again to convert into sorted array indices (rank list) and add it to probe sample
        probe_sample.rank_list = np.argsort(order)


####################################################
#                                                  #
#                    Algorithm                     #
#                                                  #
####################################################

# used to set up comparison before execution (extraction and preprocessing)
def start_comparison(comparison_method, record_output, category, *protocols):
    # loop through selected protocol(s)
    for curr_protocol in protocols:
        # output current status to show process is still running
        msg = f"Currently running {Colors.BOLD}{Colors.CRED}[" + category + "]" + comparison_method + \
              f"{Colors.ENDC} with protocol {Colors.CCYAN}" + curr_protocol + f"{Colors.ENDC} ..."
        print(f'{Colors.BOLD}INFO: {Colors.ENDC}{msg:{100}}', end='', flush=True)

        probes, references, cohort = run_extraction(curr_protocol)
        probe_samples, reference_samples, cohort_samples, run_baseline = run_preprocessing(probes, references, cohort, category, curr_protocol)

        run_comparison(comparison_method, run_baseline, curr_protocol, probe_samples, reference_samples, record_output)

        # update process status
        print("DONE!")

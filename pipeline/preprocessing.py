####################################################
#                                                  #
#                     Imports                      #
#                                                  #
####################################################

import bob.bio.face
import bob.io.base
import numpy as np
import scipy.spatial
import pathlib
import time
from helpers.colors import Colors
from helpers.file_writing import set_preprocess_time
from pipeline.comparison import set_schroff_k


####################################################
#                                                  #
#                 Path Declaration                 #
#                                                  #
####################################################

# used to combine with sample keys and load features
file_path = str(pathlib.Path().resolve())
directory_path = file_path + "/samples_pipe_all/samplewrapper-2/"


####################################################
#                                                  #
#                  Helper Methods                  #
#                                                  #
####################################################

# used to extract probes, gallery and cohort from database
def extract_samples(protocol, enable_larger_cohort):
    # define database using chosen protocol and extract samples
    database = bob.bio.face.database.SCFaceDatabase(protocol)
    probes = database.probes()
    gallery = database.references()
    cohort = database.background_model_samples()

    if enable_larger_cohort:
        cohort = cohort + database.references(group="eval") + database.probes(group="eval")

    return probes, gallery, cohort


# load features of single sample
def load_features(sample):
    sample_key = sample.key
    # add file extension to key
    new_sample_key = sample_key + ".h5"
    # try loading from destination
    try:
        sample_features = bob.io.base.load(directory_path + new_sample_key)
        sample.features = sample_features
    # terminate if file not found
    except RuntimeError:
        print(f"\n{Colors.BOLD}{Colors.CRED}WARNING:{Colors.ENDC} File '%s' not found!\n\n"
              f"{Colors.BOLD}{Colors.CRED}PROCESS TERMINATED{Colors.ENDC}" % new_sample_key)
        exit()

    return sample


# used to loop through samples and assign each with its features
def assign_features(image_set, including_set=True):
    if including_set:
        for sample_set in image_set:
            for sample in sample_set:
                load_features(sample)
    else:
        for sample in image_set:
            load_features(sample)

    return image_set


# used to extract samples for sample sets
def unwrap_sets(image_set, collected_samples):
    for sample_set in image_set:
        if len(sample_set) > 1:
            print(f"{Colors.BOLD}{Colors.CRED}WARNING:{Colors.ENDC} More than one sample in '%s'!" % sample_set)
        for sample in sample_set:
            collected_samples.append(sample)


# used to split cohort samples into cohort probes and cohort gallery
def split_cohort(cohort_samples, protocol):
    # instantiate dictionaries for probe and gallery cohort samples
    cohort_probes = {}
    cohort_gallery = {}

    for sample in cohort_samples:
        # extract the ’capture’ attribute
        curr_capture = sample.capture

        # check capture to distinguish between probe and gallery cohort
        if str(curr_capture) == "surveillance":
            # check for the protocol used when defining the database
            if str(sample.distance) == protocol:
                curr_subject_id = sample.subject_id
                # add an entry if subject_id is not yet in the dictionary
                if curr_subject_id not in cohort_probes:
                    cohort_probes[curr_subject_id] = [sample.features]
                # else extract already recorded features and add current ones
                else:
                    cohort_probes.get(curr_subject_id).append(sample.features)
        elif str(curr_capture) == "mugshot":
            cohort_gallery[sample.subject_id] = sample.features

    return cohort_probes, cohort_gallery


# used to take the average of all features from samples with the same subject_id
def calculate_average(cohort_probes):
    # instantiate dictionary for subjects w/ averaged features
    averaged_features = {}

    # loop through subjects with several features to calculate the average
    for subject_id, features in cohort_probes.items():
        # calculate the average of all features
        curr_average_features = np.mean(features, axis=0)
        # add average to dictionary
        averaged_features[subject_id] = curr_average_features

    return averaged_features


# used to calculate cosine distances between one probe/gallery and cohort
def get_cosine_distances(sample, cohort_samples):
    # instantiate list for calculated cosine distances between sample and all cohort samples
    cosine_distances = []

    for key in sorted(cohort_samples.keys()):
        # calculate and save cosine distance between sample and current cohort sample
        cosine_distances.append(
            scipy.spatial.distance.cosine(sample.features, cohort_samples[key])
        )

    return np.array(cosine_distances)


# used to convert cosine distances into rank lists
def generate_rank_list(samples, cohort_samples):
    for sample in samples:
        cosine_distances = get_cosine_distances(sample, cohort_samples)
        # use argsort to convert into array of orders
        order = np.argsort(cosine_distances)
        # use argsort again to convert into rank list and add it to sample
        sample.rank_list = np.argsort(order)


# used to standardize lists with cosine distances
def standardize(samples, cohort_samples):
    for sample in samples:
        cosine_distances = get_cosine_distances(sample, cohort_samples)
        # subtract mean from list and divide by standard deviation
        sample.standardized_distances = np.divide(np.subtract(cosine_distances, np.mean(cosine_distances)),
                                                  np.std(cosine_distances))


# used to subtract mean from lists with cosine distances
def subtract_mean(samples, cohort_samples):
    for sample in samples:
        cosine_distances = get_cosine_distances(sample, cohort_samples)
        # subtract mean from list
        sample.standardized_distances = np.subtract(cosine_distances, np.mean(cosine_distances))


# used to omit standardization
def omitted(samples, cohort_samples):
    for sample in samples:
        cosine_distances = get_cosine_distances(sample, cohort_samples)
        # directly assign without standardization
        sample.standardized_distances = cosine_distances


####################################################
#                                                  #
#                    Algorithm                     #
#                                                  #
####################################################

# used to set up comparison before execution (extraction and preprocessing)
def run_preprocessing(category, protocol, standardization_method, enable_larger_cohort):
    probes, gallery, cohort = extract_samples(protocol, enable_larger_cohort)
    probes = assign_features(probes)
    gallery = assign_features(gallery)

    # unwrap samples
    probe_samples = []
    gallery_samples = []
    unwrap_sets(probes, probe_samples)
    unwrap_sets(gallery, gallery_samples)

    # category is defined -> cohort must be used
    if category:
        # used for measuring preprocessing time
        start_time_cpu = time.process_time()

        cohort = assign_features(cohort, including_set=False)
        cohort_probes, cohort_gallery = split_cohort(cohort, protocol)
        # several samples in cohort_probes refer to the same subject,
        # therefore features must be averaged
        cohort_probes_averaged = calculate_average(cohort_probes)

        # usage of rank lists -> generate rank lists
        if category == "rank-list-comparison":
            generate_rank_list(probe_samples, cohort_probes_averaged)
            generate_rank_list(gallery_samples, cohort_gallery)

            # stop and save time measurement
            stop_time_cpu = time.process_time()
            preprocess_time = stop_time_cpu - start_time_cpu
            set_preprocess_time("rank-list", protocol, preprocess_time)

            # optimize schroff parameter
            set_schroff_k(len(cohort_probes_averaged))

        # usage of lists w/o converting to rank -> standardize lists
        elif category == "standardization_comparison":
            standardization_function = eval(standardization_method)
            standardization_function(probe_samples, cohort_probes_averaged)
            standardization_function(gallery_samples, cohort_gallery)

            # stop and save time measurement
            stop_time_cpu = time.process_time()
            preprocess_time = stop_time_cpu - start_time_cpu
            set_preprocess_time(standardization_method, protocol, preprocess_time)
    else:
        set_preprocess_time("baseline", protocol, 0)

    return probe_samples, gallery_samples

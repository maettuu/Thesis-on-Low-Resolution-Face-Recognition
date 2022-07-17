####################################################
#                                                  #
#                     Imports                      #
#                                                  #
####################################################

import bob.bio.face
import bob.io.base
import bob.extension
import numpy as np
import scipy.spatial
import pathlib
from helpers.colors import Colors


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


####################################################
#                                                  #
#                 Global Variables                 #
#                                                  #
####################################################

# used for weighting normalizing lists (standard score)
reference_theta = 1
probe_theta = 1


####################################################
#                                                  #
#                  Helper Methods                  #
#                                                  #
####################################################

# used to extract probes, gallery and cohort from database
def extract_samples(protocol):
    # define database using chosen protocol
    database = bob.bio.face.database.SCFaceDatabase(protocol)

    # several samples pointing to same reference_id, but must be looked at separately
    # extract probes, gallery and cohorts from database
    probes = database.probes()
    # probes = database.probes(group="eval")

    gallery = database.references()
    # gallery = database.references(group="eval")

    cohort = database.background_model_samples()
    # cohort = database.references(group="dev") + database.probes(group="dev")

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
    # instantiate lists for cohort probes and cohort gallery
    cohort_probes = []
    cohort_gallery = {}

    for sample in cohort_samples:
        # extract the 'capture' attribute
        curr_capture = sample.capture

        # check capture to distinguish between probes and gallery
        if str(curr_capture) == 'surveillance':
            # check for the protocol used when defining the database
            if str(sample.distance) == protocol:
                cohort_probes.append(sample)
        elif str(curr_capture) == 'mugshot':
            cohort_gallery[sample.subject_id] = sample.features

    return cohort_probes, cohort_gallery


# used to take the average of all features from samples with the same subject_id
def calculate_average(samples):

    # instantiate dictionary for subjects with several features
    subjects_with_several_features = {}

    # loop through samples and extract features of all samples with the same subject_id
    for sample in samples:
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


# used to calculate cosine distances between one probe/gallery and cohort
def get_cosine_distances(sample, reference_samples):
    # instantiate list for calculated cosine distances between sample and all cohort samples
    cosine_distances = []

    for key in sorted(reference_samples.keys()):
        # calculate and save cosine distance between sample and current cohort sample
        cosine_distances.append(
            scipy.spatial.distance.cosine(sample.features, reference_samples[key])
        )

    return np.array(cosine_distances)


# used to convert cosine distances into rank lists
def generate_rank_list(samples, reference_samples):
    for sample in samples:
        cosine_distances = get_cosine_distances(sample, reference_samples)
        # use argsort to convert into array of orders
        order = np.argsort(cosine_distances)
        # use argsort again to convert into sorted array indices (rank list) and add it to probe sample
        sample.rank_list = np.argsort(order)


# used to standardize lists with cosine distances
def standardize(samples, reference_samples, theta):
    for sample in samples:
        cosine_distances = get_cosine_distances(sample, reference_samples)
        # subtract mean from list and divide by standard deviation
        sample.standardized_distances = np.divide(np.subtract(cosine_distances, np.mean(cosine_distances)),
                                                  theta)


####################################################
#                                                  #
#                    Algorithm                     #
#                                                  #
####################################################

# used to set up comparison before execution (extraction and preprocessing)
def run_preprocessing(category, protocol):
    probes, gallery, cohort = extract_samples(protocol)
    probes = assign_features(probes)
    gallery = assign_features(gallery)

    # unwrap samples
    probe_samples = []
    gallery_samples = []
    unwrap_sets(probes, probe_samples)
    unwrap_sets(gallery, gallery_samples)

    # category is defined -> cohort must be used
    if category:
        cohort = assign_features(cohort, including_set=False)
        cohort_probes, cohort_gallery = split_cohort(cohort, protocol)
        # several samples in cohort_probes refer to the same subject,
        # therefore features must be averaged
        cohort_probes_averaged = calculate_average(cohort_probes)

        # usage of rank lists -> generate rank lists
        if category == "rank-list-comparison":
            generate_rank_list(probe_samples, cohort_probes_averaged)
            generate_rank_list(gallery_samples, cohort_gallery)

        # usage of lists w/o converting to rank -> standardize lists
        elif category == "standardization_comparison":
            standardize(probe_samples, cohort_probes_averaged, probe_theta)
            standardize(gallery_samples, cohort_gallery, reference_theta)

    return probe_samples, gallery_samples

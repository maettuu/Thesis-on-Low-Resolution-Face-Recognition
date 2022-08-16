####################################################
#                                                  #
#                     Imports                      #
#                                                  #
####################################################

import math
import numpy as np
import scipy.spatial
import scipy.stats
import time
from helpers.file_writing import file_creation, save_scores, save_results, close_files


####################################################
#                                                  #
#                 Global Variables                 #
#                                                  #
####################################################


# used for rank list comparison methods
mueller2013_lambda = 0.99
schroff_k = 43
wartmann_alpha = 1
wartmann_beta = 1
minkowski_p = 2


# setter for schroff_k
def set_schroff_k(value):
    global schroff_k
    schroff_k = value


####################################################
#                                                  #
#                Comparison Methods                #
#                                                  #
####################################################

# used to calculate cosine distances between one probe and all gallery samples (used for baseline)
def baseline(probe_sample, gallery_samples):
    # instantiate list for calculated cosine distances between probe sample and all gallery samples
    cosine_distances = []

    for gallery_sample in gallery_samples:
        # calculate and save cosine distance between probe and current gallery sample
        cosine_distance = scipy.spatial.distance.cosine(probe_sample.features, gallery_sample.features)
        cosine_distances.append(cosine_distance)

        data = [probe_sample.reference_id, probe_sample.subject_id,
                gallery_sample.reference_id, gallery_sample.subject_id,
                -cosine_distance]
        # save to external spreadsheet to determine VP
        save_scores(data)

    return -np.array(cosine_distances)


####################################################
#                                                  #
#                 Rank List Method                 #
#                                                  #
####################################################

# compute similarity of two rank lists with the help of mueller's formula 2010
def mueller2010(probe_sample, gallery_sample):
    # initialize score
    similarity_score = 0
    # loop through rank lists and compute similarity
    for probe_rank, gallery_rank in zip(probe_sample.rank_list, gallery_sample.rank_list):
        similarity_score += 1 / math.sqrt(probe_rank + gallery_rank + 1)

    return similarity_score


# compute similarity of two rank lists with the help of mueller's formula 2013
def mueller2013(probe_sample, gallery_sample):
    # initialize score
    similarity_score = 0
    # loop through rank lists and compute similarity
    for probe_rank, gallery_rank in zip(probe_sample.rank_list, gallery_sample.rank_list):
        similarity_score += mueller2013_lambda ** (probe_rank + gallery_rank)

    return similarity_score


# compute similarity of two rank lists with the help of schroff's formula
def schroff(probe_sample, gallery_sample):
    # initialize score
    similarity_score = 0
    # loop through rank lists and compute similarity
    for probe_rank, gallery_rank in zip(probe_sample.rank_list, gallery_sample.rank_list):
        similarity_score += max(schroff_k + 1 - probe_rank, 0) * max(schroff_k + 1 - gallery_rank, 0)

    return similarity_score


# OWN KENDALL IMPLEMENTATION
# compute similarity of two rank lists with the help of kendall's tau
# def kendall(probe_sample, gallery_sample):
#     number_of_ranks = len(probe_sample.rank_list)
#     probe_sample_rank_list = probe_sample.rank_list.tolist()
#     # initialize sigma and objective ranking
#     sigma = 0
#     objective_ranking = [*range(number_of_ranks)]
#     # calculate score for each rank and add it to sigma (last rank results in zero score hence is omitted)
#     for rank in range(number_of_ranks - 1):
#         # element in gallery rank list at same index as current rank in probe rank list
#         pivot = gallery_sample.rank_list[probe_sample_rank_list.index(rank)]
#         pivot_index = objective_ranking.index(pivot)
#         # subtract elements left of pivot from elements right of pivot in objective ranking for score
#         sigma += (len(objective_ranking) - 1) - (2 * pivot_index)
#         # remove pivot from objective ranking
#         objective_ranking.remove(pivot)
#
#     # calculate kendall's tau
#     return (2 * sigma) / (number_of_ranks * (number_of_ranks - 1))


# compute similarity of two rank lists with the help of kendall's tau (scipy)
def kendall(probe_sample, gallery_sample):
    tau, _ = scipy.stats.kendalltau(probe_sample.rank_list, gallery_sample.rank_list)

    return tau


# compute similarity of two rank lists with the help of kendall's weighted tau
def weighted_kendall(probe_sample, gallery_sample):
    tau, _ = scipy.stats.weightedtau(probe_sample.rank_list, gallery_sample.rank_list)

    return tau


# compute similarity of two rank lists with the help of spearman's formula
def spearman(probe_sample, gallery_sample):
    return scipy.stats.spearmanr(probe_sample.rank_list, gallery_sample.rank_list).correlation


# compute similarity of two rank lists with the help of wartmann's parametric formula
def wartmann(probe_sample, gallery_sample):
    number_of_ranks = len(probe_sample.rank_list)
    # initialize score
    similarity_score = 0
    # loop through rank lists and compute similarity
    for probe_rank, gallery_rank in zip(probe_sample.rank_list, gallery_sample.rank_list):
        similarity_score += ((abs(probe_rank - gallery_rank) / number_of_ranks) ** wartmann_alpha) * \
                            ((abs((probe_rank / (number_of_ranks * 0.5)) - 1) ** wartmann_beta) +
                             (abs((gallery_rank / (number_of_ranks * 0.5)) - 1) ** wartmann_beta))

    return -similarity_score


####################################################
#                                                  #
#              Standardization Method              #
#                                                  #
####################################################

# compute similarity of two lists with the help of braycurtis distance
def braycurtis(probe_sample, gallery_sample):
    return -scipy.spatial.distance.braycurtis(probe_sample.standardized_distances, gallery_sample.standardized_distances)


# compute similarity of two lists with the help of canberra distance
def canberra(probe_sample, gallery_sample):
    return -scipy.spatial.distance.canberra(probe_sample.standardized_distances, gallery_sample.standardized_distances)


# compute similarity of two lists with the help of cityblock distance
def cityblock(probe_sample, gallery_sample):
    return -scipy.spatial.distance.cityblock(probe_sample.standardized_distances, gallery_sample.standardized_distances)


# compute similarity of two lists with the help of cosine distance
def cosine(probe_sample, gallery_sample):
    return -scipy.spatial.distance.cosine(probe_sample.standardized_distances, gallery_sample.standardized_distances)


# compute similarity of two lists with the help of minkowski distance
def minkowski(probe_sample, gallery_sample):
    return -scipy.spatial.distance.minkowski(probe_sample.standardized_distances, gallery_sample.standardized_distances, minkowski_p)


# compute similarity of two lists with the help of sqeuclidean distance
def sqeuclidean(probe_sample, gallery_sample):
    return -scipy.spatial.distance.sqeuclidean(probe_sample.standardized_distances, gallery_sample.standardized_distances)


####################################################
#                                                  #
#                  Helper Methods                  #
#                                                  #
####################################################

# used to calculate similarity scores between one probe and all gallery samples
def get_similarity_scores(probe_sample, gallery_samples, comparison_function):
    # instantiate list for calculated similarity scores between
    # probe sample rank list and all gallery sample rank lists
    similarity_scores = []

    for gallery_sample in gallery_samples:
        similarity_score = comparison_function(probe_sample, gallery_sample)
        # append the score to the list
        similarity_scores.append(similarity_score)

        data = [probe_sample.reference_id, probe_sample.subject_id,
                gallery_sample.reference_id, gallery_sample.subject_id,
                similarity_score]
        # save to external spreadsheet to determine VP
        save_scores(data)

    return np.array(similarity_scores)


# used to see whether the correct gallery sample is paired with the current probe sample
def get_match_result(probe_sample, gallery_sample):
    # return 1 for positive matches (if the subject_ids are the same)
    if probe_sample.subject_id == gallery_sample.subject_id:
        return 1

    return 0


####################################################
#                                                  #
#                    Algorithm                     #
#                                                  #
####################################################

# used to run comparison with chosen method
def run_comparison(probe_samples, gallery_samples, category, comparison_method, protocol, record_output):
    # used to record output
    file_creation(comparison_method, protocol, record_output)

    # assign default function to variable for computation
    comparison_function = eval(comparison_method)

    # used to keep track of positive matches (equal subject_id for probe and gallery sample)
    positive_matches = 0

    # used for measuring runtime
    start_time_cpu = time.process_time()

    if not category:  # run baseline -> direct comparison
        for probe_sample in probe_samples:
            result = baseline(probe_sample, gallery_samples)
            # find maximum score and compare IDs for IP
            max_score_index = np.argmax(result)
            positive_matches += get_match_result(probe_sample, gallery_samples[max_score_index])
    else:  # makes use of preprocessed rank/standardized lists
        for probe_sample in probe_samples:
            result = get_similarity_scores(probe_sample, gallery_samples, comparison_function)
            # find maximum score and compare IDs for IP
            max_score_index = np.argmax(result)
            positive_matches += get_match_result(probe_sample, gallery_samples[max_score_index])

    # stop runtime measurement
    stop_time_cpu = time.process_time()
    runtime = stop_time_cpu - start_time_cpu

    # calculate recognition rate by dividing positive matches by total amount of probes
    recognition_rate = positive_matches / len(probe_samples)

    # save recognition rate and runtime before closing files
    if record_output:
        recognition_rate = "{:.2f}".format(recognition_rate * 100)
        save_results(comparison_method, protocol, recognition_rate, runtime)
        close_files()

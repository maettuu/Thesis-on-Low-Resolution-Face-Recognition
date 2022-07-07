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
wartmann_alpha = 1.5
wartmann_beta = 5


####################################################
#                                                  #
#                Comparison Methods                #
#                                                  #
####################################################

# used to calculate cosine distances between one probe and all references (used for baseline)
def baseline(probe_sample, reference_samples):
    # instantiate list for calculated cosine distances between probe sample and all reference samples
    cosine_distances = []

    for reference_sample in reference_samples:
        # calculate and save cosine distance between probe and current reference sample
        cosine_distance = scipy.spatial.distance.cosine(probe_sample.features, reference_sample.features)
        cosine_distances.append(cosine_distance)

        data = [probe_sample.reference_id, probe_sample.subject_id,
                reference_sample.reference_id, reference_sample.subject_id,
                -cosine_distance]
        save_scores(data)

    return -np.array(cosine_distances)


####################################################
#                                                  #
#                Rank List Approach                #
#                                                  #
####################################################

# compute similarity of two rank lists with the help of mueller's formula 2010
def mueller2010(probe_sample, reference_sample):
    # initialize score
    similarity_score = 0
    # loop through rank lists and compute similarity
    for probe_rank, reference_rank in zip(probe_sample.rank_list, reference_sample.rank_list):
        similarity_score += 1 / math.sqrt(probe_rank + reference_rank + 1)

    return similarity_score


# compute similarity of two rank lists with the help of mueller's formula 2013
def mueller2013(probe_sample, reference_sample):
    # initialize score
    similarity_score = 0
    # loop through rank lists and compute similarity
    for probe_rank, reference_rank in zip(probe_sample.rank_list, reference_sample.rank_list):
        similarity_score += mueller2013_lambda ** (probe_rank + reference_rank)

    return similarity_score


# compute similarity of two rank lists with the help of schroff's formula
def schroff(probe_sample, reference_sample):
    # initialize score
    similarity_score = 0
    # loop through rank lists and compute similarity
    for probe_rank, reference_rank in zip(probe_sample.rank_list, reference_sample.rank_list):
        similarity_score += max(schroff_k + 1 - probe_rank, 0) * max(schroff_k + 1 - reference_rank, 0)

    return similarity_score


# compute similarity of two rank lists with the help of kendall's tau
def kendall(probe_sample, reference_sample):
    number_of_ranks = len(probe_sample.rank_list)
    probe_sample_rank_list = probe_sample.rank_list.tolist()
    # initialize sigma and objective ranking
    sigma = 0
    objective_ranking = [*range(number_of_ranks)]
    # calculate score for each rank and add it to sigma (last rank results in zero score hence is omitted)
    for rank in range(number_of_ranks - 1):
        # element in reference rank list at same index as current rank in probe rank list
        pivot = reference_sample.rank_list[probe_sample_rank_list.index(rank)]
        pivot_index = objective_ranking.index(pivot)
        # subtract elements left of pivot from elements right of pivot in objective ranking for score
        sigma += (len(objective_ranking) - 1) - (2 * pivot_index)
        # remove pivot from objective ranking
        objective_ranking.remove(pivot)

    # calculate kendall's tau
    return (2 * sigma) / (number_of_ranks * (number_of_ranks - 1))


# compute similarity of two rank lists with the help of kendall's tau (scipy)
def scipy_kendall(probe_sample, reference_sample):
    tau, _ = scipy.stats.kendalltau(probe_sample.rank_list, reference_sample.rank_list)

    return tau


# compute similarity of two rank lists with the help of kendall's weighted tau
def weighted_kendall(probe_sample, reference_sample):
    tau, _ = scipy.stats.weightedtau(probe_sample.rank_list, reference_sample.rank_list)

    return tau


# compute similarity of two rank lists with the help of spearman's formula
def spearman(probe_sample, reference_sample):
    return scipy.stats.spearmanr(probe_sample.rank_list, reference_sample.rank_list).correlation


# compute similarity of two rank lists with the help of wartmann's parametric formula
def wartmann_parametric(probe_sample, reference_sample):
    number_of_ranks = len(probe_sample.rank_list)
    # initialize score
    similarity_score = 0
    # loop through rank lists and compute similarity
    for probe_rank, reference_rank in zip(probe_sample.rank_list, reference_sample.rank_list):
        similarity_score += ((abs(probe_rank - reference_rank) / number_of_ranks) ** wartmann_alpha) * \
                            ((abs((probe_rank / (number_of_ranks * 0.5)) - 1) ** wartmann_beta) +
                             (abs((reference_rank / (number_of_ranks * 0.5)) - 1) ** wartmann_beta))

    return -similarity_score


####################################################
#                                                  #
#               Mean Shifted Approach              #
#                                                  #
####################################################

# compute similarity of two lists with the help of braycurtis distance
def braycurtis(probe_sample, reference_sample):
    return -scipy.spatial.distance.braycurtis(probe_sample.cosine_distances, reference_sample.cosine_distances)


# compute similarity of two lists with the help of canberra distance
def canberra(probe_sample, reference_sample):
    return -scipy.spatial.distance.canberra(probe_sample.cosine_distances, reference_sample.cosine_distances)


# compute similarity of two lists with the help of chebyshev distance
def chebyshev(probe_sample, reference_sample):
    return -scipy.spatial.distance.chebyshev(probe_sample.cosine_distances, reference_sample.cosine_distances)


# compute similarity of two lists with the help of cityblock distance
def cityblock(probe_sample, reference_sample):
    return -scipy.spatial.distance.cityblock(probe_sample.cosine_distances, reference_sample.cosine_distances)


# compute similarity of two lists with the help of correlation distance
def correlation(probe_sample, reference_sample):
    return -scipy.spatial.distance.correlation(probe_sample.cosine_distances, reference_sample.cosine_distances)


# compute similarity of two lists with the help of cosine distance
def cosine(probe_sample, reference_sample):
    return -scipy.spatial.distance.cosine(probe_sample.cosine_distances, reference_sample.cosine_distances)


# compute similarity of two lists with the help of euclidean distance
def euclidean(probe_sample, reference_sample):
    return -scipy.spatial.distance.euclidean(probe_sample.cosine_distances, reference_sample.cosine_distances)


# compute similarity of two lists with the help of minkowski distance
def minkowski(probe_sample, reference_sample):
    return -scipy.spatial.distance.minkowski(probe_sample.cosine_distances, reference_sample.cosine_distances, 2)


# compute similarity of two lists with the help of sqeuclidean distance
def sqeuclidean(probe_sample, reference_sample):
    return -scipy.spatial.distance.sqeuclidean(probe_sample.cosine_distances, reference_sample.cosine_distances)


####################################################
#                                                  #
#                  Helper Methods                  #
#                                                  #
####################################################

# used to calculate similarity scores between one probe and all references
def get_similarity_scores(probe_sample, reference_samples, category, comparison_function):
    if not category:
        return comparison_function(probe_sample, reference_samples)
    else:
        # instantiate list for calculated similarity scores between
        # probe sample rank list and all reference sample rank lists
        similarity_scores = []

        for reference_sample in reference_samples:
            similarity_score = comparison_function(probe_sample, reference_sample)
            # append the score to the list
            similarity_scores.append(similarity_score)

            data = [probe_sample.reference_id, probe_sample.subject_id,
                    reference_sample.reference_id, reference_sample.subject_id,
                    similarity_score]
            save_scores(data)

        return np.array(similarity_scores)


# used to see whether the correct reference sample is paired with the current probe sample
def get_match_result(probe_sample, reference_sample):
    # return 1 for positive matches (if the subject_ids are the same)
    if probe_sample.subject_id == reference_sample.subject_id:
        return 1

    return 0


####################################################
#                                                  #
#                    Algorithm                     #
#                                                  #
####################################################

# used to run comparison with chosen method
def run_comparison(probe_samples, reference_samples, category, comparison_method, protocol, record_output):
    # used to record output
    file_creation(comparison_method, protocol, record_output)

    # assign default function to variable for computation
    comparison_function = eval(comparison_method)

    # used to keep track of positive matches (equal subject_id for probe and reference sample)
    positive_matches = 0

    # used for measuring runtime
    start_time_cpu = time.process_time()

    for probe_sample in probe_samples:
        result = get_similarity_scores(probe_sample, reference_samples, category, comparison_function)
        max_score_index = np.argmax(result)
        positive_matches += get_match_result(probe_sample, reference_samples[max_score_index])

    # stop runtime measurement
    stop_time_cpu = time.process_time()

    # calculate recognition rate by dividing positive matches by total amount of references
    recognition_rate = positive_matches / len(probe_samples)

    # save recognition rate and runtime before closing files
    if record_output:
        recognition_rate = ("{:.2f}".format(recognition_rate * 100)) + " %"
        runtime = ("{:.4f}".format((stop_time_cpu - start_time_cpu) * 1000)) + " ms"
        save_results(comparison_method, protocol, recognition_rate, runtime)
        close_files()

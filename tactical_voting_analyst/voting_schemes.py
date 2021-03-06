from enum import IntEnum
import numpy as np


class VotingScheme(IntEnum):
    plurality = 0
    vote_for_two = 1
    borda_count = 2
    anti_plurality = 3


# Can be used for plurality, vote for n, anti-plurality
def create_vote_for_n_vector(n: int, num_candidates: int):
    vec = np.zeros(num_candidates)
    vec[0:n] = 1
    return vec


# Can be used for borda count
def create_borda_count(num_candidates: int):
    return np.full(num_candidates, num_candidates) - np.arange(num_candidates) - 1

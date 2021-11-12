from voting_situation import *
from voting_schemes import *
from voter import Voter
import collections
from enum import IntEnum
import numpy as np


class VotingType(IntEnum):
    plurality = 1
    vote_for_two = 2
    borda_count = 3
    anti_plurality = 4


class TacticalVotingAnalyst:
    def __init__(
        self, candidates: np.ndarray[(5), np.int_], voters: list[Voter]
    ):
        """
        Initialisation
        :param candidates: list of objects from class 'Candidate'
        :param voters: list of objects from class 'Voter'
        """
        self.voting_shemes_names = [  # this will be mainly used for representation
            "plurality",
            "vote for 2",
            "borda count",
            "anti plurality",
        ]
        self.voting_situation = VotingSituation(candidates, voters)
        self.voting_schemes = self.create_voting_vectors(len(candidates))

    def create_voting_vectors(self, num_candidates: int) -> np.ndarray:
        """
        Create vectors for different voting schemes
        :param num_candidates: Number of candidates
        :return: Dictionary with vectors for several voting schemes
        """
        named_voting_vectors = {
            "plurality": create_vote_for_n_vector(1, num_candidates),
            "vote for 2": create_vote_for_n_vector(2, num_candidates),
            "borda count": create_borda_count(num_candidates),
            "anti plurality": create_vote_for_n_vector(
                num_candidates - 1, num_candidates
            ),
        }
        return np.array(
            [
                named_voting_vectors[voting_scheme_name]
                for voting_scheme_name in self.voting_shemes_names
            ]
        )

    def get_winner(self, voting_scheme: np.ndarray, print_winner=False) -> np.ndarray:
        """
        Determine the total number of votes per candidate according to a specific voting scheme
        :param voting_scheme: voting scheme ndarray
        :param print_winner: bool that indicates if the results from this voting scheme should be printed
        :return: ndarray of shape (len(candidates),) containing # votes for each candidate
        """
        # Create a counter for every candidate
        counter = np.zeros(len(self.voting_situation.candidates))

        # For every voter
        for voter in self.voting_situation.voters:
            # Process all preferences
            for i in range(len(voter.true_preferences[0])):
                # Add score to the counter dictionary
                counter[voter.true_preferences[0][i]] += voting_scheme[i]

        # If the user wants to print results
        #Todo: numpy-ize code bellow
        if print_winner:
            # Print voting scheme
            print("Voting Scheme - {}:".format(voting_scheme))
            i = 1
            # Print sorted results (based on decreasing votes)
            for k, v in sorted(
                counter.items(), key=lambda x: x[1], reverse=True
            ):
                print("{}) {}: {}".format(i, k, v))
                i += 1
            print()

        return counter

    def get_winners(self):
        """
        Determine the winner for all different voting schemes
        :return: Dictionary with the name of each candidate that won
        """

        # Create empty dictionary
        winners = {}

        # For every voting scheme, determine the winner
        for voting_scheme in self.voting_schemes_dict.keys():
            winner, counter = self.get_winner(voting_scheme)
            winners[voting_scheme] = winner
            self.outcome[voting_scheme] = collections.OrderedDict(
                dict(
                    sorted(
                        counter.items(), reverse=True, key=lambda item: item[1]
                    )
                )
            )

        # Return the winner
        return winners

    def create_count_dict(self):
        """
        Create a dictionary for every candidate with value 0 (for counting)
        :return: A dictionary for every candidate with value 0 (for counting)
        """
        #ToDo: do we need this function? This could be replaced by a np.zeros(len(candidates))
        counter = {}
        for candidate in self.voting_situation.candidates:
            counter[candidate.name] = 0
        return counter

    def overall_happiness(self):
        """
        Determine the overall happiness for each of the voting schemes
        """
        overall_happiness = {}
        for voting_scheme in self.voting_schemes_dict.keys():
            happiness = 0
            for voter in self.voting_situation.voters:
                happiness += voter.determine_happiness(
                    self.outcome[voting_scheme]
                )
            overall_happiness[voting_scheme] = happiness

        return overall_happiness

    # def determine_tactical_options(self, voting_scheme: str):
    #     """
    #     Determine the tactical voting options for all voters
    #     :param voting_scheme: String of selected voting scheme
    #     :return: All tactical options
    #     """
    #     # Determine outcome
    #     _, outcome = self.get_winner(voting_scheme)
    #
    #     print(outcome)
    #
    #     # Create list for tactical options
    #     tactical_options = []
    #
    #     # For every voter that is in our situation
    #     for voter in self.voting_situation.voters:
    #         # Update tactical preference
    #         voter.update_tactical_options(outcome, self.voting_situation.candidates,
    #                                       self.voting_schemes_dict, voting_scheme)
    #
    #         # Save tactical options
    #         tactical_options.append(voter.tactical_options)
    #
    #         print("Voter {}".format(voter.voter_id))
    #         if len(voter.tactical_options) > 0:
    #             for pref in voter.tactical_options:
    #                 print("Happiness: {} -> {}, preference: {}, new outcome: {}".format(pref[2],
    #                                 pref[1],
    #                                 [cand.name for cand in pref[0]],
    #                                 sorted(pref[3].items(), reverse=True, key=lambda item: item[1])))
    #         print()
    #
    #     return tactical_options
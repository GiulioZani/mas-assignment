from .happiness_schemes import HappinessScheme
from .voting_schemes import VotingScheme
import itertools
import ipdb

# from .candidate import Candidate
import numpy as np


class Voter:
    v_id = 0
    # def __init__(self, preferences: list[list[Candidate]]):
    def __init__(self, preferences: np.ndarray):
        """
        Initialise the preferences of the voter
        :param Preferences: List of objects from class Candidate
        """
        # Make disinction between true preferences and tactical preferences
        # self.true_preferences = preferences[0]
        # self.tactical_options = []
        self.voter_id = Voter.v_id
        Voter.v_id += 1

        self.true_preferences = preferences
        # self._true_preferences_array =
        self.tactical_preferences = preferences

    def determine_happiness(
        self, ranked_candidates_id: np.ndarray, happiness_scheme: HappinessScheme,
    ):
        """
        Determine self happiness
        :param happiness_scheme: type of happiness measurement
        :param ranked_candidates_id: ranked ndarray of 1 dimension
        ranked_candidates_id[1] = 3 means that candidate with id=3 ranked second in the final outcome
        """
        true_preferences = self.true_preferences
        pref_norm = np.arange(len(ranked_candidates_id))
        ranked_norm = np.arange(len(ranked_candidates_id) - 1, -1, -1)
        argsorting = np.arange(len(ranked_candidates_id))
        argsorting[ranked_norm] = argsorting.copy()
        indices = argsorting[pref_norm]
        # Count happiness
        happiness = 0

        if happiness_scheme == HappinessScheme.borda_count:
            borda_weights = np.arange(len(ranked_candidates_id) - 1, -1, -1)
            norm_value = np.dot(borda_weights, borda_weights)
            argsorting = np.arange(len(ranked_candidates_id))
            argsorting[ranked_candidates_id] = argsorting.copy()
            # the above argsorting is computed using counting sort, a sorting method that has linear time complexity, thus better than np.argsort, but effectively it does the same
            indices = argsorting[
                true_preferences
            ]  # we compose the indices to get "the position of each candidate n ranked_candidates_id in true_preferences"
            happiness = np.dot(
                borda_weights, borda_weights[indices]
            )  # multiply elementwise ans sum everything up
            # normalize
            happiness = happiness / norm_value

        elif happiness_scheme == HappinessScheme.linear_weight:
            linear_weights = np.arange(len(ranked_candidates_id), 0, -1)
            norm_value = np.dot(linear_weights, np.arange(len(pref_norm)) - indices)
            argsorting = np.arange(len(ranked_candidates_id))
            argsorting[ranked_candidates_id] = argsorting.copy()
            indices = argsorting[true_preferences]
            happiness = np.dot(
                linear_weights, np.arange(len(true_preferences)) - indices
            )
            happiness = 1 - happiness / norm_value

        elif happiness_scheme == HappinessScheme.squared_weight:
            squared_weights = np.square(np.arange(len(ranked_candidates_id), 0, -1))
            norm_value = np.dot(squared_weights, np.arange(len(pref_norm)) - indices)
            argsorting = np.arange(len(ranked_candidates_id))
            argsorting[ranked_candidates_id] = argsorting.copy()
            indices = argsorting[true_preferences]
            happiness = np.dot(
                squared_weights, np.arange(len(true_preferences)) - indices
            )
            happiness = 1 - happiness / norm_value
        elif happiness_scheme == HappinessScheme.cubed_weight:
            cubed_weights = np.power(np.arange(len(ranked_candidates_id), 0, -1), 3)
            norm_value = np.dot(cubed_weights, np.arange(len(pref_norm)) - indices)
            argsorting = np.arange(len(ranked_candidates_id))
            argsorting[ranked_candidates_id] = argsorting.copy()
            indices = argsorting[true_preferences]
            happiness = np.dot(
                cubed_weights, np.arange(len(true_preferences)) - indices
            )
            happiness = 1 - happiness / norm_value

        return happiness

    def update_tactical_options(
        self,
        outcome: np.ndarray,
        voting_scheme_vector: np.ndarray,
        voting_scheme: VotingScheme = VotingScheme.borda_count,
        happiness_scheme: HappinessScheme = HappinessScheme.borda_count,
    ):
        """
        Determine the tactical options for each votes
        :param outcome: Outcome of the real preferences
        :param voting_scheme_vector: vector of voting_scheme
        :param voting_scheme: String of selected voting scheme
        """
        # Reset tactical preferences
        self.tactical_options = []

        # Determine current happiness
        curr_happiness = self.determine_happiness(
            self.outcome_to_ranked_ids(outcome), happiness_scheme,
        )

        # Determine outcome without voter
        blank_outcome = self.remove_pref_outcome(
            outcome, self.true_preferences, voting_scheme_vector,
        )

        # For every permutation of preferences
        for perm in itertools.permutations(np.arange(len(outcome))):
            # Create an array
            perm = np.array(perm)

            # Determine new outcome
            new_outcome = self.add_pref_outcome(
                blank_outcome.copy(), perm, voting_scheme_vector
            )

            # Calculate new happiness
            new_happiness = self.determine_happiness(
                self.outcome_to_ranked_ids(new_outcome), happiness_scheme,
            )

            # If it's a better happiness, save
            if new_happiness > curr_happiness:
                self.tactical_options.append(
                    (perm, curr_happiness, new_happiness, new_outcome)
                )

        # Sort tactical options based on score
        self.tactical_options.sort(key=lambda x: -x[2])

    def remove_pref_outcome(
        self,
        outcome: np.ndarray,
        preference: np.ndarray,
        voting_scheme_vector: np.ndarray,
    ) -> np.ndarray:
        """
        Remove preference from outcome
        :param outcome: Current outcome
        :param preference: Preference to remove
        :param voting_scheme_vector: List of voting_scheme
        :return: Outcome after removing preference
        """
        outcome = outcome.copy()
        sorting_idxs = preference.argsort()
        sorted_voting_scheme = voting_scheme_vector[sorting_idxs]
        outcome -= sorted_voting_scheme
        return outcome

    def add_pref_outcome(
        self,
        outcome: np.ndarray,
        preference: np.ndarray,
        voting_scheme_vector: np.ndarray,
    ) -> np.ndarray:
        """
        Remove preference from outcome
        :param outcome: Current outcome
        :param preference: Preference to remove
        :param voting_scheme_vector: Lisrt of voting_scheme
        :return: Outcome after removing preference
        """
        sorting_idxs = np.argsort(preference)
        sorted_voting_scheme = voting_scheme_vector[sorting_idxs]
        outcome += sorted_voting_scheme
        return outcome

    def outcome_to_ranked_ids(self, outcome: np.ndarray) -> np.ndarray:
        """
        Sort outcome (based on scores) to rank ids
        :param outcome: Social outcome based on voting scheme
        :return: Ranks of each candidate (based on social outcome)
        """
        return (-outcome).argsort()

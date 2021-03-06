import numpy as np
import itertools
import matplotlib.pyplot as plt
from scipy.stats import norm
from enum import Enum
from .voting_schemes import VotingScheme
from .tactical_voting_analyst import HappinessScheme
from .tactical_voting_analyst import TacticalVotingAnalyst as TVA
import ipdb


class DistributionTypes(Enum):
    uniform = "uniform"
    two_peaks = "two_peaks"
    normal = "normal"


def init_voters(
    candidates: tuple[str, ...],
    voters_count: int = 100,
    distribution_function: DistributionTypes = DistributionTypes.normal,
    plot=False,
) -> tuple[np.ndarray, np.ndarray, tuple[tuple[str, ...]]]:
    permutations = np.array(tuple(itertools.permutations(candidates)))
    np.random.shuffle(permutations)
    xs = np.arange(len(permutations))
    std = len(permutations) / 8
    mean = len(permutations) / 2
    observations = np.array(np.zeros(len(permutations), dtype=int))
    probs = lambda x: x
    if distribution_function == DistributionTypes.normal:
        probs = norm(loc=mean, scale=std).pdf(xs)
        probs /= probs.sum()
    elif distribution_function == DistributionTypes.uniform:
        probs = np.zeros(len(xs)) + 1 / len(permutations)
    elif distribution_function == DistributionTypes.two_peaks:
        n_peaks = 2
        mean = len(permutations) / (n_peaks + 1)
        mean2 = 2 * (len(permutations) / (n_peaks + 1))
        sd = (len(permutations) / 2) / (3 * n_peaks)
        pdf_1 = norm(loc=mean, scale=sd).pdf
        pdf_2 = norm(loc=mean2, scale=sd).pdf
        probs = pdf_1(xs) + pdf_2(xs)
        probs /= probs.sum()

    observations = np.random.choice(xs, size=voters_count, p=probs)
    frequencies = np.zeros(len(permutations), dtype=int)
    for o in observations:
        frequencies[o] += 1
    if plot:
        plt.scatter(np.arange(len(frequencies)), frequencies)
        plt.xticks(
            np.arange(len(permutations)),
            tuple(f'{" ".join(p)}' for p in permutations),
            rotation=45,
            ha="right",
        )
        plt.savefig("../happiness_distribution.png")
        plt.show()
    named_observations = tuple(tuple(permutations[o]) for o in observations)
    return permutations, frequencies, named_observations


def test():
    voters_count = 200
    preferences, voter_counts, observations = init_voters(
        ("A", "B", "C", "D"),
        distribution_function=DistributionTypes.two_peaks,
        voters_count=voters_count,
        plot=True,
    )
    assert voter_counts.sum() == voters_count, "not correct"
    print(preferences)
    print(voter_counts)


def experiment():
    candidates = ("A", "B", "C", "D", "E")
    dist_types = tuple(DistributionTypes)
    happinesses = np.zeros(len(dist_types))
    count = 100
    for _ in range(count):
        for i, distribution_function in enumerate(dist_types):
            frequencies, voter_counts, observations = init_voters(
                candidates, distribution_function=distribution_function
            )
            preferences = tuple(
                tuple(candidates.index(a) for a in p) for p in observations
            )
            tva = TVA(
                candidates=np.arange(len(candidates)),
                candidate_names=candidates,
                preferences=preferences,
                verbose=False,
            )
            tva.get_winner(VotingScheme.borda_count)
            try:
                happinesses[i] += tva.overall_happiness(
                    VotingScheme.borda_count, HappinessScheme.cubed_weight
                )
            except:
                ipdb.set_trace()
            tactical_options = tva.determine_tactical_options(
                VotingScheme.borda_count, HappinessScheme.cubed_weight
            )
            """
            for i in range(3):
                print(
                    f"{tva.calculate_risk(tactical_options, VotingScheme.borda_count, HappinessScheme.cubed_weight, i)=}"
                )
            """
            # print(f"{distribution_function} Happiness:{happinesses[-1][1]}")
    happinesses /= count
    plt.bar(
        np.arange(len(happinesses)),
        happinesses,
        tick_label=[
            f'{str(ds).split(".")[1].replace("_", " ")}\nValue={happinesses[i]:.3f}'
            for i, ds in enumerate(dist_types)
        ],
    )
    plt.show()


def sample_preferences(candidates_names, distribution, n_voters):
    preferences = []
    for candidate_set in candidates_names:
        frequencies, voter_counts, observations = init_voters(
            candidate_set, distribution_function=distribution, voters_count=n_voters
        )

        preferences_ = tuple(
            tuple(candidate_set.index(a) for a in p) for p in observations
        )
        preferences.append(preferences_)

    return preferences


if __name__ == "__main__":
    experiment()
    # test()

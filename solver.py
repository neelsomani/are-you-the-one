"""Solver for the show 'Are You the One?'"""

import logging
import random
from typing import Dict, List, Optional, Set, Tuple


def current_possibilities(
        names: List[str],
        weekly_pairings: List[Dict[str, str]],
        lights: List[int],
        not_match: List[Tuple[str, str]],
        match: List[Tuple[str, str]],
        exclusive_groups: List[Set[str]] = ()
) -> List[dict]:
    """
    Return a list of possible pairings according to the evidence we've
    observed.

    Parameters
    ----------
    names : List[str]
        A list of the contestants' names
    weekly_pairings : List[Dict[str, str]]
        A list where each element is a pairing. The pairing is represented by a
        dictionary mapping each contestant's name to another contestant.
    lights : List[int]
        A list where each element is the number of lights for that week. The
        length must be equal to the length of `weekly_pairings`.
    not_match : List[Tuple[str, str]]
        A list of two-element tuples, where each tuple contains the names
        of two contestants that are NOT a match. The order does not matter.
    match : List[Tuple[str, str]]
        A list of two-element tuples, where each tuple contains the names
        of two contestants that ARE a match. The order does not matter.
    exclusive_groups : List[Set[str]]
        Sets of contestants that definitely are not matches with each other.
        This could be used to specify sexuality. e.g., all straight men
        would be in one group.
    """
    _validate_pairing_inputs(names=names,
                             weekly_pairings=weekly_pairings,
                             lights=lights,
                             not_match=not_match,
                             match=match,
                             exclusive_groups=exclusive_groups)
    logging.getLogger(__name__).info('Validated info')

    pairings = _get_all_possible_pairings(
        names,
        include=set(match),
        exclude=set(not_match),
        exclusive_groups=exclusive_groups
    )
    logging.getLogger(__name__).info(
        'Got {0} possible pairings'.format(len(pairings))
    )
    pairings_dicts = [dict(p) for p in pairings]
    logging.getLogger(__name__).info('Converted pairing sets to dicts')

    # Remove the possible pairings that are inconsistent with our lights data
    for idx, week in enumerate(weekly_pairings):
        weeded = []
        for p in pairings_dicts:
            if _correct_number(guess=week,
                               truth=p,
                               actually_correct=lights[idx]):
                weeded.append(p)
        pairings_dicts = weeded
        logging.getLogger(__name__).info(
            'Finished accounting for lights in week {0}'.format(idx + 1)
        )
    return pairings_dicts


def probability_of(pairings: List[Dict], a: str, b: str) -> float:
    """
    Return the probability that `a` and `b` are together.

    Parameters
    ----------
    pairings : List[Dict]
        A list of possible pairings. Each dictionary should be a mapping of
        each contestant's name to the contestant they are paired with.
    a : str
        The name of a contestant
    b : str
        The name of another contestant
    """
    return sum([p[a] == b for p in pairings]) / len(pairings)


def get_optimal_pairing(
        pairings: List[Dict], sample: Optional[int] = None
) -> Dict:
    """
    Return the pairing that minimizes the expected size of the solution
    space after seeing the number of lights.

    Parameters
    ----------
    pairings : List[Dict]
        A list of pairings, such as those returned by
        `get_all_possible_pairings`
    sample : Optional[int]
        If specified, randomly pick `sample` pairings and use that to estimate
        the expected size of the solution space after accounting for lights.
        If None, calculate the exact result.
    """
    if len(pairings) < 1:
        raise ValueError('There must be at least one possible pairing')
    n_contestants = len(pairings[0])
    min_lights = float('inf')
    min_pairing = None
    for idx, p in enumerate(pairings):
        # The expected size of the sample space is:
        # sum_{k = 0 to k = N / 2}
        # { # pairings that would result in k lights } / { total # pairings }
        # times { # pairings that would result in k lights },
        # where the first expression is the probability of k lights,
        # and the second expression is the resulting size of the solution
        # space. We ignore the constant factor of 1 / { total # pairings }.
        if sample:
            expected_size = sum(
                [sum([_correct_number(
                    guess=p,
                    truth=pairings[int(random.random() * len(pairings))],
                    actually_correct=k
                ) for _ in range(sample)])**2
                 for k in range(int(n_contestants / 2) + 1)])
        else:
            expected_size = sum([sum([_correct_number(guess=p,
                                                      truth=other_pairing,
                                                      actually_correct=k)
                                      for other_pairing in pairings])**2
                                 for k in range(int(n_contestants / 2) + 1)])
        if expected_size < min_lights:
            min_pairing = p
            min_lights = expected_size
    return min_pairing


def n_guesses(contestants: int) -> int:
    """
    Return the number of guesses required if the contestants randomly picked
    one of the valid pairings at each time step.
    """
    names = [str(i) for i in range(contestants)]
    truth = _generate_random_pairing(names)
    _enforce_symmetric_pairing(truth)
    logging.getLogger(__name__).info('Generated truth')
    logging.getLogger(__name__).info(truth)
    possibilities = _get_all_possible_pairings(names)
    logging.getLogger(__name__).info(
        'Got {0} possible pairings'.format(len(possibilities))
    )
    possibilities_dicts = [dict(p) for p in possibilities]
    logging.getLogger(__name__).info('Converted to dicts')
    guesses = 0
    while len(possibilities_dicts) > 1:
        guess = possibilities_dicts[
            int(random.random() * len(possibilities_dicts))
        ]
        logging.getLogger(__name__).info('Picked random guess')
        _enforce_symmetric_pairing(guess)
        logging.getLogger(__name__).info(guess)
        lights = _get_lights(guess=guess, truth=truth)
        logging.getLogger(__name__).info('Got {0} lights'.format(lights))
        weeded = []
        for p in possibilities_dicts:
            if _correct_number(guess=guess, truth=p, actually_correct=lights):
                weeded.append(p)
        logging.getLogger(__name__).info(
            'Weeded possibilities to {0}'.format(len(weeded))
        )
        possibilities_dicts = weeded
        guesses += 1
    logging.getLogger(__name__).info(possibilities_dicts[0])
    return guesses


def average_n_guesses(contestants: int, n: int) -> float:
    """
    Return the average of `n` calls to `n_guesses`.
    """
    return sum([n_guesses(contestants) for _ in range(n)]) / n


def get_probability_matrix(
        pairings: List[Dict]
) -> Dict[str, Dict[str, float]]:
    """
    Convert a list of pairings (such as the list returned by
    `current_possibilities`) to a 2-D matrix mapping the probability
    that each pair of contestants is together.
    """
    if len(pairings) == 0:
        raise ValueError('There must be at least one pairing')
    names = list(pairings[0].keys())
    return {
        n1: {
            n2: probability_of(pairings, n1, n2) for n2 in names
        } for n1 in names
    }


def pretty_print_matrix(mtx: Dict[str, Dict[str, float]]) -> None:
    """
    Parameters
    ----------
    mtx : Dict[str, Dict[str, float]]
        A 2-D matrix of the format outputted by `get_probability_matrix`

    Examples
    --------
    >>> pretty_print_matrix(get_probability_matrix(season_eight_week_six()))
    """
    names = list(sorted(mtx.keys()))
    header_indent = len(max(names, key=lambda k: len(k))) + 1
    header = ' ' * header_indent + ' '.join(names)
    print(header)
    for n in names:
        front = '{0}{1}'.format(n, ' ' * (header_indent - len(n)))
        for n2 in names:
            percent = int(mtx[n][n2] * 100)
            front = front + '{0}%{1}'.format(
                percent, ' ' * (len(n2) - len(str(percent)))
            )
        print(front)


def _correct_number(guess: Dict,
                    truth: Dict,
                    actually_correct: int) -> bool:
    """
    Return whether the observed number of lights is consistent with
    this truth hypothesis.
    """
    return _get_lights(guess=guess, truth=truth) == actually_correct


def _get_all_possible_pairings(
        people: List[str],
        include: Set[Tuple] = frozenset(),
        exclude: Set[Tuple] = frozenset(),
        exclusive_groups: List[Set] = ()
) -> List[Set[Tuple[str, str]]]:
    """
    Return a list of sets of tuples of pairings, where each set of tuples
    represents a possible pairing.

    Parameters
    ----------
    people : List[str]
        A list of names
    include: Set[Tuple]
        A list of pairings of people who must be together
    exclude : Set[Tuple]
        A list of pairings of people who are certainly not together
    exclusive_groups : List[Set]
        Sets of contestants that definitely are not matches with each other.
    """
    if len(people) == 0:
        return []

    clone = people[:]

    # Remove the names that we already know the pairs for
    for a, b in include:
        if a in clone:
            clone.remove(a)
        if b in people:
            clone.remove(b)

    pairings = []
    first_person = clone.pop(0)
    for i in range(len(clone)):
        next_group = clone[:]
        other_person = next_group.pop(i)
        if ((first_person, other_person) in exclude or
                (other_person, first_person) in exclude):
            continue
        if any([first_person in g and other_person in g
                for g in exclusive_groups]):
            continue
        current_group = _get_all_possible_pairings(
            next_group,
            exclude=exclude,
            exclusive_groups=exclusive_groups
        )
        # Weed out the lists where the people at the end couldn't
        # possibly be together, resulting in too short of a pairing list
        current_group = _weed_out_wrong_size(current_group)
        for s in current_group:
            s.add((first_person, other_person))
            s.add((other_person, first_person))
        if len(current_group) == 0:
            current_group.extend([{(first_person, other_person),
                                   (other_person, first_person)}])
        pairings.extend(current_group)

    # Add the known pairings
    for p in pairings:
        for a, b in include:
            p.add((a, b))
            p.add((b, a))

    return pairings


def _weed_out_wrong_size(lst: List[Set]) -> List[Set]:
    """
    Given a list of sets, weed out the sets that are smaller than the others.
    """
    if len(lst) <= 1:
        return lst
    size = len(max(lst, key=lambda k: len(k)))
    return [s for s in lst if len(s) == size]


def _generate_random_pairing(names: List[str]) -> dict:
    """
    Return a random pairing of names.
    """
    people = names[:]
    pairs = {}
    while len(people) > 0:
        a = people.pop(int(random.random() * len(people)))
        b = people.pop(int(random.random() * len(people)))
        pairs[a] = b
        pairs[b] = a
    return pairs


def _get_lights(guess: dict, truth: dict) -> int:
    """
    Return the number of lights that we would observe.
    """
    correct = 0
    for p in guess:
        if guess[p] == truth[p]:
            correct += 1
    # Adjust for double counting
    return int(correct / 2)


def _enforce_symmetric_pairing(pairing: Dict[str, str]) -> None:
    symmetric_check: Dict[str, str] = {}
    for p in pairing:
        # If we see a partner mentioned before, then that partner
        # should be equal to this one
        for k in symmetric_check:
            if symmetric_check[k] != p:
                continue
            if pairing[p] != k:
                raise ValueError(
                    'The pairings are not symmetric: {0}'.format(pairing)
                )
        # Add this person to the check in future iterations
        symmetric_check[p] = pairing[p]
    # Add any pairs that were only specified in one direction
    for k in list(pairing.keys()):
        pairing[pairing[k]] = k
    if set(pairing) != set(pairing.values()):
        raise ValueError('The pairings are not symmetric: {0}'.format(pairing))


def _validate_pairing_inputs(
        names: List[str],
        weekly_pairings: List[Dict[str, str]],
        lights: List[int],
        not_match: List[Tuple],
        match: List[Tuple],
        exclusive_groups: List[Set]
):
    if len(weekly_pairings) != len(lights):
        raise ValueError('There must be a number of lights for every week')
    if len(set(names)) != len(names):
        raise ValueError('All names must be unique')
    names = set(names)
    for d in weekly_pairings:
        _enforce_symmetric_pairing(d)
        for k in d:
            if k not in names or d[k] not in names:
                raise ValueError('The lights data has an unknown name')
    for a, b in not_match + match:
        if a not in names or b not in names:
            raise ValueError(
                'The confirmed matches or not matches has an unknown name'
            )
    for s in exclusive_groups:
        for n in s:
            if n not in names:
                raise ValueError('The exclusive groups have an unknown name')

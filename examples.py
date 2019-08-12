"""Examples that use the 'Are You the One?' solver."""

import logging
from typing import Dict, List

from solver import (
    average_n_guesses,
    current_possibilities,
    get_probability_matrix,
    pretty_print_matrix,
    probability_of
)


def season_eight_week_six() -> List[Dict]:
    names = [
        'Paige',
        'Nour',
        'Jonathan',
        'Remy',
        'Kai',
        'Jenna',
        'Jasmine',
        'Basit',
        'Max',
        'Danny',
        'Kylie',
        'Kari',
        'Justin',
        'Amber',
        'Aasha',
        'Brandon'
    ]
    weeks = [
        {
            'Aasha': 'Paige',
            'Amber': 'Nour',
            'Basit': 'Jonathan',
            'Brandon': 'Remy',
            'Danny': 'Kai',
            'Jasmine': 'Jenna',
            'Justin': 'Max',
            'Kari': 'Kylie'
        },
        {
            'Aasha': 'Brandon',
            'Amber': 'Nour',
            'Basit': 'Jonathan',
            'Danny': 'Remy',
            'Jasmine': 'Justin',
            'Jenna': 'Kai',
            'Kari': 'Kylie',
            'Max': 'Paige'
        },
        {
            'Aasha': 'Max',
            'Amber': 'Paige',
            'Basit': 'Remy',
            'Brandon': 'Jonathan',
            'Danny': 'Kai',
            'Jasmine': 'Nour',
            'Jenna': 'Justin',
            'Kari': 'Kylie'
        },
        {
            'Aasha': 'Remy',
            'Amber': 'Nour',
            'Basit': 'Danny',
            'Brandon': 'Jasmine',
            'Jenna': 'Paige',
            'Jonathan': 'Kylie',
            'Justin': 'Max',
            'Kai': 'Kari'
        },
        {
            'Aasha': 'Kai',
            'Amber': 'Nour',
            'Basit': 'Remy',
            'Brandon': 'Max',
            'Danny': 'Kari',
            'Jasmine': 'Paige',
            'Jenna': 'Kylie',
            'Jonathan': 'Justin'
        },
        {
            'Aasha': 'Brandon',
            'Amber': 'Jenna',
            'Basit': 'Jonathan',
            'Danny': 'Kai',
            'Jasmine': 'Kylie',
            'Justin': 'Max',
            'Kari': 'Paige',
            'Nour': 'Remy',
        }
    ]
    lights = [2, 2, 2, 1, 0, 3]
    not_match = [
        ('Justin', 'Nour'),
        ('Brandon', 'Remy'),
        ('Jenna', 'Kai'),
        ('Danny', 'Jenna'),
        ('Kari', 'Kylie'),
        ('Jasmine', 'Jenna')
    ]
    match = [('Aasha', 'Brandon')]
    return current_possibilities(names, weeks, lights, not_match, match)


def print_season_eight() -> None:
    s8_pairings = season_eight_week_six()
    pretty_print_matrix(
        get_probability_matrix(s8_pairings)
    )


def probability_kylie_justin() -> float:
    s8_pairings = season_eight_week_six()
    return probability_of(s8_pairings, 'Kylie', 'Justin')


def season_seven_week_four() -> List[Dict]:
    names = [
        'Andrew',
        'Brett',
        'Cam',
        'Daniel',
        'Kwasi',
        'Lewis',
        'Moe',
        'Shamoy',
        'Tevin',
        'Tomas',
        'Zak',
        'Asia',
        'Bria',
        'Cali',
        'Jasmine',
        'Kayla',
        'Kenya',
        'Lauren',
        'Maria',
        'Morgan',
        'Nutsa',
        'Samantha'
    ]
    weeks = [
        {
            'Andrew': 'Lauren',
            'Brett': 'Cali',
            'Cam': 'Kayla',
            'Daniel': 'Nutsa',
            'Kwasi': 'Asia',
            'Lewis': 'Samantha',
            'Moe': 'Jasmine',
            'Shamoy': 'Maria',
            'Tevin': 'Kenya',
            'Tomas': 'Morgan',
            'Zak': 'Bria'
        },
        {
            'Andrew': 'Morgan',
            'Brett': 'Asia',
            'Cam': 'Kayla',
            'Daniel': 'Nutsa',
            'Kwasi': 'Lauren',
            'Lewis': 'Jasmine',
            'Moe': 'Bria',
            'Shamoy': 'Maria',
            'Tevin': 'Kenya',
            'Tomas': 'Cali',
            'Zak': 'Samantha'
        },
        {
            'Andrew': 'Lauren',
            'Brett': 'Cali',
            'Cam': 'Kayla',
            'Daniel': 'Samantha',
            'Kwasi': 'Jasmine',
            'Lewis': 'Asia',
            'Moe': 'Nutsa',
            'Shamoy': 'Maria',
            'Tevin': 'Kenya',
            'Tomas': 'Bria',
            'Zak': 'Morgan'
        },
        {
            'Andrew': 'Nutsa',
            'Brett': 'Kayla',
            'Cam': 'Asia',
            'Daniel': 'Lauren',
            'Kwasi': 'Bria',
            'Lewis': 'Kenya',
            'Moe': 'Samantha',
            'Shamoy': 'Maria',
            'Tevin': 'Jasmine',
            'Tomas': 'Cali',
            'Zak': 'Morgan'
        }
    ]
    lights = [3, 3, 3, 2]
    not_match = [
        ('Tomas', 'Maria'),
        ('Andrew', 'Asia'),
        ('Brett', 'Kenya')
    ]
    match = [('Shamoy', 'Maria')]
    exclusive_groups = [
        {
            'Andrew',
            'Brett',
            'Cam',
            'Daniel',
            'Kwasi',
            'Lewis',
            'Moe',
            'Shamoy',
            'Tevin',
            'Tomas',
            'Zak'
        },
        {
            'Asia',
            'Bria',
            'Cali',
            'Jasmine',
            'Kayla',
            'Kenya',
            'Lauren',
            'Maria',
            'Morgan',
            'Nutsa',
            'Samantha'
        }
    ]
    return current_possibilities(
        names,
        weeks,
        lights,
        not_match=not_match,
        match=match,
        exclusive_groups=exclusive_groups
    )


def value_of_single_match() -> float:
    sixteen_contestants = average_n_guesses(contestants=16, n=10)
    fourteen_contestants = average_n_guesses(contestants=14, n=10)
    return sixteen_contestants - fourteen_contestants


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

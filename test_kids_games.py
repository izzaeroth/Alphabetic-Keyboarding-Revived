import random
import unittest
from collections import Counter
from kids_games import GAME_NAMES, SPEED_PIXELS, make_targets, game_points, high_scores

class KidsGamesTests(unittest.TestCase):
    def test_letters_with_five_repeats_max(self):
        targets = make_targets(GAME_NAMES[0], rng=random.Random(42))
        self.assertEqual(len(targets), 20)
        self.assertEqual(20 - len(set(targets)), 5)
        self.assertLessEqual(max(Counter(targets).values()), 2)

    def test_four_letter_targets(self):
        targets = make_targets(GAME_NAMES[1], rng=random.Random(42))
        self.assertEqual(len(targets), 20)
        self.assertTrue(all(len(x)==4 and x.isalpha() for x in targets))

    def test_word_targets(self):
        targets = make_targets(GAME_NAMES[2], rng=random.Random(42))
        self.assertEqual(len(targets), 20)
        self.assertEqual(len(targets), len(set(targets)))

    def test_scoring(self):
        name = GAME_NAMES[0]
        self.assertGreater(game_points(name,3,15,2), game_points(name,1,15,2))
        self.assertGreater(game_points(name,1,15,0), game_points(name,1,15,2))
        self.assertEqual(game_points(name,1,0,20,10),0)

    def test_ludicrous_speed_is_fastest_and_scores_more(self):
        self.assertEqual(sorted(SPEED_PIXELS), [1, 2, 3, 4])
        self.assertGreater(SPEED_PIXELS[4], SPEED_PIXELS[3])
        self.assertGreater(game_points(GAME_NAMES[0], 4, 18, 2),
                           game_points(GAME_NAMES[0], 3, 18, 2))

    def test_high_scores(self):
        records = [dict(mode='Kids Game', student='Ann',game=GAME_NAMES[0],score=80),
                   dict(mode='Kids Game', student='Ann',game=GAME_NAMES[0],score=110),
                   dict(mode='Kids Game', student='Ben',game=GAME_NAMES[1],score=150),
                   dict(mode='Keyboard Sprint',student='Ann',score=999)]
        self.assertEqual(high_scores(records,student='Ann')[0]['score'],110)
        self.assertEqual(len(high_scores(records,game=GAME_NAMES[1])),1)

if __name__ == '__main__': unittest.main()

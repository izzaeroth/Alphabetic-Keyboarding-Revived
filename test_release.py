"""Unit tests for content, scoring, and navigation."""
import random
import unittest
from typing_content import SPRINT_WORDS, SENTENCE_SETS, make_sprint_round, calculate_score
from app import parse_lessons, parse_menus

class ContentTests(unittest.TestCase):
    def test_original_curriculum(self):
        lessons = parse_lessons()
        self.assertEqual(len(lessons), 18)
        self.assertEqual(sum(map(len, lessons.values())), 90)
        self.assertEqual(set(lessons), set(range(1, 19)))
        self.assertEqual(len(parse_menus()), 18)

    def test_navigation_unique_and_nonempty(self):
        lessons = parse_lessons()
        order = [(n, s['id']) for n in sorted(lessons) for s in lessons[n]]
        self.assertEqual(len(order), len(set(order)))
        self.assertTrue(all(s['lines'] and all(s['lines']) for parts in lessons.values() for s in parts))

    def test_independent_copies(self):
        a = parse_lessons(); a[1][0]['lines'][0] = 'changed'
        self.assertNotEqual(parse_lessons()[1][0]['lines'][0], 'changed')

    def test_sprint_no_duplicates(self):
        rng = random.Random(6)
        a = make_sprint_round(SPRINT_WORDS, (), 12, rng)
        b = make_sprint_round(SPRINT_WORDS, a, 12, rng)
        self.assertEqual(len(set(a)), 12)
        self.assertEqual(len(set(b)), 12)
        self.assertFalse(set(a).intersection(b))

    def test_sentence_sets(self):
        self.assertGreaterEqual(len(SENTENCE_SETS), 3)
        self.assertTrue(all(len(lines) >= 5 for lines in SENTENCE_SETS.values()))

    def test_scores(self):
        score = calculate_score([('hello','hello',0)], 60)
        self.assertEqual(score['wpm'], 1.)
        self.assertEqual(score['accuracy'], 100.)
        self.assertEqual(calculate_score([('hello','hallo',1)],60)['errors'], 1)

if __name__ == '__main__': unittest.main()

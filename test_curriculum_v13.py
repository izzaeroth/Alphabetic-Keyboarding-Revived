"""Check the intentionally staged home-row curriculum."""
import unittest
from lesson_content import LESSONS, LESSON_TITLES


class HomeRowCurriculumTests(unittest.TestCase):
    def test_full_curriculum_remains(self):
        self.assertEqual(set(LESSONS), set(range(1, 19)))
        self.assertEqual(sum(map(len, LESSONS.values())), 90)
        self.assertEqual(len(LESSON_TITLES), 18)
        self.assertTrue(all(len(exercise['lines']) == 3 for lesson in LESSONS.values() for exercise in lesson))

    def test_single_hand_exercises_have_no_spaces_or_other_hand(self):
        for lesson, allowed in ((1, set('asdf')), (2, set('jkl;'))):
            text = ''.join(line for sec in LESSONS[lesson] for line in sec['lines'])
            self.assertTrue(set(text) <= allowed)
            self.assertNotIn(' ', text)

    def test_both_hands_before_space_bar(self):
        both = ''.join(line for sec in LESSONS[3] for line in sec['lines'])
        self.assertNotIn(' ', both)
        self.assertTrue(set(both) <= set('asdfjkl;'))
        self.assertIn('asdf', both)
        self.assertIn('jkl;', both)

    def test_space_introduced_in_four(self):
        self.assertIn('Space Bar', LESSON_TITLES[4])
        self.assertTrue(any(' ' in line for sec in LESSONS[4] for line in sec['lines']))
        self.assertTrue(any(' ' in line for sec in LESSONS[5] for line in sec['lines']))

    def test_new_key_progression(self):
        # Before the lower-row lessons, no untaught letters should appear.
        for lesson in range(4, 9):
            extras = 'eiru' if lesson == 7 else 'qwertyuiop' if lesson == 8 else ''
            allowed = set('asdfjkl; ' + extras)
            for section in LESSONS[lesson]:
                for line in section['lines']:
                    self.assertFalse(set(line) - allowed, (lesson, line, set(line) - allowed))

    def test_later_topics_preserved(self):
        all_titles = ' '.join(LESSON_TITLES.values()).lower()
        for topic in ('upper', 'lower', 'number', 'punctuation', 'capital', 'accuracy', 'fluency'):
            self.assertIn(topic, all_titles)

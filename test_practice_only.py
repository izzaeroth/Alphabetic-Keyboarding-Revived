"""Lesson sessions use guided practice; separate activities measure speed."""
import tkinter as tk
import unittest
from unittest.mock import patch

from app import App


def button_labels(parent):
    found = []
    for child in parent.winfo_children():
        if isinstance(child, tk.Button):
            found.append(child.cget('text'))
        found.extend(button_labels(child))
    return found


class PracticeOnlyTests(unittest.TestCase):
    def test_lesson_flow_has_only_guided_practice(self):
        root = tk.Tk()
        root.withdraw()
        try:
            with patch.object(App, 'load_progress', return_value=[]), patch.object(App, 'load_profile', return_value='Demo'):
                app = App(root)
            app.lesson_number = 1
            first = app.lessons[1][0]
            app.introduce_section(first)
            labels = button_labels(root)
            self.assertIn('Start Practice', labels)
            self.assertNotIn('Start Timed Test', labels)
            app.start_section(first)
            self.assertEqual(app.mode, 'Practice')
            labels = button_labels(root)
            self.assertIn('Restart exercise', labels)
            self.assertFalse(any('Switch to' in label for label in labels))
            app.show_help()
            self.assertNotIn('Timed Test', button_labels(root))
        finally:
            root.destroy()


if __name__ == '__main__':
    unittest.main()

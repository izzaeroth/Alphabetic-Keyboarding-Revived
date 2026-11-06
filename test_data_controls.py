"""Tests for clearing reports and resetting the app without changing independent lessons."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
import app


class DataControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_save, self.old_settings = app.SAVE, app.SETTINGS
        app.SAVE = Path(self.temp.name) / 'progress.json'
        app.SETTINGS = Path(self.temp.name) / 'settings.json'
        self.root = tk.Tk()
        self.application = app.App(self.root)
        self.application.profile = 'Alice'
        self.application._write_progress([{'student':'Alice','lesson':1},
                                          {'student':'Bob','lesson':2},
                                          {'student':'Charlie','lesson':3}])

    def tearDown(self):
        self.root.destroy()
        app.SAVE, app.SETTINGS = self.old_save, self.old_settings
        self.temp.cleanup()

    def test_clear_dialog_current_student_only(self):
        self.application.clear_reports_dialog()
        popup = [w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel)][0]
        self.assertTrue(popup.winfo_exists())
        # Locate the Delete button by label rather than relying on layout ordering.
        def walk(w):
            yield w
            for child in w.winfo_children():
                yield from walk(child)
        delete = next(w for w in walk(popup) if isinstance(w, tk.Button) and w.cget('text')=='Clear Selected Reports')
        with patch.object(app.messagebox,'askyesno',return_value=True), \
             patch.object(app.messagebox,'askyesnocancel',return_value=False), \
             patch.object(app.messagebox,'showinfo'):
            delete.invoke()
        self.assertEqual([x['student'] for x in self.application.progress], ['Bob','Charlie'])
        self.assertEqual(len(__import__('json').loads(app.SAVE.read_text())), 2)

    def test_factory_reset_canceled(self):
        with patch.object(app.messagebox,'askyesno',return_value=True), \
             patch.object(app.messagebox,'askyesnocancel',return_value=False), \
             patch.object(app.simpledialog,'askstring',return_value='NO'), \
             patch.object(app.messagebox,'showinfo'):
            self.application.factory_reset()
        self.assertEqual(len(self.application.progress),3)

    def test_factory_reset_clears_all_and_resets_student(self):
        with patch.object(app.messagebox,'askyesno',return_value=True), \
             patch.object(app.messagebox,'askyesnocancel',return_value=False), \
             patch.object(app.simpledialog,'askstring',return_value='RESET'), \
             patch.object(app.messagebox,'showinfo'):
            self.application.factory_reset()
        self.assertEqual(self.application.progress,[])
        self.assertEqual(self.application.profile,'Student')
        self.assertEqual(__import__('json').loads(app.SETTINGS.read_text())['student'],'Student')
        self.assertEqual(len(app.parse_lessons()), 18)


if __name__=='__main__':
    unittest.main()

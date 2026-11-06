import unittest
from pathlib import Path
class LabelsTest(unittest.TestCase):
    def test_credits_and_branding(self):
        source = (Path(__file__).parent / 'app.py').read_text(encoding='utf-8')
        self.assertIn('Alphabetic Keyboarding Revived', source)
        self.assertIn('ALPHABETIC KEYBOARDING REVIVED', source)
        self.assertNotIn('REMA' + 'STERED', source.upper())
        self.assertNotIn("('Keyboard Shortcut',", source)
        self.assertIn("('Help & About', self.show_help)", source)
        self.assertIn('Progress and Settings', source)
        for name in ('Haugo', 'Hausmann', 'Jackson'):
            self.assertIn(name, source)
        self.assertNotIn('KBDATA.TXT', source)
        self.assertNotIn('KBMENU.TXT', source)
        self.assertNotIn('KeybridgeTyping', source)
        self.assertNotIn('Legacy', source)
        self.assertNotIn('migrate_previous_independent_edition', source)
if __name__ == '__main__': unittest.main()

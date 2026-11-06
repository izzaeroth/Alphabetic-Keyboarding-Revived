"""Games UI smoke test (runs under a desktop or Xvfb display)."""
import tkinter as tk
import unittest
from unittest.mock import patch
from app import App
from kids_games import GAME_NAMES

class GamesGuiTests(unittest.TestCase):
    def test_launcher_game_and_high_scores(self):
        root = tk.Tk()
        root.withdraw()
        try:
            with patch.object(App, 'load_progress', return_value=[]), patch.object(App, 'load_profile', return_value='Demo'):
                app = App(root)
            app.show_games()
            app.open_kids_game(GAME_NAMES[1])
            win = app._kids_game_window
            self.assertEqual(win.phase, 'ready')
            self.assertFalse(win.running)
            self.assertEqual(len(win.targets), 20)
            self.assertIsNone(win.start_time)
            # Speed is selected in the pop-out, before pressing Start Game.
            win.speed_choice.set(3)
            win.start_countdown()
            self.assertEqual(win.speed, 3)
            self.assertEqual(win.phase, 'countdown')
            self.assertEqual(win.countdown_remaining, 3)
            self.assertFalse(win.running)
            from types import SimpleNamespace
            before = win.target_y
            win.on_key(SimpleNamespace(keysym='a', char=win.current()[0]))
            self.assertEqual(win.typed, '')
            win.tick()
            self.assertEqual(win.target_y, before)
            # Stop during countdown: no score saved and speed unlocked.
            win.stop_game()
            self.assertEqual(win.phase, 'ready')
            self.assertEqual(win.start_button.cget('text'), 'Start Game')
            self.assertEqual(win.speed_buttons[0].cget('state'), 'normal')
            self.assertEqual(win.hits, 0)
            self.assertIsNone(win.start_time)
            win.speed_choice.set(2)
            win.toggle_game()
            self.assertEqual(win.phase, 'countdown')
            self.assertEqual(win.speed, 2)
            self.assertEqual(win.start_button.cget('text'), 'Stop Game')
            win.speed_choice.set(3)  # locked during play
            win.countdown_step()
            self.assertEqual(win.countdown_remaining, 2)
            win.countdown_step()
            self.assertEqual(win.countdown_remaining, 1)
            win.countdown_step()
            self.assertEqual(win.phase, 'playing')
            self.assertTrue(win.running)
            self.assertIsNotNone(win.start_time)
            # Stop during active play, reset everything and start fresh.
            win.hits = 2
            win.incorrect = 1
            win.stop_game()
            self.assertEqual(win.phase, 'ready')
            self.assertEqual(win.hits, 0)
            self.assertEqual(win.incorrect, 0)
            self.assertEqual(win.position, 0)
            self.assertIsNone(win.start_time)
            win.toggle_game()
            for _ in range(3):
                win.countdown_step()
            self.assertTrue(win.running)
            target = win.current()
            win.on_key(SimpleNamespace(keysym='a', char=target[0]))
            self.assertEqual(win.typed, target[0])
            wrong = next(c for c in 'abcdefghijklmnopqrstuvwxyz' if c != target[1])
            win.on_key(SimpleNamespace(keysym=wrong, char=wrong))
            self.assertEqual(win.typed, '')
            win.close()
            app.show_game_high_scores()
            app.show_help()
            root.update()
        finally:
            root.destroy()

if __name__ == '__main__': unittest.main()

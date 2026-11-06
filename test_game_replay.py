"""Verify a completed kids' game can be replayed without reopening its window."""
import time
import tkinter as tk
import unittest
from kids_games import FallingGame, GAME_NAMES


class GameReplayTests(unittest.TestCase):
    def test_completed_round_allows_new_speed_and_new_round(self):
        root = tk.Tk()
        root.withdraw()
        saved = []
        game = None
        try:
            game = FallingGame(root, game=GAME_NAMES[0], speed=1,
                               student='Demo', on_finish=saved.append)
            self.assertEqual(game.phase, 'ready')
            game.start_countdown()
            for _ in range(3):
                game.countdown_step()
            self.assertEqual(game.phase, 'playing')
            game.hits = 16
            game.misses = 4
            game.position = len(game.targets)
            game.start_time = time.monotonic() - 50
            game.finish()
            self.assertEqual(game.phase, 'finished')
            self.assertEqual(len(saved), 1)
            self.assertEqual(game.start_button.cget('state'), 'normal')
            self.assertEqual(game.speed_buttons[0].cget('state'), 'normal')
            self.assertEqual(game.start_button.cget('text'), 'Start Game')
            root.update()
            self.assertIsNotNone(game.last_result)
            game.speed_choice.set(4)
            game.toggle_game()
            self.assertEqual(game.phase, 'countdown')
            self.assertEqual(game.speed, 4)
            self.assertEqual(game.countdown_remaining, 3)
            self.assertEqual(game.position, 0)
            self.assertEqual(game.hits, 0)
            self.assertIsNone(game.last_result)
            self.assertEqual(len(saved), 1)  # No extra saved round just for replaying.
            game.stop_game()
            self.assertEqual(game.phase, 'ready')
        finally:
            if game is not None and game.winfo_exists():
                game.close()
            root.destroy()


if __name__ == '__main__':
    unittest.main()

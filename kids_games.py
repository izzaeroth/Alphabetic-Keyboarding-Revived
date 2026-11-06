"""Original children's falling-type games for Alphabetic Keyboarding Revived."""
from __future__ import annotations
import random
import string
import time
import tkinter as tk
from datetime import datetime

GAME_NAMES = ('Falling Letters', 'Four-Letter Challenge', 'Falling Words')
SPEED_PIXELS = {1: 1.0, 2: 2.5, 3: 4.0, 4: 5.5}  # pixels per 30 ms tick
WORDS = ('cat', 'dog', 'sun', 'rain', 'tree', 'bird', 'fish', 'book', 'play', 'jump',
         'frog', 'milk', 'star', 'moon', 'ball', 'cake', 'ship', 'duck', 'frog',
         'blue', 'green', 'smile', 'happy', 'apple', 'house', 'light', 'river',
         'cloud', 'train', 'beach', 'piano', 'robot', 'tiger', 'zebra', 'mouse',
         'bread', 'chair', 'table', 'plant', 'grape', 'peach', 'water', 'brush')


def make_targets(game: str, count: int = 20, rng=None):
    """Create one round; single-letter rounds include at most five repeats."""
    rng = rng or random.Random()
    if game == GAME_NAMES[0]:
        # Exactly 15 different letters and 5 repeated letters, never > 5 repeats.
        unique_count = min(count, 15) if count <= 20 else min(count, 26)
        originals = rng.sample(string.ascii_lowercase, unique_count)
        if count > len(originals):
            originals += rng.sample(originals, min(5, count - len(originals)))
        rng.shuffle(originals)
        return originals
    if game == GAME_NAMES[1]:
        return [''.join(rng.choices(string.ascii_lowercase, k=4)) for _ in range(count)]
    if game == GAME_NAMES[2]:
        pool = list(dict.fromkeys(WORDS))
        if count <= len(pool):
            return rng.sample(pool, count)
        return [rng.choice(pool) for _ in range(count)]
    raise ValueError('Unknown game')


def game_points(game: str, speed: int, hits: int, misses: int, incorrect: int = 0):
    """Points reward successful targets; mistakes lower the final score."""
    base = {GAME_NAMES[0]: 10, GAME_NAMES[1]: 20, GAME_NAMES[2]: 25}[game]
    return max(0, hits * base * speed - misses * (base // 2) - incorrect * 2)


def high_scores(records, student=None, game=None):
    """Sorted high scores, optionally limited to one student and/or game."""
    rows = [r for r in records if r.get('mode') == 'Kids Game'
            and (student is None or r.get('student') == student)
            and (game is None or r.get('game') == game)]
    return sorted(rows, key=lambda r: (-int(r.get('score') or 0),
                                     -int(r.get('hits') or 0), r.get('timestamp', '')))


class FallingGame(tk.Toplevel):
    """Independent keyboard-driven pop-out game; never blocks the main program."""
    def __init__(self, parent, *, game, speed, student, on_finish, on_close=None):
        super().__init__(parent)
        self.game = game
        self.speed = int(speed)
        self.student = student
        self.on_finish = on_finish
        self.on_close = on_close
        self.title(f'{game} — {student}')
        self.configure(bg='#081b56')
        self.geometry('900x640')
        self.minsize(650, 470)
        # A game opens maximized, but remains a separate, restorable window.
        try:
            self.state('zoomed')  # Native Windows maximize state.
        except tk.TclError:
            try:
                self.attributes('-zoomed', True)  # Supported by some other Tk window managers.
            except tk.TclError:
                pass
        self.targets = make_targets(game)
        self.position = 0
        self.typed = ''
        self.hits = 0
        self.misses = 0
        self.incorrect = 0
        self.target_y = 55.0
        self.running = False
        self.phase = 'ready'  # ready -> countdown -> playing -> finished
        self.countdown_remaining = 0
        self.countdown_job = None
        self.pause_until = 0.0
        self.advance_job = None
        self.tick_job = None
        self.start_time = None
        self.finished = False
        self.last_result = None
        self.protocol('WM_DELETE_WINDOW', self.close)
        tk.Label(self, text=game, font=('Segoe UI', 23, 'bold'),
                 bg='#081b56', fg='#ffe36d').pack(pady=(16, 4))
        controls = tk.Frame(self, bg='#081b56')
        controls.pack(pady=(2, 8))
        tk.Label(controls, text='Choose your speed:', bg='#081b56', fg='white',
                 font=('Segoe UI', 12, 'bold')).pack(side='left', padx=(0, 10))
        self.speed_choice = tk.IntVar(value=self.speed)
        self.speed_buttons = []
        for level, caption in [(1, '1 · Easy'), (2, '2 · Medium'), (3, '3 · Fast'), (4, '4 · Ludicrous Speed')]:
            button = tk.Radiobutton(controls, text=caption, value=level, variable=self.speed_choice,
                                    bg='#081b56', fg='white', selectcolor='#112c75',
                                    activebackground='#081b56', activeforeground='white',
                                    font=('Segoe UI', 11), padx=6)
            button.pack(side='left', padx=5)
            self.speed_buttons.append(button)
        self.start_button = tk.Button(controls, text='Start Game', command=self.toggle_game,
                                     font=('Segoe UI', 12, 'bold'), bg='#ffe36d', fg='#081b56',
                                     activebackground='#fff0a3', padx=14, pady=5)
        self.start_button.pack(side='left', padx=(20, 0))
        self.status = tk.Label(self, bg='#081b56', fg='white', font=('Segoe UI', 12))
        self.status.pack(pady=(0, 7))
        self.canvas = tk.Canvas(self, bg='#112c75', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True, padx=26, pady=(0, 12))
        self.feedback = tk.Label(self, text='Choose a speed, then click Start Game.',
                                 bg='#081b56', fg='#dce7ff', font=('Segoe UI', 12))
        self.feedback.pack(pady=(0, 10))
        self.bind('<KeyPress>', self.on_key)
        self.focus_job = self.after(60, self.focus_force)
        self.tick()

    def toggle_game(self):
        if self.phase in ('countdown', 'playing'):
            self.stop_game()
        elif self.phase in ('ready', 'finished'):
            self.start_countdown()

    def stop_game(self):
        """Abort the current round; discard its score and permit a fresh start."""
        if self.phase not in ('countdown', 'playing'):
            return
        self.running = False
        for job in (self.advance_job, self.countdown_job):
            if job is not None:
                try:
                    self.after_cancel(job)
                except tk.TclError:
                    pass
        self.advance_job = None
        self.countdown_job = None
        self.phase = 'ready'
        self.countdown_remaining = 0
        self.reset_round()
        for button in self.speed_buttons:
            button.configure(state='normal')
        self.start_button.configure(text='Start Game', state='normal')
        self.feedback.configure(text='Round stopped. Choose a speed, then click Start Game.', fg='#dce7ff')

    def reset_round(self):
        """Prepare a new unsaved round, discarding the previous round state."""
        self.targets = make_targets(self.game)
        self.position = 0
        self.typed = ''
        self.hits = self.misses = self.incorrect = 0
        self.target_y = 55.0
        self.pause_until = 0.0
        self.start_time = None
        self.finished = False
        self.last_result = None

    def start_countdown(self):
        """Lock the chosen speed and begin a full three-second countdown."""
        if self.phase not in ('ready', 'finished'):
            return
        self.reset_round()
        self.speed = self.speed_choice.get()
        self.phase = 'countdown'
        self.countdown_remaining = 3
        self.start_button.configure(text='Stop Game', state='normal')
        for button in self.speed_buttons:
            button.configure(state='disabled')
        self.feedback.configure(text='Get ready! The targets will start after the countdown.',
                                fg='#dce7ff')
        self.countdown_job = self.after(1000, self.countdown_step)

    def countdown_step(self):
        self.countdown_job = None
        if self.phase != 'countdown':
            return
        self.countdown_remaining -= 1
        if self.countdown_remaining == 0:
            self.phase = 'playing'
            self.running = True
            self.start_time = time.monotonic()
            self.feedback.configure(text='Type the falling target before it crosses the line!',
                                    fg='#dce7ff')
        else:
            self.countdown_job = self.after(1000, self.countdown_step)

    def close(self):
        self.running = False
        for job in (self.advance_job, self.tick_job, self.countdown_job, self.focus_job):
            if job is not None:
                try:
                    self.after_cancel(job)
                except tk.TclError:
                    pass
        self.destroy()
        if self.on_close:
            self.on_close()

    def current(self):
        return self.targets[self.position]

    def on_key(self, event):
        if event.keysym == 'Escape':
            self.close()
            return 'break'
        if not self.running or self.finished or time.monotonic() < self.pause_until:
            return 'break'
        key = event.char.lower()
        if not key or key not in string.ascii_lowercase:
            return 'break'
        expected = self.current()
        if key == expected[len(self.typed)]:
            self.typed += key
            if self.typed == expected:
                self.hits += 1
                self.feedback.config(text='Great job! Next target in a moment.', fg='#a4f8ba')
                self.pause_until = time.monotonic() + 0.5
                self.advance_job = self.after(500, self.advance)
            else:
                self.feedback.config(text=f'{len(self.typed)} of {len(expected)} letters correct', fg='#a4f8ba')
        else:
            self.incorrect += 1
            if self.game != GAME_NAMES[0]:
                self.typed = ''  # Reset the entire four-letter sequence or word.
                self.feedback.config(text='Try that sequence again from the beginning.', fg='#ff9da7')
            else:
                self.feedback.config(text='Try the highlighted letter again.', fg='#ff9da7')
        return 'break'

    def advance(self):
        self.advance_job = None
        if not self.running:
            return
        self.position += 1
        self.target_y = 55.0
        self.typed = ''
        self.pause_until = 0.0
        if self.position == len(self.targets):
            self.finish()
        else:
            self.feedback.config(text='Type the next target!', fg='#dce7ff')

    def miss_target(self):
        self.misses += 1
        self.feedback.config(text='The target crossed the line. Keep going!', fg='#ff9da7')
        self.position += 1
        self.typed = ''
        self.target_y = 55.0
        if self.position == len(self.targets):
            self.finish()

    def tick(self):
        if not self.winfo_exists():
            return
        if self.phase == 'playing' and time.monotonic() >= self.pause_until and self.position < len(self.targets):
            self.target_y += SPEED_PIXELS[self.speed]
        self.canvas.delete('all')
        width = max(450, self.canvas.winfo_width())
        height = max(250, self.canvas.winfo_height())
        line = height - 70
        self.canvas.create_line(20, line, width - 20, line, fill='#ff9da7', width=4)
        self.canvas.create_text(24, line + 18, text='FINISH LINE', anchor='nw',
                                fill='#ffbdc4', font=('Segoe UI', 10, 'bold'))
        if self.phase == 'playing' and self.position < len(self.targets):
            target = self.current()
            self.canvas.create_text(width / 2, self.target_y,
                                    text=target, fill='#fff1a3',
                                    font=('Consolas', 38 if len(target) < 5 else 31, 'bold'))
            if self.typed:
                self.canvas.create_text(width / 2, self.target_y + 42, text=self.typed,
                                        fill='#9af3b2', font=('Consolas', 19, 'bold'))
            if self.target_y >= line - 29 and time.monotonic() >= self.pause_until:
                self.miss_target()
        if self.phase == 'ready':
            self.canvas.create_text(width / 2, height / 2 - 25,
                                    text='READY TO PLAY?', fill='#ffe36d',
                                    font=('Segoe UI', 29, 'bold'))
            self.canvas.create_text(width / 2, height / 2 + 35,
                                    text='Choose Speed 1–4 above, then click Start Game.',
                                    fill='white', font=('Segoe UI', 13))
        elif self.phase == 'countdown':
            self.canvas.create_text(width / 2, height / 2 - 15,
                                    text=str(self.countdown_remaining), fill='#ffe36d',
                                    font=('Segoe UI', 72, 'bold'))
            self.canvas.create_text(width / 2, height / 2 + 75,
                                    text='Get ready to type!', fill='white',
                                    font=('Segoe UI', 16, 'bold'))
        elif self.phase == 'finished' and self.last_result is not None:
            result = self.last_result
            self.canvas.create_text(width / 2, height / 2 - 75,
                                    text='ROUND COMPLETE!', fill='#ffe36d',
                                    font=('Segoe UI', 29, 'bold'))
            self.canvas.create_text(width / 2, height / 2 - 15,
                                    text=f"{result['score']} POINTS  •  {result['accuracy_pct']}% ACCURACY",
                                    fill='white', font=('Segoe UI', 18, 'bold'))
            self.canvas.create_text(width / 2, height / 2 + 45,
                                    text='Choose a speed above and click Start Game to play again.',
                                    fill='#a4f8ba', font=('Segoe UI', 14))
        if self.phase == 'finished' and self.last_result is not None:
            self.status.config(text=f"Finished!  {self.hits}/{len(self.targets)} correct   •   Score {self.last_result['score']}")
        else:
            self.status.config(text=f'Target {min(self.position + 1, len(self.targets))} / {len(self.targets)}     Speed {self.speed}     '
                                    f'Correct {self.hits}     Missed {self.misses}     '
                                    f'Points {game_points(self.game, self.speed, self.hits, self.misses, self.incorrect)}')
        self.tick_job = self.after(30, self.tick)

    def finish(self):
        if self.finished:
            return
        self.finished = True
        self.running = False
        self.phase = 'finished'
        seconds = max(0.1, time.monotonic() - self.start_time)
        score = game_points(self.game, self.speed, self.hits, self.misses, self.incorrect)
        accuracy = round(100 * self.hits / max(1, self.hits + self.incorrect + self.misses), 1)
        record = dict(student=self.student, timestamp=datetime.now().isoformat(timespec='seconds'),
                      lesson=None, section=None, title=self.game, mode='Kids Game', game=self.game,
                      speed_level=self.speed, score=score, hits=self.hits, misses=self.misses,
                      incorrect_keys=self.incorrect, errors=self.misses + self.incorrect,
                      accuracy_pct=accuracy, seconds=round(seconds, 1), lines=len(self.targets))
        self.last_result = record
        self.on_finish(record)
        for button in self.speed_buttons:
            button.configure(state='normal')
        self.start_button.configure(text='Start Game', state='normal')
        self.feedback.config(text='Round saved! Change speed or click Start Game to play again.', fg='#a4f8ba')

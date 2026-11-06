"""Alphabetic Keyboarding Revived: independently authored typing lessons and Windows interface."""
from __future__ import annotations
import json
import csv
import random
import zipfile
import tempfile
import shutil
import time
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from pathlib import Path
from datetime import datetime
from statistics import mean
from typing_content import SPRINT_WORDS, SENTENCE_SETS, make_sprint_round, calculate_score
from lesson_content import LESSON_TITLES, LESSONS

SAVE = Path.home() / 'AlphabeticKeyboardingRevived' / 'progress.json'
SETTINGS = SAVE.parent / 'settings.json'

COLORS = dict(bg='#061a6b', panel='#112a8b', ink='#f3f4ff', accent='#ffe36d', correct='#94f6b5', wrong='#ff8c9a')


def parse_menus():
    """Lesson names for the independent curriculum."""
    return LESSON_TITLES.copy()


def parse_lessons():
    """New practice material; return independent objects for each session."""
    return {number: [{'id': part['id'], 'title': part['title'], 'lines': part['lines'][:]} for part in parts]
            for number, parts in LESSONS.items()}


# Finger codes: left/right pinky, ring, middle, index, thumb.
FINGER_KEYS = {
    'LP': '`~1!qaz', 'LR': '2@ws', 'LM': '3#ed',
    'LI': '4$5%rtfgvb', 'RI': '6^7&yuhjnm',
    'RM': '8*ik,', 'RR': '9(ol.', 'RP': '0)-_=+[{]}\\|;:\"\'/?',
    'LT': ' ', 'RT': ' ',
}
# Finger assignments for the graphical keyboard.
FINGER_LOOKUP = {c: finger for finger, chars in FINGER_KEYS.items() for c in chars}
FINGER_LOOKUP[' '] = 'RT'
FINGER_LABELS = {'LP':'Left pinky','LR':'Left ring','LM':'Left middle',
                 'LI':'Left index','LT':'Thumb (space)', 'RI':'Right index',
                 'RM':'Right middle','RR':'Right ring','RP':'Right pinky','RT':'Thumb (space)'}
SHIFT_KEYS = {'!':'1','@':'2','#':'3','$':'4','%':'5','^':'6','&':'7','*':'8',
              '(':'9',')':'0','_':'-','+':'=','{':'[','}':']','|':'\\',
              ':':';','\"':'\'','<':',','>':'.','?':'/','~':'`'}
KEY_ROWS = [
    [('`',1),('1',1),('2',1),('3',1),('4',1),('5',1),('6',1),('7',1),('8',1),('9',1),('0',1),('-',1),('=',1),('⌫',1.8)],
    [('Tab',1.5),('Q',1),('W',1),('E',1),('R',1),('T',1),('Y',1),('U',1),('I',1),('O',1),('P',1),('[',1),(']',1),('\\',1.3)],
    [('Caps',1.8),('A',1),('S',1),('D',1),('F',1),('G',1),('H',1),('J',1),('K',1),('L',1),(';',1),("'",1),('Enter',2)],
    [('Shift',2.3),('Z',1),('X',1),('C',1),('V',1),('B',1),('N',1),('M',1),(',',1),('.',1),('/',1),('Shift',2.7)],
    [('Ctrl',1.5),('Alt',1.5),('Space',7),('Alt',1.5),('Ctrl',1.5)],
]
FINGER_COLORS = {'LP':'#fb7185','LR':'#f59e0b','LM':'#facc15','LI':'#22c55e',
                 'RI':'#06b6d4','RM':'#818cf8','RR':'#c084fc','RP':'#f472b6',
                 'LT':'#60a5fa','RT':'#60a5fa'}


def finger_for(character):
    if not character:
        return None
    if character.isalpha():
        character = character.lower()
    return FINGER_LOOKUP.get(character)


class KeyboardGuide(tk.Frame):
    """On-screen keyboard and illustrated hand-position guide."""
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg'])
        self.next_char = ''
        self.canvas = tk.Canvas(self, height=280, bg=COLORS['bg'], highlightthickness=0)
        self.canvas.pack(fill='x')
        self.hands = tk.Canvas(self, height=155, bg=COLORS['bg'], highlightthickness=0)
        self.hands.pack(fill='x')
        self.hint = tk.Label(self, bg=COLORS['bg'], fg=COLORS['accent'],
                             font=('Segoe UI', 11, 'bold'))
        self.hint.pack(pady=(0, 3))
        self.canvas.bind('<Configure>', lambda e: self.draw())
        self.hands.bind('<Configure>', lambda e: self.draw_hands())

    def set_next(self, character):
        self.next_char = character or ''
        self.hint.config(text=(f'Next key: {repr(character)}  •  {FINGER_LABELS.get(finger_for(character), "Follow the line")}'
                               if character else 'Line complete — press Enter'))
        self.draw()
        self.draw_hands()

    def draw(self):
        c = self.canvas
        c.delete('all')
        width = max(400, c.winfo_width())
        margin, gap = 10, 5
        height = max(38, min(58, (c.winfo_height()-12)/5-6))
        keywidth = (width - 2*margin - 13*gap) / 16.1
        base = SHIFT_KEYS.get(self.next_char, self.next_char).upper()
        if base == ' ':
            base = 'Space'
        for row_id, row in enumerate(KEY_ROWS):
            x = margin
            y = 5 + row_id * (height + 5)
            for label, units in row:
                w = units * keywidth + (units-1)*gap
                on = label.upper() == base or (label == 'Space' and base == 'Space')
                if self.next_char.isupper() and self.next_char.isalpha() and label == 'Shift':
                    on = True
                if self.next_char in SHIFT_KEYS and label == 'Shift':
                    on = True
                finger = finger_for(label.lower()) if len(label) == 1 else None
                fill = '#fef08a' if on else ('#283c67' if not finger else '#203451')
                outline = '#facc15' if on else '#435476'
                c.create_rectangle(x, y, x+w, y+height, fill=fill, outline=outline, width=2 if on else 1)
                c.create_text(x+w/2, y+height/2, text=label, fill='#172554' if on else '#f1f5f9',
                              font=('Segoe UI', 13 if len(label)<6 else 10, 'bold' if on else 'normal'))
                if finger and not on:
                    c.create_rectangle(x+3, y+height-5, x+w-3, y+height-2,
                                       fill=FINGER_COLORS[finger], outline='')
                x += w+gap

    def draw_hands(self):
        """Anatomical palm / four extending fingers / outward-angled thumb.
        Schematic hands for learning finger position.
        """
        c = self.hands
        c.delete('all')
        w, h = max(460, c.winfo_width()), max(160, c.winfo_height())
        scale = min(1.35, max(.62, w / 1100))
        active = finger_for(self.next_char)
        for side, cx in [('L', w*.28), ('R', w*.72)]:
            mirror = 1 if side == 'L' else -1
            c.create_text(cx, 13, text='LEFT HAND' if side == 'L' else 'RIGHT HAND',
                          fill='#dbeafe', font=('Segoe UI', 11, 'bold'))
            palm_top = h*.59
            palm_bottom = h*.88
            palm_left = cx - 66*scale
            palm_right = cx + 66*scale
            c.create_oval(palm_left, palm_top-10*scale, palm_right, palm_bottom+10*scale,
                          fill='#405879', outline='#92aacb', width=2)
            # Four nearly vertical fingers: pinky shortest, middle longest.
            # For the right hand, mirror their arrangement horizontally.
            configs = [('P',-1.5, .39), ('R',-.5,.30), ('M',.5,.235), ('I',1.5,.34)]
            for suffix, pos, height_ratio in configs:
                code = side+suffix
                x = cx + mirror*pos*30*scale
                tip_y = max(31, h*height_ratio)
                bottom_y = palm_top+9*scale
                selected = code == active
                base_color = '#58718e'
                finger_color = FINGER_COLORS[code] if selected else base_color
                r = 12*scale
                c.create_polygon(x-r,bottom_y, x-r,tip_y+r, x-r*.65,tip_y-r*.4,
                                 x,tip_y-r, x+r*.65,tip_y-r*.4, x+r,tip_y+r,
                                 x+r,bottom_y, fill=finger_color, outline='#9ab0cf', width=2,
                                 smooth=True)
                c.create_oval(x-r*.62, tip_y-r*.6, x+r*.62, tip_y+r*.65,
                              fill='#fef08a' if selected else '#90a5c0', outline='')
            # Thumb originates near the inside edge of each palm, not in the finger row.
            thumb_code = side+'T'
            selected = (active == thumb_code or self.next_char == ' ')
            inner_x = cx + mirror*53*scale
            thumb_tip_x = cx + mirror*88*scale
            thumb_tip_y = h*.49
            c.create_line(inner_x, h*.77, thumb_tip_x, thumb_tip_y,
                          fill=FINGER_COLORS[thumb_code] if selected else '#58718e',
                          width=21*scale, capstyle='round')
            c.create_oval(thumb_tip_x-10*scale, thumb_tip_y-10*scale,
                          thumb_tip_x+10*scale, thumb_tip_y+10*scale,
                          fill='#fef08a' if selected else '#90a5c0', outline='')
            if active and active.startswith(side):
                title = FINGER_LABELS.get(active, '')
                c.create_text(cx, h*.98, text=title,
                              fill=COLORS['accent'], font=('Segoe UI', 10, 'bold'), anchor='s')
        if not active:
            c.create_text(w/2, h-3, text='Finger guide', fill='#aabed8',
                          font=('Segoe UI', 9), anchor='s')


class App:
    def __init__(self, root):
        self.root = root
        root.title('Alphabetic Keyboarding Revived')
        root.geometry('1080x850')
        root.minsize(900, 650)
        # Windows 11: launch maximized, with a normal title bar and Restore button.
        # Keep the default geometry as the size when the user restores the window.
        try:
            root.state('zoomed')
        except tk.TclError:
            # Other platforms may not support Tk's 'zoomed' window state.
            pass
        root.configure(bg=COLORS['bg'])
        self.menus = parse_menus()
        self.lessons = parse_lessons()
        self.progress = self.load_progress()
        self.profile = self.load_profile()
        self.game_active = False
        self.previous_sprint = []
        self.sentence_running = False
        self.speed_goal = None
        self.section = None
        self.lesson_number = None
        self.index = 0
        self.started = None
        self.line_started = None
        self.elapsed_typing = 0.0
        self.complete = False
        self.mode = 'Practice'
        self.mistake_keys = 0
        self.root.bind('<F1>', lambda event: self.show_help())
        self.display_home()

    def load_progress(self):
        try:
            return json.loads(SAVE.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return []

    def save_result(self, record):
        self.progress.append(record)
        SAVE.parent.mkdir(parents=True, exist_ok=True)
        SAVE.write_text(json.dumps(self.progress, indent=2), encoding='utf-8')

    def load_profile(self):
        try:
            data = json.loads(SETTINGS.read_text(encoding='utf-8'))
            return str(data.get('student', 'Student'))[:48] or 'Student'
        except (OSError, ValueError, AttributeError):
            return 'Student'

    def change_profile(self):
        name = simpledialog.askstring('Student name', 'Enter a student name:',
                                      initialvalue=self.profile, parent=self.root)
        if not name or not name.strip():
            return
        self.profile = name.strip()[:48]
        SETTINGS.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS.write_text(json.dumps({'student': self.profile}, indent=2), encoding='utf-8')
        self.display_home()

    def mine(self):
        return [r for r in self.progress if r.get('student') == self.profile]

    def show_reports(self):
        self.clear()
        self.label(self.root, 'PROGRESS AND SETTINGS', 24, COLORS['accent'], True).pack(pady=(18, 6))
        self.button(self.root, '← Home', self.display_home).pack(anchor='w', padx=26, pady=4)
        records = self.mine()
        head = tk.Frame(self.root, bg=COLORS['bg']); head.pack(padx=28, pady=12, fill='x')
        lesson_records = [r for r in records if isinstance(r.get('lesson'), int)]
        completed = {(r.get('lesson'), r.get('section')) for r in lesson_records}
        all_sections = sum(len(v) for v in self.lessons.values())
        best = max((float(r.get('estimated_wpm') or 0) for r in lesson_records), default=0)
        latest = lesson_records[-1] if lesson_records else None
        avgacc = sum(float(r.get('accuracy_pct') or 0) for r in lesson_records) / len(lesson_records) if lesson_records else 0
        stats = (f'Student: {self.profile}    •    {len(records)} attempts    •    '
                 f'{len(completed)}/{all_sections} sections practiced\n'
                 f'Best lesson speed: {best:.1f} WPM    •    Average lesson accuracy: {avgacc:.1f}%'
                 + (f'    •    Last attempt: {latest.get("timestamp", "")[:10]}' if latest else ''))
        self.label(head, stats, 13, justify='left').pack(anchor='w')
        tools = tk.Frame(self.root, bg=COLORS['bg']); tools.pack(fill='x', padx=28, pady=5)
        self.label(tools, 'View:', 12).pack(side='left', padx=(0, 10))
        options = ['All results', 'Lesson results', 'Sentence tests', 'Keyboard Sprint', 'Other activities'] + [f'Lesson {n}' for n in range(1, 19)]
        self.report_filter = tk.StringVar(value='All results')
        selector = ttk.Combobox(tools, textvariable=self.report_filter, values=options, state='readonly', width=19)
        selector.pack(side='left')
        export_tools = tk.Frame(self.root, bg=COLORS['bg']); export_tools.pack(fill='x', padx=28, pady=3)
        for caption, action in [('Save Summary',self.export_report),('Export for Excel',self.export_csv),
                                ('Back Up Progress',self.backup_records),('Restore Progress',self.restore_records)]:
            self.button(export_tools, caption, action).pack(side='left', padx=(0,8))
        manage_tools = tk.Frame(self.root, bg=COLORS['bg']); manage_tools.pack(fill='x', padx=28, pady=3)
        self.button(manage_tools, 'Clear Reports', self.clear_reports_dialog).pack(side='left', padx=(0,8))
        self.button(manage_tools, 'Reset to First-Run Settings', self.factory_reset).pack(side='left', padx=(0,8))
        area = tk.Frame(self.root, bg=COLORS['bg']); area.pack(fill='both', expand=True, padx=28, pady=(8, 16))
        cols = ('date','lesson','section','mode','speed','accuracy','errors','duration')
        table = ttk.Treeview(area, columns=cols, show='headings')
        for col, title, width in [('date','Date / time',145),('lesson','Lesson',125),('section','Exercise',215),
                                  ('mode','Mode',135),('speed','Speed (WPM)',105),('accuracy','Accuracy %',105),('errors','Errors',75),('duration','Seconds',90)]:
            table.heading(col, text=title); table.column(col, width=width, anchor='center' if col not in ('date','section') else 'w', stretch=True)
        scrollbar = ttk.Scrollbar(area, orient='vertical', command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        table.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        def refresh(event=None):
            table.delete(*table.get_children())
            for r in reversed(records):
                if not self.report_matches(r, self.report_filter.get()): continue
                table.insert('', 'end', values=(r.get('timestamp',''),
                    f'Lesson {r["lesson"]}' if r.get('lesson') else ('Sentence test' if r.get('mode')=='Sentence Speed Test' else 'Sprint'),
                    (f'{r.get("section")} — {r.get("title", "")}' if r.get("section") is not None else r.get("title", ""))[:65],
                    r.get('mode','Practice'), r.get('estimated_wpm','—'), r.get('accuracy_pct','—'),
                    r.get('errors','—'), r.get('seconds','—')))
        selector.bind('<<ComboboxSelected>>', refresh)
        refresh()
        self.label(self.root, 'Speed is measured in words per minute (WPM).', 10).pack(pady=(0, 7))
        history = [r for r in lesson_records if r.get('estimated_wpm') is not None]
        if history:
            chart = tk.Canvas(self.root, height=100, bg='#0d2372', highlightthickness=0)
            chart.pack(fill='x', padx=32, pady=(0,12))
            def draw_chart(event=None):
                chart.delete('all')
                sample = history[-40:]; values = [max(0,float(r.get('estimated_wpm') or 0)) for r in sample]
                w = max(200,chart.winfo_width()); h = max(80,chart.winfo_height()); high = max(10,max(values))
                chart.create_text(12,12, text='Recent lesson speeds (WPM)', fill='white', anchor='nw', font=('Segoe UI',10,'bold'))
                if len(values) == 1: values = [values[0],values[0]]
                points = []
                for i,val in enumerate(values):
                    points.extend((22+i*(w-44)/(len(values)-1), h-12-(val/high)*(h-38)))
                chart.create_line(*points, fill='#ffe36d', width=3, smooth=False)
            chart.bind('<Configure>',draw_chart)


    def backup_records(self):
        path = filedialog.asksaveasfilename(parent=self.root, defaultextension='.zip',
            initialfile='AlphabeticKeyboardingRevived_Backup.zip', filetypes=[('Backup ZIP','*.zip')])
        if not path: return False
        try:
            with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
                z.writestr('progress.json', json.dumps(self.progress,indent=2))
                z.writestr('settings.json',json.dumps({'student': self.profile},indent=2))
                z.writestr('backup_info.txt','Alphabetic Keyboarding Revived student records backup\n')
            messagebox.showinfo('Backup complete','Records and student selection were backed up.')
            return True
        except (OSError, ValueError) as ex:
            messagebox.showerror('Backup failed',str(ex))
            return False

    def _backup_before_removing(self):
        """Offer a ZIP backup; cancellation or failed backup prevents deletion."""
        choice = messagebox.askyesnocancel(
            'Back up your results?',
            'Would you like to save a backup before continuing?\n\n'
            'Yes: make a backup first.\nNo: continue without one.\nCancel: keep everything.',
            parent=self.root)
        if choice is None:
            return False
        if choice and not self.backup_records():
            return False
        return True

    def _write_progress(self, records):
        """Write all results safely before changing the in-memory copy."""
        SAVE.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix='progress_', suffix='.json', dir=str(SAVE.parent))
        try:
            with open(fd, 'w', encoding='utf-8') as stream:
                json.dump(records, stream, indent=2)
            Path(temp_name).replace(SAVE)
        finally:
            Path(temp_name).unlink(missing_ok=True)
        self.progress = records

    def clear_reports_dialog(self):
        """Choose whose results to clear without deleting student names or preferences."""
        names = sorted({str(r.get('student')) for r in self.progress} | {self.profile}, key=str.casefold)
        win = tk.Toplevel(self.root)
        win.title('Clear Reports')
        win.configure(bg=COLORS['bg'])
        win.geometry('520x470')
        win.transient(self.root)
        win.grab_set()
        self.label(win, 'Clear Saved Reports', 21, COLORS['accent'], True).pack(pady=(18, 6))
        self.label(win, 'Choose which students’ results to remove. Student names and lessons stay.',
                   11, wraplength=470, justify='center').pack(padx=16, pady=7)
        choice = tk.StringVar(value='current')
        for text, value in [('Current student only', 'current'),
                            ('Choose from student list', 'selected'),
                            ('All students', 'all')]:
            tk.Radiobutton(win, text=text, variable=choice, value=value,
                           bg=COLORS['bg'], fg=COLORS['ink'], selectcolor=COLORS['panel'],
                           activebackground=COLORS['bg'], activeforeground='white',
                           font=('Segoe UI', 12)).pack(anchor='w', padx=35, pady=2)
        listbox = tk.Listbox(win, selectmode=tk.EXTENDED, exportselection=False,
                             height=6, font=('Segoe UI', 11))
        for name in names:
            listbox.insert('end', name)
        listbox.pack(fill='x', padx=35, pady=(10, 5))
        # Allow multiple students, selected with Ctrl+click or Shift+click.
        self.label(win, 'For multiple students, hold Ctrl while clicking names.', 10).pack(pady=(0, 8))
        count_label = self.label(win, '', 11, COLORS['accent'], True)
        count_label.pack(pady=5)

        def selected_names():
            if choice.get() == 'all':
                return set(names)
            if choice.get() == 'current':
                return {self.profile}
            return {names[i] for i in listbox.curselection()}

        def count_results():
            chosen = selected_names()
            total = sum(str(r.get('student')) in chosen for r in self.progress)
            count_label.config(text=f'{total} saved result(s) selected for removal')
            return chosen, total

        def confirm():
            chosen, count = count_results()
            if not chosen:
                messagebox.showinfo('Choose a student', 'Select at least one student from the list.', parent=win)
                return
            if not count:
                messagebox.showinfo('No reports to clear', 'Those students have no saved reports.', parent=win)
                return
            if not messagebox.askyesno('Confirm report deletion',
                    f'Delete {count} saved result(s) for {len(chosen)} student(s)?\n\n'
                    'This cannot be undone without a backup. Other students’ results will remain.',
                    parent=win):
                return
            if not self._backup_before_removing():
                return
            remaining = [r for r in self.progress if str(r.get('student')) not in chosen]
            try:
                self._write_progress(remaining)
            except OSError as ex:
                messagebox.showerror('Could not clear reports', str(ex), parent=win)
                return
            win.destroy()
            messagebox.showinfo('Reports cleared', f'Removed {count} saved result(s).')
            self.show_reports()

        choice.trace_add('write', lambda *_: count_results())
        listbox.bind('<<ListboxSelect>>', lambda event: count_results())
        buttons = tk.Frame(win, bg=COLORS['bg'])
        buttons.pack(pady=8)
        self.button(buttons, 'Clear Selected Reports', confirm).pack(side='left', padx=7)
        self.button(buttons, 'Cancel', win.destroy).pack(side='left', padx=7)
        count_results()

    def factory_reset(self):
        """Reset local student data without changing lesson content."""
        if not messagebox.askyesno('Restore starting settings',
                'Return Alphabetic Keyboarding to its first-run state?\n\n'
                'This clears ALL students’ results and returns to the default Student profile.\n'
                'Lessons and program files will NOT be removed.',
                parent=self.root):
            return
        if not self._backup_before_removing():
            return
        answer = simpledialog.askstring('Confirm factory reset',
            'To confirm, type RESET in capital letters:', parent=self.root)
        if answer != 'RESET':
            messagebox.showinfo('Reset canceled', 'Nothing was changed.', parent=self.root)
            return
        try:
            self._write_progress([])
            # The reset marker for settings is the same default state as a fresh install.
            SETTINGS.parent.mkdir(parents=True, exist_ok=True)
            SETTINGS.write_text(json.dumps({'student': 'Student'}, indent=2), encoding='utf-8')
        except OSError as ex:
            messagebox.showerror('Reset could not finish',
                f'Could not fully reset saved data: {ex}', parent=self.root)
            return
        self.profile = 'Student'
        self.previous_sprint = []
        self.speed_goal = None
        self.section = None
        self.lesson_number = None
        self.index = 0
        self.elapsed_typing = 0.0
        self.game_active = False
        self.sentence_running = False
        messagebox.showinfo('Reset complete', 'Alphabetic Keyboarding is ready for a fresh start.', parent=self.root)
        self.display_home()

    def restore_records(self):
        path = filedialog.askopenfilename(parent=self.root,filetypes=[('Backup ZIP','*.zip')])
        if not path: return
        try:
            with zipfile.ZipFile(path) as z:
                data = json.loads(z.read('progress.json'))
            if not isinstance(data,list) or any(not isinstance(row,dict) for row in data):
                raise ValueError('Backup records have an invalid format.')
            if len(data)>100000: raise ValueError('Backup contains too many records.')
            # Merge, don't overwrite: preserve current progress and avoid duplicate imports.
            keys = {json.dumps(r,sort_keys=True) for r in self.progress}
            additions = [r for r in data if json.dumps(r,sort_keys=True) not in keys]
            if not messagebox.askyesno('Restore records',
                f'Add {len(additions)} records from this backup?\nExisting records will be kept.'):
                return
            self.progress.extend(additions)
            SAVE.parent.mkdir(parents=True,exist_ok=True)
            SAVE.write_text(json.dumps(self.progress,indent=2),encoding='utf-8')
            messagebox.showinfo('Restore complete',f'Imported {len(additions)} records.')
            self.show_reports()
        except (OSError, ValueError, KeyError, zipfile.BadZipFile) as ex:
            messagebox.showerror('Restore failed',str(ex))

    @staticmethod
    def report_matches(record, choice):
        lesson = record.get('lesson')
        if choice == 'All results': return True
        if choice == 'Lesson results': return isinstance(lesson, int)
        if choice == 'Other activities': return lesson is None
        if choice == 'Sentence tests': return record.get('mode') == 'Sentence Speed Test'
        if choice == 'Keyboard Sprint': return record.get('mode') == 'Keyboard Sprint'
        return str(lesson) == choice.removeprefix('Lesson ')

    def export_report(self):
        records = [r for r in self.mine() if self.report_matches(r, self.report_filter.get())]
        path = filedialog.asksaveasfilename(parent=self.root, defaultextension='.txt',
            initialfile='AlphabeticKeyboardingRevived_Report.txt', filetypes=[('Text reports','*.txt')])
        if not path: return
        lines = ['ALPHABETIC KEYBOARDING — STUDENT REPORT',
                 f'Student: {self.profile}', f'Generated: {datetime.now().isoformat(timespec="minutes")}',
                 f'Filter: {self.report_filter.get()}', f'Attempt count: {len(records)}',
                 'Speed and accuracy are estimates for practice and comparison.', '',
                 'Date / time         Lesson / section                       WPM    Accuracy Errors  Seconds', '-'*99]
        for r in records:
            name = (f'Lesson {r["lesson"]} / {r.get("section", "?")}' if r.get('lesson') else r.get('title','Bonus activity'))
            lines.append(f'{str(r.get("timestamp",""))[:19]:19} {name[:35]:35} '
                         f'{str(r.get("estimated_wpm","")):>6} {str(r.get("accuracy_pct","")):>9} '
                         f'{str(r.get("errors","")):>6} {str(r.get("seconds","")):>8}')
        try:
            Path(path).write_text('\n'.join(lines)+'\n', encoding='utf-8')
            messagebox.showinfo('Report saved','Saved printable report to:\n'+path)
        except OSError as ex: messagebox.showerror('Export failed', str(ex))

    def export_csv(self):
        records=[r for r in self.mine() if self.report_matches(r, self.report_filter.get())]
        if not records:
            messagebox.showinfo('No results','There are no results to export yet.')
            return
        name=filedialog.asksaveasfilename(parent=self.root,defaultextension='.csv',
                 initialfile='AlphabeticKeyboardingRevived_Results.csv',filetypes=[('CSV files','*.csv')])
        if not name:return
        cols=['student','timestamp','lesson','section','title','mode','lines','seconds','estimated_wpm','accuracy_pct','errors','key_mistakes','goal_wpm','goal_met','scoring_version']
        try:
            with open(name,'w',encoding='utf-8-sig',newline='') as f:
                w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(records)
            messagebox.showinfo('Export complete','Saved your results to:\n'+name)
        except OSError as ex:messagebox.showerror('Export failed',str(ex))

    def show_technique(self):
        """Display newly written general keyboarding advice."""
        self.clear()
        body = tk.Frame(self.root, bg=COLORS['bg']); body.pack(padx=35, pady=22, anchor='nw')
        self.label(body, 'KEYBOARDING TECHNIQUE', 24, COLORS['accent'], True).pack(anchor='w', pady=(0,12))
        self.button(body, '← Home', self.display_home).pack(anchor='w', pady=(0,16))
        guidance = [
            'Sit comfortably with your feet supported.',
            'Relax your shoulders and keep your elbows near your sides.',
            'Start with your fingers resting lightly on the home row.',
            'Let your wrists stay relaxed rather than pressing down on the desk.',
            'Keep your eyes on the exercise instead of hunting for keys.',
            'Use small, gentle movements rather than striking hard.',
            'Return each finger to its home position after reaching.',
            'Use the opposite hand to hold Shift for capital letters.',
            'Reach for Enter with your right pinky, then return to home row.',
            'Tap the space bar with whichever thumb feels natural.',
        ]
        self.label(body, 'Good typing habits', 14, COLORS['accent']).pack(anchor='w', pady=(3,10))
        for n, tip in enumerate(guidance, 1):
            self.label(body, f'{n:02d}.  {tip}', 13).pack(anchor='w', pady=5)
        self.label(body, 'Try these tips whenever you practice.', 11).pack(anchor='w', pady=18)

    def show_speed_builder(self):
        self.clear()
        body = tk.Frame(self.root, bg=COLORS['bg']); body.pack(padx=36, pady=28, anchor='nw')
        self.label(body, 'SPEED BUILDER', 24, COLORS['accent'], True).pack(anchor='w', pady=(0,15))
        self.button(body, '← Home', self.display_home).pack(anchor='w', pady=(0,18))
        self.label(body, 'Choose a typing speed to work toward, then start any lesson.', 14).pack(anchor='w', pady=8)
        self.label(body, 'Your goal will appear with your lesson results. You can turn it off at any time.', 11).pack(anchor='w', pady=5)
        row = tk.Frame(body, bg=COLORS['bg']); row.pack(anchor='w', pady=15)
        self.label(row, 'Speed goal (WPM):', 14).pack(side='left', padx=(0,12))
        goal = tk.StringVar(value='20')
        tk.Spinbox(row, from_=5, to=150, increment=5, width=6, textvariable=goal,
                   font=('Consolas',15)).pack(side='left')
        def proceed():
            try: self.speed_goal = max(5, min(150, int(goal.get())))
            except ValueError:
                messagebox.showerror('Goal', 'Enter a goal between 5 and 150 WPM.')
                return
            self.display_home()
            messagebox.showinfo('Speed goal activated',f'Your target is {self.speed_goal} WPM.\nSelect a lesson and exercise to begin.')
        self.button(body, 'Set goal and choose a lesson', proceed).pack(anchor='w', pady=8)
        self.button(body, 'Turn speed goal off', self.disable_speed_goal).pack(anchor='w', pady=8)

    def disable_speed_goal(self):
        self.speed_goal = None
        self.display_home()

    def show_sentence_test(self):
        """Sentence speed tests for the independent curriculum."""
        self.clear()
        panel = tk.Frame(self.root, bg=COLORS['bg'])
        panel.pack(fill='both', expand=True, padx=32, pady=16)
        self.label(panel, 'SENTENCE SPEED TEST', 24, COLORS['accent'], True).pack(pady=(0,8))
        self.label(panel, 'Type complete sentences. Press Enter to finish each sentence. The clock pauses between sentences.', 12,
                   wraplength=1000).pack(pady=(0,8))
        self.button(panel, '← Main menu', self.display_home).pack(anchor='w', pady=(0,8))
        self.label(panel, 'Choose a test:', 13, COLORS['accent'], True).pack(anchor='w', pady=5)
        for name, sentences in SENTENCE_SETS.items():
            self.button(panel, f'{name}  •  {len(sentences)} sentences',
                        lambda n=name: self.start_sentence_test(n)).pack(anchor='w', fill='x', pady=5)
        self.label(panel, 'Choose a set to practice speed and accuracy with complete sentences.', 11).pack(anchor='w', pady=18)

    def start_sentence_test(self, name):
        self.sentence_name = name
        self.sentence_items = SENTENCE_SETS[name]
        self.sentence_index = 0
        self.sentence_attempts = []
        self.sentence_elapsed = 0.0
        self.sentence_started = None
        self.sentence_key_mistakes = 0
        self.sentence_complete = False
        self.clear()
        panel = tk.Frame(self.root, bg=COLORS['bg'])
        panel.pack(fill='both', expand=True, padx=30, pady=15)
        self.label(panel, f'SENTENCE TEST  •  {name}', 22, COLORS['accent'], True).pack(pady=(0,10))
        self.button(panel, '← Sentence tests', self.show_sentence_test).pack(anchor='w', pady=(0,10))
        self.sentence_status = self.label(panel, '', 13, COLORS['accent'])
        self.sentence_status.pack(pady=8)
        self.label(panel, 'COPY THIS SENTENCE', 11, COLORS['accent'], True).pack(pady=(4,5))
        self.sentence_target = self.label(panel, '', 17, bold=True, wraplength=920, justify='center')
        self.sentence_target.pack(fill='x', padx=12, pady=(4,14))
        self.label(panel, 'YOUR TYPING', 11, COLORS['accent'], True).pack(pady=(0,4))
        self.sentence_entry = tk.Entry(panel, font=('Consolas', 17), bg='white', fg='#101827')
        self.sentence_entry.pack(fill='x', padx=12, pady=(0,8))
        self.sentence_entry.bind('<KeyPress>', self.sentence_keypress)
        self.sentence_entry.bind('<KeyRelease>', self.sentence_feedback)
        self.sentence_entry.bind('<Return>', self.sentence_submit)
        self.sentence_entry.bind('<<Paste>>', lambda e: 'break')
        self.sentence_hint = self.label(panel, '', 12, wraplength=900)
        self.sentence_hint.pack(pady=7)
        self.button(panel, 'Finish Sentence  (Enter)', self.sentence_submit).pack(pady=6)
        self.sentence_guide = KeyboardGuide(panel)
        self.sentence_guide.pack(fill='both', expand=True, padx=12, pady=8)
        self.sentence_show_line()

    def sentence_show_line(self):
        if self.sentence_index >= len(self.sentence_items):
            self.finish_sentence_test()
            return
        self.sentence_started = None
        self.sentence_line_mistakes = 0
        self.sentence_status.config(text=f'Sentence {self.sentence_index+1} of {len(self.sentence_items)}  •  Ready — timer paused')
        current = self.sentence_items[self.sentence_index]
        self.sentence_target.config(text=current)
        self.sentence_entry.delete(0,'end')
        self.sentence_hint.config(text='Start when ready. Press Enter to stop timing and submit.', fg=COLORS['ink'])
        self.sentence_guide.set_next(current[:1])
        self.sentence_entry.focus_set()

    def sentence_keypress(self, event):
        if self.sentence_complete or self.sentence_index >= len(self.sentence_items): return
        if event.keysym in ('Return','BackSpace') or not event.char or not event.char.isprintable(): return
        if self.sentence_started is None:
            self.sentence_started = time.monotonic()
            self.sentence_status.config(text=f'Sentence {self.sentence_index+1} of {len(self.sentence_items)}  •  Timing')
        typed = self.sentence_entry.get()
        expected = self.sentence_items[self.sentence_index]
        if len(typed) >= len(expected) or event.char != expected[len(typed)]:
            self.sentence_line_mistakes += 1

    def sentence_feedback(self, event=None):
        if self.sentence_complete or self.sentence_index >= len(self.sentence_items): return
        text = self.sentence_entry.get()
        goal = self.sentence_items[self.sentence_index]
        self.sentence_guide.set_next(goal[len(text)] if len(text) < len(goal) else '')
        good = sum(a == b for a, b in zip(text, goal))
        self.sentence_hint.config(text=f'{good} matching characters  •  {max(0,len(goal)-len(text))} remaining  •  Press Enter to submit',
                                  fg=COLORS['correct'] if good == len(text) else COLORS['wrong'])

    def sentence_submit(self, event=None):
        if self.sentence_complete: return 'break'
        if self.sentence_started is not None:
            self.sentence_elapsed += time.monotonic() - self.sentence_started
            self.sentence_started = None
        typed = self.sentence_entry.get()
        if not typed:
            self.sentence_hint.config(text='Type the sentence first, then press Enter.', fg=COLORS['wrong'])
            return 'break'
        goal = self.sentence_items[self.sentence_index]
        if typed != goal:
            errors = sum(a != b for a,b in zip(goal,typed)) + abs(len(goal)-len(typed))
            if not messagebox.askyesno('Check your typing',
                    f'There are {errors} differences from the sentence. Continue anyway?\nSelect No to make corrections.', parent=self.root):
                self.sentence_hint.config(text='Make your corrections, then press Enter. Timing continues when you type again.', fg=COLORS['accent'])
                return 'break'
        self.sentence_attempts.append((goal, typed, self.sentence_line_mistakes))
        self.sentence_index += 1
        self.sentence_show_line()
        return 'break'

    def finish_sentence_test(self):
        self.sentence_complete = True
        scores = calculate_score(self.sentence_attempts, self.sentence_elapsed)
        record = dict(student=self.profile,timestamp=datetime.now().isoformat(timespec='seconds'),
                      lesson=None,section=None,title=f'Sentence Speed Test — {self.sentence_name}',
                      mode='Sentence Speed Test', lines=len(self.sentence_attempts),
                      seconds=round(self.sentence_elapsed,1),estimated_wpm=scores['wpm'],
                      accuracy_pct=scores['accuracy'],errors=scores['errors'],
                      key_mistakes=scores['key_mistakes'],scoring_version='v1.0-sentences')
        self.save_result(record)
        self.clear()
        panel=tk.Frame(self.root,bg=COLORS['bg']);panel.pack(padx=32,pady=55)
        self.label(panel, 'SENTENCES COMPLETE!', 24, COLORS['accent'], True).pack(pady=10)
        self.label(panel, f'{scores["wpm"]:.1f} WPM   •   {scores["accuracy"]:.1f}% accuracy', 19, COLORS['correct'],True).pack(pady=12)
        self.label(panel, f'{scores["errors"]} uncorrected differences   •   {scores["key_mistakes"]} incorrect keystrokes   •   {self.sentence_elapsed:.1f} active seconds', 12).pack(pady=6)
        self.label(panel, 'Results saved. Breaks between sentences do not affect your typing speed.', 11).pack(pady=9)
        controls=tk.Frame(panel,bg=COLORS['bg']);controls.pack(pady=12)
        for caption, action in [('Try Again',lambda:self.start_sentence_test(self.sentence_name)),
                                ('Choose Another Test',self.show_sentence_test),('Main Menu',self.display_home),('Progress and Settings',self.show_reports)]:
            self.button(controls,caption,action).pack(side='left',padx=5)

    def show_game(self):
        # Optional original practice game.
        self.clear()
        self.label(self.root, 'KEYBOARD SPRINT', 24, COLORS['accent'], True).pack(pady=(24,8))
        self.label(self.root, 'Type 12 different words as quickly and accurately as you can.', 11).pack(pady=6)
        self.button(self.root,'← Home',self.display_home).pack(anchor='w',padx=25)
        self.game_words=make_sprint_round(SPRINT_WORDS, self.previous_sprint, 12)
        self.previous_sprint=list(self.game_words)
        self.game_step=0;self.game_misses=0;self.game_started=None
        self.game_status=self.label(self.root,'Word 1 of 12',14);self.game_status.pack(pady=(50,12))
        self.game_target=self.label(self.root,self.game_words[0],32,COLORS['accent'],True)
        self.game_target.pack(pady=20)
        self.game_input=tk.Entry(self.root,font=('Consolas',24),justify='center',width=25)
        self.game_input.pack(pady=12)
        self.game_input.bind('<Return>',self.game_check)
        self.game_input.focus_set()
        self.game_tip=self.label(self.root,'Type the word and press Enter',12)
        self.game_tip.pack(pady=10)
        self.guide=KeyboardGuide(self.root);self.guide.pack(fill='both',expand=True,padx=25,pady=10)
        self.guide.set_next(self.game_words[0][0])
        self.game_input.bind('<KeyRelease>',self.game_feedback)

    def game_feedback(self, event=None):
        if self.game_started is None and self.game_input.get():self.game_started=time.monotonic()
        if self.game_step>=len(self.game_words):return
        text=self.game_input.get();target=self.game_words[self.game_step]
        self.guide.set_next(target[len(text)] if len(text)<len(target) else '')

    def game_check(self,event=None):
        if self.game_step>=len(self.game_words):return 'break'
        expected=self.game_words[self.game_step]
        typed=self.game_input.get().strip()
        if typed!=expected:
            self.game_misses+=1
            self.game_tip.config(text='Try again — match the displayed word.',fg=COLORS['wrong'])
            self.game_input.delete(0,'end');self.guide.set_next(expected[0]);return 'break'
        self.game_step+=1
        if self.game_step==len(self.game_words):
            seconds=max(1,time.monotonic()-(self.game_started or time.monotonic()))
            count=sum(len(w) for w in self.game_words)
            wpm=round(count/5*60/seconds,1)
            record=dict(student=self.profile,timestamp=datetime.now().isoformat(timespec='seconds'),
                        lesson=None,section=None,title='Keyboard Sprint',mode='Keyboard Sprint',lines=12,
                        seconds=round(seconds,1),estimated_wpm=wpm,
                        accuracy_pct=round(100*12/(12+self.game_misses),1),errors=self.game_misses)
            self.save_result(record)
            self.clear()
            self.label(self.root,'KEYBOARD SPRINT COMPLETE!',24,COLORS['accent'],True).pack(pady=(100,20))
            self.label(self.root,f'{wpm} estimated WPM • {self.game_misses} retries • {seconds:.1f} seconds',16).pack(pady=18)
            self.button(self.root,'Play again',self.show_game).pack(pady=10)
            self.button(self.root,'Home',self.display_home).pack(pady=10)
            return 'break'
        self.game_target.config(text=self.game_words[self.game_step]);self.game_input.delete(0,'end')
        self.game_status.config(text=f'Word {self.game_step+1} of 12')
        self.game_tip.config(text='Nice! Keep going.',fg=COLORS['correct'])
        self.guide.set_next(self.game_words[self.game_step][0]);return 'break'

    def clear(self):
        for child in self.root.winfo_children():
            child.destroy()

    def label(self, parent, text, size=14, color=None, bold=False, **kw):
        return tk.Label(parent, text=text, bg=COLORS['bg'], fg=color or COLORS['ink'],
                        font=('Consolas', size, 'bold' if bold else 'normal'), **kw)

    def button(self, parent, text, command):
        return tk.Button(parent, text=text, command=command, bg=COLORS['panel'],
                         fg=COLORS['ink'], activebackground='#2744ad',
                         activeforeground='white', font=('Consolas', 12),
                         padx=14, pady=7, bd=1, relief='solid', cursor='hand2')

    def display_home(self):
        self.clear()
        # Centering a maximum-width content column avoids a disconnected scrollbar
        # and too-wide lesson buttons on large monitors.
        body = tk.Frame(self.root, bg=COLORS['bg'])
        body.pack(fill='both', expand=True, padx=20, pady=(8, 5))
        center = tk.Frame(body, bg=COLORS['bg'])
        center.pack(anchor='n', expand=False)
        self.label(center, 'ALPHABETIC KEYBOARDING REVIVED', 26, COLORS['accent'], True).pack(pady=(7, 3))
        self.label(center, 'Learn • Practice • Track your progress', 12).pack(pady=(0, 7))
        # Two compact tool rows prevent labels from clipping on normal laptop displays.
        tool_rows = [
            [('Student: '+self.profile+'  ✎', self.change_profile),
             ('Progress and Settings', self.show_reports), ('Keyboard Sprint', self.show_game)],
            [('Sentence Speed Test', self.show_sentence_test), ('Technique tips', self.show_technique), ('Speed builder', self.show_speed_builder), ('Help & About', self.show_help)],
        ]
        for row in tool_rows:
            bar = tk.Frame(center, bg=COLORS['bg'])
            bar.pack(pady=(0, 3))
            for title, action in row:
                self.button(bar, title, action).pack(side='left', padx=5)
        self.label(center, 'CHOOSE A LESSON' + (f'  •  SPEED GOAL: {self.speed_goal} WPM' if self.speed_goal else ''), 15, COLORS['ink'], True).pack(pady=(0, 7))
        grid = tk.Frame(center, bg=COLORS['bg']); grid.pack()
        for col in range(2):
            grid.grid_columnconfigure(col, minsize=370, weight=1)
        for lesson_num in range(1,19):
            title = self.menus.get(lesson_num, f'Lesson {lesson_num}')
            count = len(self.lessons.get(lesson_num, []))
            # Two-column, nine-row layout: no pointless full-screen scrollbar.
            caption = f'{lesson_num:02d}   {title}  ·  {count} exercises'
            b = self.button(grid, caption, lambda n=lesson_num: self.open_lesson(n))
            b.config(anchor='w', width=41, height=2, pady=0, wraplength=375, justify='left')
            b.grid(row=(lesson_num-1)%9, column=(lesson_num-1)//9,
                   padx=7, pady=1, sticky='ew')

    def open_lesson(self, lesson_num):
        self.clear()
        self.lesson_number = lesson_num
        self.label(self.root, f'LESSON {lesson_num}: {self.menus.get(lesson_num, "")}', 20,
                   COLORS['accent'], True).pack(pady=(24, 16))
        self.button(self.root, '← All lessons', self.display_home).pack(anchor='w', padx=24)
        sections = self.lessons.get(lesson_num, [])
        if not sections:
            self.label(self.root, 'No typing exercises are currently available for this lesson.').pack(pady=40)
            return
        # Keep lesson navigation at a comfortable width, even on a 4K display.
        outer = tk.Frame(self.root, bg=COLORS['bg'])
        outer.pack(fill='both', expand=True, padx=35, pady=15)
        listing = tk.Frame(outer, bg=COLORS['bg'])
        listing.pack(anchor='n')
        self.label(listing, 'Choose an activity below. You can preview it before starting.', 11).pack(pady=(2,14))
        for s in sections:
            b = self.button(listing, f'{s["id"]}.  {s["title"]}   •   {len(s["lines"])} lines',
                            lambda sec=s: self.introduce_section(sec))
            b.config(width=64, anchor='w', wraplength=650, justify='left')
            b.pack(pady=4)

    def introduce_section(self, section, mode=None):
        """Exercise preview and finger placement guide."""
        self.section = section
        self.mode = mode or 'Practice'
        self.clear()
        panel = tk.Frame(self.root, bg=COLORS['bg'])
        panel.pack(fill='both', expand=True, padx=35, pady=20)
        self.label(panel, f'LESSON {self.lesson_number}  •  READY TO PRACTICE', 23, COLORS['accent'], True).pack(pady=(4,12))
        self.label(panel, section['title'], 20, bold=True, wraplength=800).pack(pady=(0,10))
        self.label(panel, f'{len(section["lines"])} lines • Timer starts with your first character and stops on Enter.', 12).pack(pady=(0,8))
        # Choose the next physical key directly from this section's first line.
        # Preview the first typing character.
        sample = section['lines'][0]
        self.label(panel, 'YOUR FIRST LINE', 12, COLORS['accent'], True).pack(pady=(5,5))
        self.label(panel, sample, 16, bold=True, wraplength=900).pack(pady=(0,10))
        self.label(panel, 'The highlighted key and finger show where to start. Keep your fingers near the home row.', 11,
                   wraplength=900).pack(pady=(0,5))
        guide = KeyboardGuide(panel)
        guide.pack(fill='x', padx=10)
        guide.set_next(sample[0] if sample else '')
        controls = tk.Frame(panel, bg=COLORS['bg']); controls.pack(pady=(14,8))
        self.button(controls, 'Start Practice', lambda: self.start_section(section,self.mode)).pack(side='left',padx=8)
        self.button(controls, 'Start Timed Test', lambda: self.start_section(section,'Timed Test')).pack(side='left',padx=8)
        self.button(controls, 'Back to exercises', lambda: self.open_lesson(self.lesson_number)).pack(side='left',padx=8)

    def show_help(self):
        """Browse student help by topic; no development/change log language."""
        self.clear()
        header = tk.Frame(self.root, bg=COLORS['bg'])
        header.pack(fill='x', padx=30, pady=(14, 6))
        self.label(header, 'HELP & ABOUT', 24, COLORS['accent'], True).pack(side='left')
        self.button(header, '← Main Menu', self.display_home).pack(side='right')
        self.label(self.root, 'Click a help topic below to see what it does and how to use it.',
                   13, wraplength=900).pack(anchor='w', padx=30, pady=(0, 12))

        topics = [
            ('MAIN MENU', [
                ('Student', 'Choose the name used for your lessons and scores. Enter a different name to switch students or create a new student.'),
                ('Choose a Lesson', 'Select one of the 18 lessons, then choose an exercise. Read the preview and begin when you are ready.'),
                ('Progress and Settings', 'View lesson history, typing speed, accuracy, and errors. Save or export reports, back up and restore records, clear selected student results, or reset the program to its starting settings.'),
                ('Keyboard Sprint', 'Type each word and press Enter. A round contains 12 words, followed by your speed and accuracy results.'),
                ('Sentence Speed Test', 'Choose a set of sentences. Type each one, press Enter, and review your speed and accuracy at the end.'),
                ('Technique Tips', 'Read advice about posture, hand position, and comfortable typing habits.'),
                ('Speed Builder', 'Choose a words-per-minute target and practice an exercise to see whether you reach it.'),
            ]),
            ('TYPING LESSONS', [
                ('Practice', 'Learn with the highlighted keyboard and finger guide. Use Backspace when you want to correct what you typed.'),
                ('Timed Test', 'Type the exercise to measure speed and accuracy. Incorrect keys can still count as errors even after you correct them.'),
                ('Lesson Timer', 'The timer begins when you type the first character of a line. Press Enter to finish the line and stop the timer. It remains paused until you start typing the next line.'),
                ('After an Exercise', 'Choose Next Exercise / Lesson to continue, Repeat Exercise to try again, View Student Report to check your results, or Return to Menu.'),
            ]),
            ('REPORTS & RECORDS', [
                ('Save Summary', 'Save a readable summary of the selected student’s progress.'),
                ('Export for Excel', 'Save results in a CSV file that can be opened with Excel or other spreadsheet programs.'),
                ('Back Up Progress', 'Make a ZIP backup of the student results and selected student name.'),
                ('Restore Progress', 'Bring results back from a saved backup. Imported results are merged with existing records.'),
                ('Clear Reports', 'Delete results for the current student, students you choose, or all students. You can make a backup and must confirm before deletion.'),
                ('Factory Reset', 'Clear all saved results, return to the default Student selection, and reset the speed goal. Lessons and activities remain available. A backup and confirmation are offered first.'),
            ]),
            ('ABOUT', [
                ('About the Program', 'Alphabetic Keyboarding Revived is an independently developed Windows typing tutor with guided lessons, word practice, sentence tests, and student reports.\n\nInspired by the keyboarding education software of the 1990s, with a historical acknowledgment to Haugo, Hausmann, and Jackson, authors credited on the 1994 DOS program of the same name.\n\nThis application is not affiliated with or endorsed by the original authors or publisher and does not include the original program or lesson files.'),
                            ]),
        ]

        main = tk.Frame(self.root, bg=COLORS['bg'])
        main.pack(fill='both', expand=True, padx=30, pady=(0, 18))
        nav = tk.Frame(main, bg=COLORS['panel'], width=285)
        nav.pack(side='left', fill='y', padx=(0, 16))
        nav.pack_propagate(False)
        nav_canvas = tk.Canvas(nav, bg=COLORS['panel'], highlightthickness=0, width=270)
        nav_scroll = ttk.Scrollbar(nav, orient='vertical', command=nav_canvas.yview)
        nav_canvas.configure(yscrollcommand=nav_scroll.set)
        nav_scroll.pack(side='right', fill='y')
        nav_canvas.pack(side='left', fill='both', expand=True)
        nav_content = tk.Frame(nav_canvas, bg=COLORS['panel'])
        nav_window = nav_canvas.create_window((0, 0), window=nav_content, anchor='nw')
        nav_content.bind('<Configure>', lambda event: nav_canvas.configure(scrollregion=nav_canvas.bbox('all')))
        nav_canvas.bind('<Configure>', lambda event: nav_canvas.itemconfigure(nav_window, width=event.width))

        detail = tk.Frame(main, bg=COLORS['panel'], padx=28, pady=26)
        detail.pack(side='left', fill='both', expand=True)
        heading = tk.Label(detail, text='Select a help topic', bg=COLORS['panel'],
                           fg=COLORS['accent'], font=('Segoe UI', 21, 'bold'), anchor='w')
        heading.pack(anchor='w', fill='x', pady=(0, 18))
        description = tk.Label(detail, text='Choose any button on the left to read instructions for that feature.',
                               bg=COLORS['panel'], fg=COLORS['ink'], font=('Segoe UI', 14),
                               anchor='nw', justify='left', wraplength=650)
        description.pack(anchor='w', fill='x')
        detail.bind('<Configure>', lambda event: description.configure(wraplength=max(240, event.width - 65)))
        selected = {'button': None}
        def show_topic(name, explanation, button):
            if selected['button'] is not None:
                selected['button'].configure(bg=COLORS['bg'], fg=COLORS['ink'])
            selected['button'] = button
            button.configure(bg='#3458bc', fg='white')
            heading.configure(text=name)
            description.configure(text=explanation)

        for category, entries in topics:
            tk.Label(nav_content, text=category, bg=COLORS['panel'], fg=COLORS['accent'],
                     font=('Segoe UI', 10, 'bold'), anchor='w').pack(fill='x', padx=12, pady=(14, 5))
            for name, explanation in entries:
                btn = tk.Button(nav_content, text=name, bg=COLORS['bg'], fg=COLORS['ink'],
                                activebackground='#3458bc', activeforeground='white',
                                font=('Segoe UI', 11), relief='flat', anchor='w',
                                padx=12, pady=7, cursor='hand2')
                btn.configure(command=lambda n=name, e=explanation, b=btn: show_topic(n, e, b))
                btn.pack(fill='x', padx=9, pady=2)

        # Wheel scrolling is limited to the topic list, not the whole application.
        def scroll_topics(event):
            if event.delta:
                nav_canvas.yview_scroll(-int(event.delta / 120), 'units')
            return 'break'
        for widget in (nav_canvas, nav_content):
            widget.bind('<MouseWheel>', scroll_topics)
        for child in nav_content.winfo_children():
            child.bind('<MouseWheel>', scroll_topics)

    def start_section(self, section, mode=None):
        self.section = section
        self.mode = mode or 'Practice'
        self.index = 0
        self.line_started = None
        self.elapsed_typing = 0.0
        self.complete = False
        self.attempts = []
        self.mistake_keys = 0
        self.entry_changes = 0
        self.show_practice()

    def section_position(self):
        sections = self.lessons.get(self.lesson_number, [])
        # Prefer the exact selected exercise; IDs aren't guaranteed unique across
        # all versions of the lesson data.
        for i, sec in enumerate(sections):
            if sec is self.section:
                return i
        return next((i for i, sec in enumerate(sections) if sec['id'] == self.section['id'] and sec['title'] == self.section['title']), -1)

    def next_section(self):
        sections = self.lessons.get(self.lesson_number, [])
        pos = self.section_position()
        if pos < 0:
            self.open_lesson(self.lesson_number)
            return
        if pos + 1 < len(sections):
            self.introduce_section(sections[pos+1],self.mode)
        elif self.lesson_number < 18:
            # Next means actually advance to the next available exercise, not
            # show another chooser and leave the student wondering if it advanced.
            for next_lesson in range(self.lesson_number+1,19):
                if self.lessons.get(next_lesson):
                    self.lesson_number = next_lesson
                    self.introduce_section(self.lessons[next_lesson][0], self.mode)
                    return
            self.display_home()
        else:
            self.display_home()

    def show_practice(self):
        self.clear()
        self.label(self.root, f'LESSON {self.lesson_number}  •  {self.section["title"]}',
                   19, COLORS['accent'], True).pack(pady=(15, 7))
        nav = tk.Frame(self.root, bg=COLORS['bg']); nav.pack(fill='x', padx=24, pady=4)
        self.button(nav, '← Exercises', lambda: self.open_lesson(self.lesson_number)).pack(side='left')
        self.button(nav, 'Restart exercise', lambda: self.start_section(self.section,self.mode)).pack(side='right')
        self.button(nav, 'Switch to ' + ('Timed Test' if self.mode=='Practice' else 'Practice'),
                    lambda: self.start_section(self.section,'Timed Test' if self.mode=='Practice' else 'Practice')).pack(side='right',padx=10)
        self.status = self.label(self.root, '', 11); self.status.pack(pady=(7,4))
        help_text = ('Practice: follow the keyboard and correct mistakes with Backspace.' if self.mode=='Practice' else
                     'Timed Test: correct your typing if needed; mistakes still count.')
        self.label(self.root, help_text, 11, COLORS['accent']).pack(pady=(0,3))
        self.label(self.root, 'COPY THIS LINE', 11, COLORS['accent'],True).pack()
        self.target = self.label(self.root, '', 19, bold=True, wraplength=980, justify='left')
        self.target.pack(padx=25, pady=(5,8))
        self.label(self.root, 'YOUR TYPING', 11, COLORS['accent'],True).pack()
        self.entry = tk.Entry(self.root, font=('Consolas', 19), bg='white', fg='#111',
                              insertbackground='#111', width=65)
        self.entry.pack(padx=40, pady=(6,7), fill='x')
        self.entry.bind('<KeyPress>', self.on_practice_keypress)
        self.entry.bind('<KeyRelease>', self.update_feedback)
        self.entry.bind('<Return>', self.submit)
        self.entry.bind('<<Paste>>', lambda event: 'break')
        self.feedback = self.label(self.root, '', 11); self.feedback.pack(pady=(0,4))
        self.button(self.root, 'Finish Line  (Enter)', self.submit).pack(pady=3)
        self.guide = KeyboardGuide(self.root); self.guide.pack(fill='both', expand=True,padx=22,pady=(4,0))
        self.show_line()

    def show_line(self):
        items = self.section['lines']
        if self.index >= len(items):
            self.finish(); return
        self.line_started = None
        self.line_mistakes = 0
        self.last_text = ''
        self.status.config(text=f'{self.mode}  •  Line {self.index+1} of {len(items)}  •  Ready (timer paused)  •  Press Enter to advance')
        self.target.config(text=items[self.index])

        self.entry.delete(0,'end'); self.entry.focus_set()
        if items[self.index] in items[:self.index]:
            first = items.index(items[self.index]) + 1
            hint = f'Practice repeat: same as line {first}. Type when ready, then press Enter.'
            self.feedback.config(text=hint, fg=COLORS['accent'])
        else:
            self.feedback.config(text='Start when ready. Press Enter to finish this line.',fg=COLORS['ink'])
        self.guide.set_next(items[self.index][:1])

    def on_practice_keypress(self, event):
        # Ignore function/navigation keys and Enter. The timer starts only on typing.
        if (self.line_started is None and not self.complete
                and event.char and event.char.isprintable() and event.keysym != 'Return'):
            self.line_started = time.monotonic()
            self.status.config(text=f'{self.mode}  •  Line {self.index+1} of {len(self.section["lines"])}  •  Timing')
        # Count an incorrect key when pressed, even if corrected later.
        if event.char and event.char.isprintable() and event.keysym != 'Return':
            pos = len(self.entry.get())
            expected = self.section['lines'][self.index]
            if pos >= len(expected) or event.char != expected[pos]:
                self.line_mistakes += 1

    def pause_line_timer(self):
        if self.line_started is not None:
            self.elapsed_typing += time.monotonic() - self.line_started
            self.line_started = None

    def update_feedback(self, event=None):
        if self.complete or self.index >= len(self.section['lines']):return
        typed = self.entry.get(); original = self.section['lines'][self.index]
        matched = sum(a == b for a,b in zip(original,typed))
        self.guide.set_next(original[len(typed)] if len(typed) < len(original) else '')
        remainder = max(0,len(original)-len(typed))
        self.feedback.config(text=f'{matched} matching positions  •  {remainder} characters remaining  •  Enter to finish',
            fg=COLORS['correct'] if matched==len(typed) else COLORS['wrong'])

    def submit(self, event=None):
        if self.complete:return 'break'
        self.pause_line_timer()  # Stop before any dialog appears.
        original = self.section['lines'][self.index]; typed = self.entry.get()
        if not typed:
            self.feedback.config(text='Type the line first, then press Enter.',fg=COLORS['wrong'])
            return 'break'
        if typed != original:
            errors = sum(a!=b for a,b in zip(typed,original))+abs(len(typed)-len(original))
            ok = messagebox.askyesno('Check your typing',
                f'There are {errors} differences from the practice line.\n\n'
                'Go to the next line? Select No to fix your typing.',parent=self.root)
            if not ok:
                # Continuing after a correction starts a new active interval on the next typed character.
                self.feedback.config(text='Make your corrections, then press Enter. Timing continues when you type again.',fg=COLORS['accent'])
                return 'break'
        self.attempts.append({'expected':original,'typed':typed,'key_mistakes':self.line_mistakes})
        self.index += 1
        self.show_line()
        return 'break'

    def finish(self):
        self.complete = True; self.pause_line_timer()
        elapsed = max(.01,self.elapsed_typing)
        chars = sum(len(a['typed']) for a in self.attempts)
        expected_chars = sum(len(a['expected']) for a in self.attempts)
        remaining_errors = sum(sum(x!=y for x,y in zip(a['expected'],a['typed']))
                      + abs(len(a['expected'])-len(a['typed'])) for a in self.attempts)
        key_mistakes = sum(a['key_mistakes'] for a in self.attempts)
        accuracy = 100*max(0,expected_chars-remaining_errors)/expected_chars if expected_chars else 0
        wpm = chars/5*60/elapsed
        goal_met = wpm >= self.speed_goal if self.speed_goal else None
        record = {'timestamp':datetime.now().isoformat(timespec='seconds'),
                  'lesson':self.lesson_number,'section':self.section['id'],'title':self.section['title'],
                  'student':self.profile,'mode':self.mode,'lines':len(self.attempts),
                  'seconds':round(elapsed,1),'estimated_wpm':round(wpm,1),
                  'accuracy_pct':round(accuracy,1),'errors':remaining_errors,
                  'key_mistakes':key_mistakes,'goal_wpm':self.speed_goal,'goal_met':goal_met,
                  'scoring_version':'v0.8'}
        self.save_result(record)
        self.clear()
        box = tk.Frame(self.root,bg=COLORS['bg']); box.pack(pady=(65,10))
        self.label(box,'GREAT WORK!',26,COLORS['accent'],True).pack(pady=8)
        self.label(box,f'Lesson {self.lesson_number}  •  {self.section["title"]}  •  {self.mode}',14).pack(pady=6)
        self.label(box,f'{wpm:.1f} WPM     |     {accuracy:.1f}% accuracy',20,COLORS['correct'],True).pack(pady=12)
        self.label(box,f'{remaining_errors} uncorrected differences  •  {key_mistakes} incorrect keystrokes  •  {elapsed:.1f} seconds active typing',13).pack(pady=6)
        if self.speed_goal:
            self.label(box,f'{self.speed_goal} WPM goal: '+('Reached!' if goal_met else 'Keep practicing'),14,COLORS['accent']).pack(pady=9)
        self.label(box,'Results saved. Breaks between lines do not affect your typing speed.',11).pack(pady=13)
        buttons = tk.Frame(box,bg=COLORS['bg']); buttons.pack(pady=15)
        self.button(buttons,'Next Activity →',self.next_section).pack(side='left',padx=7)
        self.button(buttons,'Main Menu',self.display_home).pack(side='left',padx=7)
        self.button(buttons,'Try Again',lambda:self.start_section(self.section,self.mode)).pack(side='left',padx=7)
        self.button(box,'Progress and Settings',self.show_reports).pack(pady=9)


if __name__ == '__main__':
    root = tk.Tk()
    try:
        App(root)
    except Exception as exc:
        messagebox.showerror('Unable to open Alphabetic Keyboarding', str(exc))
        raise
    root.mainloop()

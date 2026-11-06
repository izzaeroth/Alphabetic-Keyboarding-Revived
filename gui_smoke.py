import tempfile
from pathlib import Path
import app
import tkinter as tk
from unittest.mock import patch
with tempfile.TemporaryDirectory() as temp:
 app.SAVE=Path(temp)/'progress.json'; app.SETTINGS=Path(temp)/'settings.json'
 root=tk.Tk();root.geometry('1280x800')
 a=app.App(root);root.update()
 print('home bounds',root.winfo_width(),root.winfo_height())
 a.show_sentence_test();root.update()
 a.start_sentence_test('Everyday sentences');root.update()
 print('sentence controls',a.sentence_target.cget('text'))
 for line in list(a.sentence_items):
  a.sentence_entry.insert(0,line)
  a.sentence_started=__import__('time').monotonic()-3
  a.sentence_submit()
  root.update()
 print('sentence results',a.progress[-1]['mode'],a.progress[-1]['lines'])
 a.show_game();root.update()
 for word in list(a.game_words):
  a.game_input.insert(0,word)
  a.game_check();root.update()
 print('sprint results',a.progress[-1]['mode'])
 a.open_lesson(1);root.update();a.introduce_section(a.lessons[1][0]);root.update();a.start_section(a.lessons[1][0]);root.update()
 for line in a.section['lines']:
  a.entry.insert(0,line);a.line_started=__import__('time').monotonic()-1;a.submit();root.update()
 print('lesson complete',a.progress[-1]['lesson'])
 a.next_section();root.update()
 print('next section',a.section['title'])
 a.show_reports();root.update();print('reports render ok')
 root.destroy()

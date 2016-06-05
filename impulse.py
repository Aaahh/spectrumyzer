#!/usr/bin/python2

import curses, time, impulse

def bar(window, x, y, height, value):
  stop = value * height
  for i in range(height, -1, -1):
    if i < stop:
      color = (i * 4 / height) + 1
      window.addstr(y + height - i, x, "    ", curses.color_pair(color) | curses.A_BOLD | curses.A_REVERSE)
        

def draw(window):
  h,w = window.getmaxyx()
  audio_sample_array = impulse.getSnapshot(True)
  i = 0
  l = len(audio_sample_array) / 4
  step = l / ((w - 10) / 5)
  for x in range(3, w - 5, 5):
    value = audio_sample_array[i]
    bar(window, x, 3, h - 6 , value)
    i += step


def main(window):
  curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
  curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
  curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
  curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
  curses.curs_set(0)

  curses.use_default_colors()
  window.nodelay(True)
  window.clear()
  window.refresh()
  while window.getch() != 113 and window.getch() != 185:
    draw(window)
    window.refresh()
    time.sleep(0.05)
    window.clear()

  window.clear()
  window.refresh()

if __name__ == "__main__":
    curses.wrapper(main)

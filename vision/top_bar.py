"""The black line at the bottom of the game's top bar."""

# The top bar ends with a black line across the screen (Xiaomi y=226,
# OnePlus Nord 3 y=284; the status bar height differs). Black row =
# over 90 % of its pixels have every channel below 10. Searched in
# this band of the screen height: ads and loading screens have black
# rows higher up.
LINE_MAX_VALUE = 10
LINE_MIN_RATIO = 0.9
BAND_TOP = 0.06
BAND_BOTTOM = 0.15


def find_top_bar_line(image_bgr, min_rows):
  """Return the y of the top bar's black line, else None.

  It is the end of the first run of at least min_rows black rows in
  the top band. The first run, not the lowest black row: a black row
  lower in the restaurant (e.g. a night city) must not move the line
  down. A run reaching the band bottom is no line (e.g. a black
  screen).
  """
  height = image_bgr.shape[0]
  top = round(height * BAND_TOP)
  bottom = round(height * BAND_BOTTOM)
  black_pixels = image_bgr[top:bottom].max(axis=2) < LINE_MAX_VALUE
  black_rows = black_pixels.mean(axis=1) > LINE_MIN_RATIO
  run = 0
  for i, black in enumerate(black_rows):
    if black:
      run += 1
    elif run >= min_rows:
      return top + i - 1
    else:
      run = 0
  return None

"""
sandbox.py - Interactive testing tool for auto-eatventure

Templates are automatically scaled to match the detected device
resolution, the same way the bot scales them at runtime.

Commands:
  sc [name]                  - Take a screenshot. Optionally save it as
                               a template with the given name.
  save <name>                - Save the last screenshot as a new PNG
                               template to matching_screenshots/
  crop <x> <y> <w> <h> <name>
                             - Crop a region from the last screenshot
                               and save it as a template
  match <template> [threshold]
                             - Test HSV template matching against the
                               last screenshot
  match_gray <template> [threshold]
                             - Test grayscale matching against the
                               last screenshot
  match_all <template> [threshold]
                             - Find all matches (HSV, clustered) of the
                               template in the last screenshot
  match_box [threshold]      - Test box detection exactly as the bot
                               does (actions/boxes.py)
  diag [tmpl ...]            - Score all (or the listed) templates
                               against the last screenshot, annotate
  show                       - Open the last screenshot in the default
                               viewer
  show_annot                 - Show the last screenshot with match
                               annotations
  list                       - List available templates
  tap <x> <y>                - Tap a coordinate on the device
  help                       - Show this help
  q / quit                   - Exit

Annotations: RED circle = match above threshold,
             YELLOW circle = best location below threshold
"""

import os
import subprocess
import sys

import cv2

from actions.boxes import BOX_THRESHOLD
from android.device import Device
from bot import config
from coords.geometry import Point, Region
from coords.scaled import ScaledCoords
from vision import matching
from vision.templates import TEMPLATES_DIR, load_template

CAPTURED_PATH = 'captured_screenshots_on_the_fly/screenshot.png'
ANNOTATED_PATH = (
  'captured_screenshots_on_the_fly/annotated_screenshot.png')

DEFAULT_THRESHOLD = 0.8
# diag: a best score at least this high is "close" to a match
CLOSE_THRESHOLD = 0.6

# Radius of the circles marking matches in the annotated screenshot
ANNOTATION_RADIUS = 14

# BGR colors of the annotations
RED = (0, 0, 255)
ORANGE = (0, 165, 255)
YELLOW = (0, 255, 255)
GREEN = (0, 255, 0)

QUIT_COMMANDS = ('q', 'quit', 'exit')


class Sandbox:
  """State shared by the commands: the device, its scale, the
  templates and the last screenshot."""

  def __init__(self, device):
    self.device = device
    self.coords = ScaledCoords(*device.screen_size())
    self.templates = {}
    self.bgr = None
    self.hsv = None
    self.gray = None

  def load_templates(self):
    """Load all PNGs of TEMPLATES_DIR, resized to the device."""
    self.templates = {}
    for file_name in sorted(os.listdir(TEMPLATES_DIR)):
      name, extension = os.path.splitext(file_name)
      if extension.lower() != '.png':
        continue
      path = os.path.join(TEMPLATES_DIR, file_name)
      try:
        self.templates[name] = load_template(
          path, self.coords.x_scale, self.coords.y_scale)
      except FileNotFoundError as error:
        print(f'  {error} — skipped.')

  def capture(self):
    """Take a new screenshot and save it to CAPTURED_PATH."""
    self.bgr = self.device.screenshot()
    self.hsv = cv2.cvtColor(self.bgr, cv2.COLOR_BGR2HSV)
    self.gray = _gray(self.bgr)
    _save_image(self.bgr, CAPTURED_PATH)
    print(f'  Size: {self.bgr.shape[1]}x{self.bgr.shape[0]}')

  def save_template(self, image, name):
    """Save the image as template <name> and reload the templates."""
    _save_image(image, os.path.join(TEMPLATES_DIR, f'{name}.png'))
    self.load_templates()

  def has_screenshot(self):
    if self.bgr is None:
      print("  No screenshot yet. Run 'sc' first.")
      return False
    return True

  def template(self, name):
    """The template of this name, else None (with a message)."""
    if name not in self.templates:
      print(f"  Template '{name}' not found. "
            "Use 'list' to see available templates.")
      return None
    return self.templates[name]


# ── commands: each takes the Sandbox and the arguments (strings) ──────


def cmd_sc(sandbox, args):
  """Take a screenshot, optionally save it as a template."""
  print('  Capturing screenshot...')
  sandbox.capture()
  if args:
    sandbox.save_template(sandbox.bgr, args[0])
    print(f"  Template '{args[0]}' added.")


def cmd_save(sandbox, args):
  """Save the last screenshot as a template."""
  if not args:
    print('  Usage: save <name>')
  elif sandbox.has_screenshot():
    sandbox.save_template(sandbox.bgr, args[0])
    print(f"  Template '{args[0]}' added.")


def cmd_crop(sandbox, args):
  """Save a region of the last screenshot as a template."""
  if len(args) < 5:
    print('  Usage: crop <x> <y> <w> <h> <name>')
    return
  if not sandbox.has_screenshot():
    return
  try:
    x, y, width, height = (int(arg) for arg in args[:4])
  except ValueError:
    print('  All of x, y, w, h must be integers.')
    return
  name = args[4]
  image = Region(x, y, x + width, y + height).crop(sandbox.bgr)
  if image.size == 0:
    print('  Empty region — check coordinates.')
    return
  sandbox.save_template(image, name)
  print(f"  Cropped template '{name}' saved "
        f'({width}x{height} px at {x},{y}).')


def cmd_match(sandbox, args):
  _match_best(sandbox, args, 'match', _hsv_images)


def cmd_match_gray(sandbox, args):
  _match_best(sandbox, args, 'match_gray', _gray_images)


def cmd_match_all(sandbox, args):
  """All matches (HSV) of a template, clustered like the bot."""
  if not args:
    print('  Usage: match_all <template_name> [threshold]')
    return
  if not sandbox.has_screenshot():
    return
  template = sandbox.template(args[0])
  if template is None:
    return
  threshold = _threshold(args, 1, DEFAULT_THRESHOLD)
  points = matching.all_matches(sandbox.hsv, template.hsv, threshold)
  print(f'  Found {len(points)} match(es): {_points_text(points)}')
  if points:
    annotated = sandbox.bgr.copy()
    for point in points:
      _mark(annotated, point, RED)
      _frame(annotated, _template_region(point, template))
    _save_annotated(annotated)


def cmd_match_box(sandbox, args):
  """Same as actions.boxes.open_all(): all matches (BGR) of 'box',
  of 'box2' only when 'box' is not found."""
  if not sandbox.has_screenshot():
    return
  threshold = _threshold(args, 0, BOX_THRESHOLD)
  for name in ('box', 'box2'):
    template = sandbox.template(name)
    if template is None:
      continue
    points = matching.all_matches(sandbox.bgr, template.bgr, threshold)
    print(f'  {name}: {len(points)} match(es) at threshold '
          f'{threshold}: {_points_text(points)}')
    if points:
      annotated = sandbox.bgr.copy()
      for point in points:
        _mark(annotated, point, RED, name)
        _frame(annotated, _template_region(point, template))
      _save_annotated(annotated)
      return
  print('  No box found.')


def cmd_diag(sandbox, args):
  """Best HSV and grayscale score of each template, best first; the
  better of the two is annotated."""
  if sandbox.bgr is None:
    print('  Capturing screenshot first...')
    sandbox.capture()
  rows = _diag_rows(sandbox, args or sorted(sandbox.templates))

  print(f"\n  {'TEMPLATE':<35} {'HSV':>6}  {'GRAY':>6}  STATUS")
  print(f"  {'-' * 35} {'-' * 6}  {'-' * 6}  ------")
  annotated = sandbox.bgr.copy()
  for name, hsv, gray in rows:
    score, region = max(hsv, gray, key=lambda match: match[0])
    status, color = _diag_status(score)
    print(f'  {name:<35} {hsv[0]:>6.3f}  {gray[0]:>6.3f}  {status}')
    _mark(annotated, region.center, color, f'{score:.2f}')
  print()
  _save_annotated(annotated)
  print(f'  RED=match(>={DEFAULT_THRESHOLD})  '
        f'ORANGE=close(>={CLOSE_THRESHOLD})  '
        f'YELLOW=miss(<{CLOSE_THRESHOLD})')


def cmd_show(sandbox, _args):
  if sandbox.has_screenshot():
    _open_image(CAPTURED_PATH)


def cmd_show_annot(_sandbox, _args):
  if not os.path.exists(ANNOTATED_PATH):
    print('  No annotated screenshot yet. Run a match command first.')
  else:
    _open_image(ANNOTATED_PATH)


def cmd_list(sandbox, _args):
  """List the templates with their (scaled) sizes."""
  if not sandbox.templates:
    print('  No templates found.')
    return
  print(f'  Templates in {TEMPLATES_DIR}/:')
  for name, template in sorted(sandbox.templates.items()):
    print(f'    {name:<35} {template.width}x{template.height}px')


def cmd_tap(sandbox, args):
  """Tap a point (device pixels) on the device."""
  if len(args) < 2:
    print('  Usage: tap <x> <y>')
    return
  try:
    point = Point(int(args[0]), int(args[1]))
  except ValueError:
    print('  x and y must be integers.')
    return
  sandbox.device.tap(point)
  print(f'  Tapped ({point.x}, {point.y})')


def cmd_help(_sandbox, _args):
  print(__doc__)


COMMANDS = {
  'sc': cmd_sc,
  'save': cmd_save,
  'crop': cmd_crop,
  'match': cmd_match,
  'match_gray': cmd_match_gray,
  'match_all': cmd_match_all,
  'match_box': cmd_match_box,
  'diag': cmd_diag,
  'show': cmd_show,
  'show_annot': cmd_show_annot,
  'list': cmd_list,
  'tap': cmd_tap,
  'help': cmd_help,
}


# ── helpers ───────────────────────────────────────────────────────────


def _match_best(sandbox, args, command, images):
  """match / match_gray: the best match of one template.

  images(sandbox, template) gives the (screenshot, template) images
  to match in the wanted color space.
  """
  if not args:
    print(f'  Usage: {command} <template_name> [threshold]')
    return
  if not sandbox.has_screenshot():
    return
  template = sandbox.template(args[0])
  if template is None:
    return
  threshold = _threshold(args, 1, DEFAULT_THRESHOLD)
  score, region = matching.best_match(*images(sandbox, template))
  center = region.center
  matched = score >= threshold
  if matched:
    print(f'  MATCH at center=({center.x},{center.y})  '
          f'score={score:.4f}  (threshold={threshold})')
  else:
    print(f'  No match — best score={score:.4f} at '
          f'center=({center.x},{center.y})  threshold={threshold}')
  annotated = sandbox.bgr.copy()
  _mark(annotated, center, RED if matched else YELLOW)
  _frame(annotated, region)
  _save_annotated(annotated)


def _hsv_images(sandbox, template):
  return sandbox.hsv, template.hsv


def _gray_images(sandbox, template):
  return sandbox.gray, _gray(template.bgr)


def _gray(bgr):
  return cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)


def _threshold(args, index, default):
  """The threshold argument at the index, else the default."""
  return float(args[index]) if len(args) > index else default


def _diag_rows(sandbox, names):
  """(name, HSV match, gray match) of the templates, best first.

  A match is (score, Region) of matching.best_match().
  """
  rows = []
  for name in names:
    template = sandbox.templates.get(name)
    if template is None:
      print(f"  Template '{name}' not found — skipped.")
      continue
    hsv = matching.best_match(sandbox.hsv, template.hsv)
    gray = matching.best_match(sandbox.gray, _gray(template.bgr))
    rows.append((name, hsv, gray))
  rows.sort(key=lambda row: max(row[1][0], row[2][0]), reverse=True)
  return rows


def _diag_status(score):
  """(status text, annotation color) of a diag score."""
  if score >= DEFAULT_THRESHOLD:
    return '✓ match', RED
  if score >= CLOSE_THRESHOLD:
    return '~ close', ORANGE
  return '✗ miss', YELLOW


def _template_region(center, template):
  return Region.around(center, template.width // 2,
                       template.height // 2)


def _points_text(points):
  return [tuple(point) for point in points]


def _mark(image, center, color, label=''):
  """Circle the point in the image, with an optional label."""
  cv2.circle(image, center, ANNOTATION_RADIUS, color, thickness=3)
  if label:
    cv2.putText(image, label, (center.x + 8, center.y - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)


def _frame(image, region):
  cv2.rectangle(image, (region.left, region.top),
                (region.right, region.bottom), GREEN, 2)


def _save_annotated(image):
  _save_image(image, ANNOTATED_PATH)
  print("  Annotated screenshot saved — run 'show_annot' to view.")


def _save_image(image, path):
  os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
  cv2.imwrite(path, image)
  print(f'  Saved: {path}')


def _open_image(path):
  """Open the image in the OS default viewer."""
  if sys.platform == 'win32':
    os.startfile(os.path.abspath(path))  # pylint: disable=no-member
  else:
    # The viewer keeps running on its own, so no "with"
    # pylint: disable-next=consider-using-with
    subprocess.Popen(['xdg-open', path])


def _print_scale(sandbox):
  x_scale, y_scale = sandbox.coords.x_scale, sandbox.coords.y_scale
  if abs(x_scale - 1.0) > 0.001 or abs(y_scale - 1.0) > 0.001:
    print(f'  [sandbox] Templates scaled x={x_scale:.4f}, '
          f'y={y_scale:.4f} to match device resolution.')
  else:
    print('  [sandbox] Device matches reference resolution — '
          'templates used at original size.')


def run_commands(sandbox):
  """Read and run commands until quit."""
  while True:
    try:
      line = input('sandbox> ').strip()
    except (EOFError, KeyboardInterrupt):
      print('\nBye!')
      return
    if not line:
      continue
    command, *args = line.split()
    command = command.lower()
    if command in QUIT_COMMANDS:
      print('Bye!')
      return
    if command not in COMMANDS:
      print(f"  Unknown command '{command}'. "
            "Type 'help' for available commands.")
      continue
    try:
      COMMANDS[command](sandbox, args)
    except (ValueError, cv2.error) as error:
      print(f'  Error: {error}')


def main():
  """Connect to the device and run the sandbox."""
  print('=== auto-eatventure sandbox ===')
  print("Type 'help' for available commands.\n")
  device = Device(config.DEVICE_SERIAL)
  print(f'Connected to device: {device.serial}')
  sandbox = Sandbox(device)
  sandbox.load_templates()
  _print_scale(sandbox)
  run_commands(sandbox)


if __name__ == '__main__':
  main()

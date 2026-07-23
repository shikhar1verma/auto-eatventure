"""
sandbox.py - Interactive testing tool for auto-eatventure

Templates are automatically scaled to match the detected device resolution,
the same way adb_autoplay.py scales them at runtime.

Commands:
  sc [name]          - Take a screenshot. Optionally save as template with given name.
  save <name>        - Save the last screenshot as a new PNG template to matching_screenshots/
  crop <x> <y> <w> <h> <name>  - Crop region from last screenshot and save as template
  match <template> [threshold]     - Test HSV template matching against last screenshot
  match_gray <template> [threshold] - Test grayscale matching against last screenshot
  match_all <template> [threshold]  - Find all matches of template in last screenshot
  match_box [threshold]  - Test box detection exactly as main app does (color mask + matching)
  diag [tmpl ...]    - Score all (or listed) templates against last screenshot and annotate
  show               - Open the last screenshot in the default viewer
  show_annot         - Show last screenshot with match annotations
  list               - List available templates
  tap <x> <y>        - Tap a coordinate on the device
  help               - Show this help
  q / quit           - Exit

Annotations: RED circle = match above threshold, YELLOW circle = best location below threshold
"""

import os
import sys
import io
import subprocess
import numpy as np
import cv2
from PIL import Image
from adbutils import adb
from dotenv import load_dotenv
from scaled_coords import ScaledCoords, detect_resolution

load_dotenv()

CAPTURED_PATH = "./captured_screenshots_on_the_fly/screenshot.png"
TEMPLATES_DIR = "./matching_screenshots"
ANNOTATED_PATH = "./captured_screenshots_on_the_fly/annotated_screenshot.png"


def get_device():
    serial = os.getenv("device_serial", os.getenv("DEVICE_SERIAL", "")).strip()
    if serial:
        device = adb.device(serial=serial)
    else:
        devices = adb.device_list()
        if not devices:
            raise RuntimeError("No ADB devices connected. Connect your phone and enable USB Debugging.")
        device = devices[0]
        print(f"  [sandbox] No device_serial in .env — using first connected device: {device.serial}")
    print(f"Connected to device: {device.serial}")
    return device


def capture_screenshot(device) -> np.ndarray:
    """Capture screenshot from device, return as BGR numpy array."""
    adb_command = f"adb -s {device.serial} shell screencap -p"
    output = subprocess.check_output(adb_command.split())
    output = output.replace(b"\r\n", b"\n")
    pilimg = Image.open(io.BytesIO(output))
    pilimg.load()
    pilimg = pilimg.convert("RGB")
    bgr = np.array(pilimg)[:, :, ::-1].copy()
    return bgr


def save_image(bgr: np.ndarray, path: str):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    cv2.imwrite(path, bgr)
    print(f"  Saved: {path}")


def load_templates(directory: str) -> dict:
    templates = {}
    for fname in os.listdir(directory):
        if fname.lower().endswith(".png"):
            name = os.path.splitext(fname)[0]
            path = os.path.join(directory, fname)
            simple = cv2.imread(path)
            if simple is None:
                continue
            templates[name] = {
                "simple": simple,
                "grayscale": cv2.cvtColor(simple, cv2.COLOR_BGR2GRAY),
                "bgr2hsv": cv2.cvtColor(simple, cv2.COLOR_BGR2HSV),
                "path": path,
            }
    return templates


def resize_templates(templates: dict, x_scale: float, y_scale: float) -> dict:
    """Resize all loaded templates proportionally to the detected device resolution.

    Mirrors the scaling done by adb_autoplay.py so sandbox scores are comparable.
    """
    if abs(x_scale - 1.0) < 0.001 and abs(y_scale - 1.0) < 0.001:
        return templates
    resized = {}
    for name, data in templates.items():
        simple = data["simple"]
        h, w = simple.shape[:2]
        target_w = max(1, round(w * x_scale))
        target_h = max(1, round(h * y_scale))
        interp = cv2.INTER_AREA if (target_w < w or target_h < h) else cv2.INTER_LINEAR
        r_simple = cv2.resize(simple, (target_w, target_h), interpolation=interp)
        resized[name] = {
            "simple": r_simple,
            "grayscale": cv2.cvtColor(r_simple, cv2.COLOR_BGR2GRAY),
            "bgr2hsv": cv2.cvtColor(r_simple, cv2.COLOR_BGR2HSV),
            "path": data["path"],
        }
    return resized


def apply_box_mask(image: np.ndarray, tolerance: int = 2) -> np.ndarray:
    """Mirror of AutoEatventure.apply_box_mask — keeps only box-colored pixels."""
    colors = [(13, 152, 171), (14, 155, 140)]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    combined_mask = np.zeros_like(hsv[:, :, 0])
    for color in colors:
        lower = np.array([max(color[0] - tolerance, 0), max(color[1] - tolerance, 0), max(color[2] - tolerance, 0)])
        upper = np.array([min(color[0] + tolerance, 180), min(color[1] + tolerance, 255), min(color[2] + tolerance, 255)])
        combined_mask = cv2.bitwise_or(combined_mask, cv2.inRange(hsv, lower, upper))
    return cv2.bitwise_and(image, image, mask=combined_mask)


def count_nonzero_pixels(image: np.ndarray) -> int:
    """Count pixels that survived a mask (non-black)."""
    if len(image.shape) == 2:
        return int(np.count_nonzero(image))
    return int(np.count_nonzero(image[:, :, 0]) + np.count_nonzero(image[:, :, 1]) + np.count_nonzero(image[:, :, 2]))
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    print(f"  max_val={max_val:.4f}  max_loc={max_loc}  threshold={threshold}")
    if max_val >= threshold:
        return max_loc, max_val
    return None, max_val


def find_all_templates(image: np.ndarray, template: np.ndarray, threshold=0.8):
    h, w = template.shape[:2]
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    coords = [(int(x + w // 2), int(y + h // 2)) for x, y in zip(*locations[::-1])]
    return coords


def annotate_and_save(bgr: np.ndarray, point_list: list, path: str, sc: ScaledCoords, template_shape=None, color=(0, 0, 255)):
    annotated = bgr.copy()
    for x, y in point_list:
        cv2.circle(annotated, (x, y), radius=sc.annotation_radius, color=(0, 0, 255), thickness=3)
        if template_shape:
            h, w = template_shape[:2]
            cv2.rectangle(annotated, (x - w // 2, y - h // 2), (x + w // 2, y + h // 2), (0, 255, 0), 2)
    save_image(annotated, path)


def open_image(path: str):
    """Open image with OS default viewer."""
    if sys.platform == "win32":
        os.startfile(os.path.abspath(path))
    else:
        subprocess.Popen(["xdg-open", path])


def print_help():
    print(__doc__)


def main():
    print("=== auto-eatventure sandbox ===")
    print("Type 'help' for available commands.\n")

    device = get_device()
    actual_w, actual_h = detect_resolution(device)
    sc = ScaledCoords(actual_w, actual_h)
    templates = load_templates(TEMPLATES_DIR)
    templates = resize_templates(templates, sc.x_scale, sc.y_scale)
    if abs(sc.x_scale - 1.0) > 0.001 or abs(sc.y_scale - 1.0) > 0.001:
        print(f"  [sandbox] Templates scaled x={sc.x_scale:.4f}, y={sc.y_scale:.4f} to match device resolution.")
    else:
        print(f"  [sandbox] Device matches reference resolution — templates used at original size.")
    last_bgr: np.ndarray | None = None
    last_match_coords: list = []
    last_match_template_name: str | None = None

    while True:
        try:
            raw = input("sandbox> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not raw:
            continue

        parts = raw.split()
        cmd = parts[0].lower()

        # ── screenshot ────────────────────────────────────────────────────────
        if cmd == "sc":
            print("  Capturing screenshot...")
            last_bgr = capture_screenshot(device)
            save_image(last_bgr, CAPTURED_PATH)
            if len(parts) >= 2:
                template_name = parts[1]
                dest = os.path.join(TEMPLATES_DIR, f"{template_name}.png")
                save_image(last_bgr, dest)
                templates = load_templates(TEMPLATES_DIR)
                print(f"  Template '{template_name}' added.")
            print(f"  Size: {last_bgr.shape[1]}x{last_bgr.shape[0]}")

        # ── save last screenshot as template ──────────────────────────────────
        elif cmd == "save":
            if len(parts) < 2:
                print("  Usage: save <name>")
            elif last_bgr is None:
                print("  No screenshot captured yet. Run 'sc' first.")
            else:
                name = parts[1]
                dest = os.path.join(TEMPLATES_DIR, f"{name}.png")
                save_image(last_bgr, dest)
                templates = load_templates(TEMPLATES_DIR)
                print(f"  Template '{name}' added.")

        # ── crop region and save as template ─────────────────────────────────
        elif cmd == "crop":
            if len(parts) < 6:
                print("  Usage: crop <x> <y> <w> <h> <name>")
            elif last_bgr is None:
                print("  No screenshot captured yet. Run 'sc' first.")
            else:
                try:
                    x, y, w, h, name = int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]), parts[5]
                    region = last_bgr[y:y+h, x:x+w]
                    if region.size == 0:
                        print("  Empty region — check coordinates.")
                    else:
                        dest = os.path.join(TEMPLATES_DIR, f"{name}.png")
                        save_image(region, dest)
                        templates = load_templates(TEMPLATES_DIR)
                        print(f"  Cropped template '{name}' saved ({w}x{h} px at {x},{y}).")
                except ValueError:
                    print("  All of x, y, w, h must be integers.")

        # ── template matching (hsv) ───────────────────────────────────────────
        elif cmd == "match":
            if len(parts) < 2:
                print("  Usage: match <template_name> [threshold]")
            elif last_bgr is None:
                print("  No screenshot yet. Run 'sc' first.")
            else:
                name = parts[1]
                threshold = float(parts[2]) if len(parts) >= 3 else 0.8
                if name not in templates:
                    print(f"  Template '{name}' not found. Use 'list' to see available templates.")
                else:
                    hsv_sc = cv2.cvtColor(last_bgr, cv2.COLOR_BGR2HSV)
                    hsv_tmpl = templates[name]["bgr2hsv"]
                    h, w = hsv_tmpl.shape[:2]
                    result = cv2.matchTemplate(hsv_sc, hsv_tmpl, cv2.TM_CCOEFF_NORMED)
                    _, best_val, _, best_loc = cv2.minMaxLoc(result)
                    cx, cy = best_loc[0] + w // 2, best_loc[1] + h // 2
                    matched = best_val >= threshold
                    last_match_coords = [(cx, cy)]
                    last_match_template_name = name
                    color = (0, 0, 255) if matched else (0, 255, 255)  # red=match, yellow=miss
                    annotate_and_save(last_bgr, last_match_coords, ANNOTATED_PATH, sc, hsv_tmpl.shape, color=color)
                    if matched:
                        print(f"  MATCH at center=({cx},{cy})  score={best_val:.4f}  (threshold={threshold})")
                    else:
                        print(f"  No match — best score={best_val:.4f} at center=({cx},{cy})  threshold={threshold}")
                        print(f"  Yellow circle saved — run 'show_annot' to see where the best match was.")

        # ── grayscale matching ────────────────────────────────────────────────
        elif cmd == "match_gray":
            if len(parts) < 2:
                print("  Usage: match_gray <template_name> [threshold]")
            elif last_bgr is None:
                print("  No screenshot yet. Run 'sc' first.")
            else:
                name = parts[1]
                threshold = float(parts[2]) if len(parts) >= 3 else 0.8
                if name not in templates:
                    print(f"  Template '{name}' not found.")
                else:
                    gray_sc = cv2.cvtColor(last_bgr, cv2.COLOR_BGR2GRAY)
                    gray_tmpl = templates[name]["grayscale"]
                    h, w = gray_tmpl.shape[:2]
                    result = cv2.matchTemplate(gray_sc, gray_tmpl, cv2.TM_CCOEFF_NORMED)
                    _, best_val, _, best_loc = cv2.minMaxLoc(result)
                    cx, cy = best_loc[0] + w // 2, best_loc[1] + h // 2
                    matched = best_val >= threshold
                    last_match_coords = [(cx, cy)]
                    last_match_template_name = name
                    color = (0, 0, 255) if matched else (0, 255, 255)  # red=match, yellow=miss
                    annotate_and_save(last_bgr, last_match_coords, ANNOTATED_PATH, sc, gray_tmpl.shape, color=color)
                    if matched:
                        print(f"  MATCH at center=({cx},{cy})  score={best_val:.4f}  (threshold={threshold})")
                    else:
                        print(f"  No match — best score={best_val:.4f} at center=({cx},{cy})  threshold={threshold}")
                        print(f"  Yellow circle saved — run 'show_annot' to see where the best match was.")

        # ── find all matches ──────────────────────────────────────────────────
        elif cmd == "match_all":
            if len(parts) < 2:
                print("  Usage: match_all <template_name>")
            elif last_bgr is None:
                print("  No screenshot yet. Run 'sc' first.")
            else:
                name = parts[1]
                threshold = float(parts[2]) if len(parts) >= 3 else 0.8
                if name not in templates:
                    print(f"  Template '{name}' not found.")
                else:
                    hsv_sc = cv2.cvtColor(last_bgr, cv2.COLOR_BGR2HSV)
                    hsv_tmpl = templates[name]["bgr2hsv"]
                    coords = find_all_templates(hsv_sc, hsv_tmpl, threshold)
                    print(f"  Found {len(coords)} match(es): {coords}")
                    last_match_coords = coords
                    last_match_template_name = name
                    if coords:
                        annotate_and_save(last_bgr, coords, ANNOTATED_PATH, sc, hsv_tmpl.shape)

        # ── match_box: exact replica of main-app box detection ────────────────
        elif cmd == "match_box":
            if last_bgr is None:
                print("  No screenshot yet. Run 'sc' first.")
            else:
                threshold = float(parts[1]) if len(parts) >= 2 else 0.7
                masked_sc = apply_box_mask(last_bgr)
                nonzero_sc = count_nonzero_pixels(masked_sc)
                print(f"  Box-color pixels in screenshot: {nonzero_sc}")
                if nonzero_sc == 0:
                    print("  WARNING: color mask found NO pixels — box color not present on screen.")
                    print("  Box detection will always fail. Check if a box is actually visible on screen.")

                results = []
                for tmpl_name in ("box", "box2"):
                    if tmpl_name not in templates:
                        print(f"  Template '{tmpl_name}' not found — skipped.")
                        continue
                    masked_tmpl = apply_box_mask(templates[tmpl_name]["simple"])
                    nonzero_tmpl = count_nonzero_pixels(masked_tmpl)
                    if nonzero_tmpl == 0:
                        print(f"  WARNING: '{tmpl_name}' template has 0 pixels after mask — "
                              "template color doesn't match mask colors. Box detection won't work.")
                        continue
                    result = cv2.matchTemplate(masked_sc, masked_tmpl, cv2.TM_CCOEFF_NORMED)
                    _, best_val, _, best_loc = cv2.minMaxLoc(result)
                    h, w = masked_tmpl.shape[:2]
                    cx, cy = best_loc[0] + w // 2, best_loc[1] + h // 2
                    matched = best_val >= threshold
                    results.append((tmpl_name, best_val, (cx, cy), matched))
                    status = "MATCH" if matched else "miss"
                    print(f"  {tmpl_name}: score={best_val:.4f} at center=({cx},{cy})  [{status}]  "
                          f"(template pixels after mask: {nonzero_tmpl})")

                if results:
                    annotated = last_bgr.copy()
                    for tmpl_name, val, (cx, cy), matched in results:
                        color = (0, 0, 255) if matched else (0, 255, 255)
                        cv2.circle(annotated, (cx, cy), radius=sc.annotation_radius, color=color, thickness=3)
                        cv2.putText(annotated, f"{tmpl_name}:{val:.2f}", (cx + 8, cy - 8),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
                    save_image(annotated, ANNOTATED_PATH)
                    print("  Annotated screenshot saved — run 'show_annot' to view.")

        # ── diag ─────────────────────────────────────────────────────────────
        elif cmd == "diag":
            if last_bgr is None:
                print("  Capturing screenshot first...")
                last_bgr = capture_screenshot(device)
                save_image(last_bgr, CAPTURED_PATH)
                print(f"  Size: {last_bgr.shape[1]}x{last_bgr.shape[0]}")

            key_list = parts[1:] if len(parts) > 1 else sorted(templates.keys())
            hsv_sc = cv2.cvtColor(last_bgr, cv2.COLOR_BGR2HSV)
            gray_sc = cv2.cvtColor(last_bgr, cv2.COLOR_BGR2GRAY)

            rows = []
            for name in key_list:
                if name not in templates:
                    print(f"  Template '{name}' not found — skipped.")
                    continue
                # HSV score
                hsv_result = cv2.matchTemplate(hsv_sc, templates[name]["bgr2hsv"], cv2.TM_CCOEFF_NORMED)
                _, hsv_val, _, hsv_loc = cv2.minMaxLoc(hsv_result)
                # grayscale score
                gray_result = cv2.matchTemplate(gray_sc, templates[name]["grayscale"], cv2.TM_CCOEFF_NORMED)
                _, gray_val, _, gray_loc = cv2.minMaxLoc(gray_result)
                rows.append((name, hsv_val, hsv_loc, gray_val, gray_loc, templates[name]["bgr2hsv"].shape))

            rows.sort(key=lambda r: max(r[1], r[3]), reverse=True)

            print(f"\n  {'TEMPLATE':<35} {'HSV':>6}  {'GRAY':>6}  STATUS")
            print(f"  {'-'*35} {'-'*6}  {'-'*6}  ------")
            annotated = last_bgr.copy()
            for name, hsv_val, hsv_loc, gray_val, gray_loc, shape in rows:
                best_val = max(hsv_val, gray_val)
                best_loc = hsv_loc if hsv_val >= gray_val else gray_loc
                h_t, w_t = shape[:2]
                cx, cy = best_loc[0] + w_t // 2, best_loc[1] + h_t // 2
                if best_val >= 0.8:
                    status = "✓ match"
                    dot_color = (0, 0, 255)      # red
                elif best_val >= 0.6:
                    status = "~ close"
                    dot_color = (0, 165, 255)    # orange
                else:
                    status = "✗ miss"
                    dot_color = (0, 255, 255)    # yellow
                print(f"  {name:<35} {hsv_val:>6.3f}  {gray_val:>6.3f}  {status}")
                cv2.circle(annotated, (cx, cy), radius=sc.annotation_radius, color=dot_color, thickness=2)
                cv2.putText(annotated, f"{best_val:.2f}", (cx + 8, cy - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, dot_color, 1)

            save_image(annotated, ANNOTATED_PATH)
            print(f"\n  Annotated screenshot saved — run 'show_annot' to view.")
            print(f"  RED=match(>=0.8)  ORANGE=close(>=0.6)  YELLOW=miss(<0.6)")

        # ── show last screenshot ──────────────────────────────────────────────
        elif cmd == "show":
            if last_bgr is None:
                print("  No screenshot yet.")
            else:
                open_image(CAPTURED_PATH)

        # ── show annotated screenshot ─────────────────────────────────────────
        elif cmd == "show_annot":
            if not os.path.exists(ANNOTATED_PATH):
                print("  No annotated screenshot yet. Run a match command first.")
            else:
                open_image(ANNOTATED_PATH)

        # ── list templates ────────────────────────────────────────────────────
        elif cmd == "list":
            if not templates:
                print("  No templates found.")
            else:
                print(f"  Templates in {TEMPLATES_DIR}/:")
                for name, data in sorted(templates.items()):
                    h, w = data["simple"].shape[:2]
                    print(f"    {name:<35} {w}x{h}px")

        # ── tap ───────────────────────────────────────────────────────────────
        elif cmd == "tap":
            if len(parts) < 3:
                print("  Usage: tap <x> <y>")
            else:
                try:
                    x, y = int(parts[1]), int(parts[2])
                    device.shell(f"input tap {x} {y}")
                    print(f"  Tapped ({x}, {y})")
                except ValueError:
                    print("  x and y must be integers.")

        # ── help / quit ───────────────────────────────────────────────────────
        elif cmd == "help":
            print_help()

        elif cmd in ("q", "quit", "exit"):
            print("Bye!")
            break

        else:
            print(f"  Unknown command '{cmd}'. Type 'help' for available commands.")


if __name__ == "__main__":
    main()

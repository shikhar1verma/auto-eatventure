# Station upgrade icon detection (red circle + white up arrow)

2026-10-14. Problem: the old `get_food_icon_locations()` (grayscale
template `buy_better_food_icon.png`, threshold 0.8, DBSCAN; now
`stations.find_icons()` with the detector below) misses icons while
they pulse (size changes) and finds them on a screen dimmed by a
dialog (grayscale correlation ignores brightness) - with the "Restaurant
Race ended!" dialog the bot kept tapping a dimmed icon, so the stale
recovery never ran.

Data: all 274 saved screenshots of both phones (`experiments/**`) plus
`xiaomi_seq/`, `xiaomi_seq2/`, `oneplus_seq/` (frames while the bots
ran, ~0.5-1 s apart).

Icon colors: red disk BGR (76, 84, 255) = HSV (1, 179, 255), arrow
pure white. Under a dialog the red has V ~116-142.

## Detection (`find_upgrade_icons()` in `src/auto_eatventure/vision/upgrade_icons.py`)

1. White mask (S <= 70, V >= 225; the pink glow of "Double" labels
   tints the arrow), connected components.
2. Arrow-shaped component: height 22-48 ref px, w/h 0.7-1.3, fill
   0.4-0.75, top corners empty (<= 0.3; X buttons ~0.85), bottom
   middle filled (>= 0.3), center filled (>= 0.5; letter "o" 0).
3. Red disk around it: of 9 points on the upper half circle (r = 0.8
   arrow height) >= 4 are icon red (H 0-3, S 150-210, V >= 235). Only
   the upper half: labels below the icons and the side panel cover
   part of the ring.

## Results vs the old detector

- 274 frames: old 339 icons, new 444 icons.
- Old-only: 25, all false (dimmed icons under a dialog, text "Pirates").
- New-only: 130, all checked by eye - real icons (pulsing, tilted,
  under "Double" labels / coin text).
- No false positive found (red X buttons, "!" badges, "Stop" button,
  red hair, red cups rejected).
- CPU: 28 ms/frame vs 120 ms/frame (no matchTemplate, no DBSCAN).
- Per-frame counts (Xiaomi seq): old 000000012103001102021021111110,
  new 000000034444000444433343334333.

# Template Matching

> <- Back to [AGENTS.md](../../AGENTS.md)

## Overview

The project uses **OpenCV template matching** (`cv2.matchTemplate` with `TM_CCOEFF_NORMED`; `TM_SQDIFF_NORMED` for the Food Delivery truck and the helper button, see strategy 2) to detect game UI elements in screenshots. No OCR is used. The detection lives in `vision/` (`src/auto_eatventure/vision/`; module paths below are relative to `src/auto_eatventure/`):

- `vision/templates.py` -- catalog `TEMPLATE_NAMES`, loading and resizing
- `vision/matching.py` -- `best_match()`, `closest_match()`, `all_matches()` (DBSCAN)
- `vision/screen.py` -- `Screen`: the last screenshot and the searches the actions use (`game.screen`)
- `vision/colors.py` -- HSV color ranges (`RED`) and `color_ratio()`
- `vision/upgrade_icons.py` -- station upgrade icons by shape and color

All `Screen` searches take the template name and an optional `Region` to search in (the whole screen by default) and return positions in screen pixels.

## Matching Strategies

### 1. HSV Matching (Default)

`Screen.find(name, region, threshold=0.8)` / `Screen.has(...)`:

- `TM_CCOEFF_NORMED` (`matching.best_match()`) of the HSV template on the HSV screenshot
- `find()` returns the matched `Region` (score above the threshold) or `None`
- More robust to lighting variations in the game
- Used for most UI elements

### 2. Brightness-Sensitive Matching (SQDIFF)

`Screen.find_exact(name, region, max_difference=0.02)`:

- `TM_SQDIFF_NORMED` (`matching.closest_match()`) on raw BGR, match when the difference is below `max_difference` (0 = identical)
- `TM_CCOEFF_NORMED` ignores brightness, so it can't tell a black icon
  from the same icon greyed out; SQDIFF can
- Used for the Food Delivery truck (available = black, cooldown /
  unavailable = grey) and the helper button (available = black
  person with an empty line under it; max difference 0.015, since the
  black person with only an ad icon under it scores ~0.03)

### 3. Multi-Match (BGR + DBSCAN)

`Screen.find_all(name, threshold=0.8)`:

- `TM_CCOEFF_NORMED` on raw BGR over the whole screen
- Returns the centers (`Point`s) of all matching objects
- Used for box detection (`actions/boxes.py`)

## Multi-Match Detection with DBSCAN

`matching.all_matches()` in `vision/matching.py`:

1. Finds **all** locations above threshold
2. Calculates center point for each match
3. Clusters with DBSCAN (`eps=CLUSTER_MAX_DISTANCE` = 10, `min_samples=CLUSTER_MIN_MATCHES` = 5)
4. Returns cluster centroids as final positions

## Template Catalog

All templates are in `matching_screenshots/` and listed (file name without `.png`) in `TEMPLATE_NAMES` in `vision/templates.py`:

| Template | Used by | Strategy | Threshold |
|----------|---------|----------|-----------|
| `open_button.png` | `levels.is_open_button_shown()` (first stand after renovate / fly) | HSV | 0.9 |
| `welcome_city_okay.png` | `levels.is_welcome_okay_shown()` ("Welcome to <city>" after fly) | HSV | 0.9 |
| `settings.png` | `start_dialogs.wait_until_ready()`, `adventures.collect()` (main screen) | HSV | 0.8 |
| `offline_earnings.png` | `start_dialogs.wait_until_ready()` | HSV | 0.8 |
| `race_ended_title.png`, `race_claim.png` | `race_reward.claim()` ("Restaurant Race ended!"; Claim searched only below the title) | HSV | 0.8 |
| `box.png`, `box2.png` | `boxes.open_all()` | BGR multi | 0.7 |
| `go_next_level_icon.png` | `levels.go_to_next_level()` | HSV | 0.95 |
| `fly_next_city_icon.png` | `levels.go_to_next_level()` | HSV | 0.95 |
| `chest_icon.png` | `chests.open_all()` | HSV | 0.8 |
| `popup_close_cross.png` | `popups.close_popup()` | HSV | 0.8 |
| `popular_dish_select.png`, `popular_dish_start.png`, `popular_dish_stop.png` | `popular_dish._button_state()` (region around the Popular Dish button) | HSV | 0.9 |
| `food_delivery_available.png` | `food_delivery.find_truck()` (left button column) | BGR SQDIFF | < 0.02 |
| `food_delivery_accept.png` | `food_delivery._is_accept_shown()` (region around the first order's Accept) | HSV | 0.9 |
| `helper_available.png` | `helper_invite.is_available()` (region around the helper button) | BGR SQDIFF | < 0.015 |
| `helper_invite.png` | `helper_invite._is_invite_shown()` (region around the first helper's Invite) | HSV | 0.8 |
| `adventure_zeus_key.png`, `adventure_pirates_key.png` | `adventures._find_enter_button()` (key icon of an adventure in the "Events" list) | HSV | 0.8 |
| `adventure_zeus_dialog_key.png`, `adventure_pirates_dialog_key.png` | `adventures._has_key()` (counter of the level dialog; the other key / an ad icon there scores <= 0.46) | HSV | 0.8 |

Not template-matched (pulsing / plain color, so the share of
pixels in an HSV range is measured with `Screen.color_ratio()`):

| Element | Detection | Color | Min ratio |
|---------|-----------|-------|-----------|
| Red badge on the upgrade button | `upgrades._has_badge()` | red | 0.12 |
| Red X (close) of the Upgrades dialog | `upgrades._is_dialog_open()` | red | 0.4 |
| First row's buy button in the Upgrades dialog | `upgrades._is_first_affordable()` | blue (grey = too expensive) | 0.3 |
| Red X of the "Events" dialog / an adventure's level dialog / the reward summary | `adventures._is_events_dialog_open()`, `_is_level_dialog_open()`, `_is_summary()` | red | 0.5 |
| Right arrow of an adventure's level dialog (last level not selected) | `adventures._has_right_arrow()` | blue | 0.2 |
| Background of the adventure reward screen | `adventures._is_reward_screen()` | dark blue (Zeus) or brown (Pirates) | 0.8 |

The dimmed screen check (`popups.is_screen_dimmed()`) uses the
maximum brightness of the grayscale settings gear instead.

## Station Upgrade Icons (shape + color, no template)

`find_upgrade_icons()` in `vision/upgrade_icons.py`, used by
`stations.find_icons()`. The icon (red circle, white up arrow)
pulses, so the old grayscale template (`buy_better_food_icon.png`)
missed it in many frames, and grayscale correlation also found it on a
screen dimmed by a dialog (the bot kept tapping it under "Restaurant
Race ended!"). Now:

1. White mask (S <= 70, V >= 225), connected components with an arrow
   height of `upgrade_arrow_min/max_height_y` (22-48 ref px).
2. Arrow shape of the bounding box: aspect 0.7-1.3, fill 0.4-0.75,
   empty top corners (an X has them full), filled stem and center
   (a letter "o" has an empty center).
3. Red circle: of 9 points on the upper half circle (radius 0.8 x arrow
   height) at least 4 are icon red (H 0-3, S 150-210, V >= 235). Only
   the upper half, as labels below the icon cover the rest; a dimmed
   red (V ~120) doesn't count, so dimmed icons are not found.

On the 274 saved screenshots of both phones (after the
`station_icon_max_y` and club button filters): 444 icons found vs 339
with the template (130 more real ones, 25 false ones of the template
dropped), ~30 ms per frame vs ~120 ms. The red badge of the bottom
Upgrades button looks like a station icon too; `station_icon_max_y`
keeps it out. Data: `experiments/upgrade_icons/NOTES.md`.

## Template Scaling

Templates are resized at load time in `vision/templates.py` (`load_templates()` -> `_resize()`):

```python
target_width = max(1, round(width * x_scale))
target_height = max(1, round(height * y_scale))
```

- Scale factors = `actual_resolution / reference_resolution` (1220x2712)
- Uses `INTER_AREA` when shrinking, `INTER_LINEAR` when enlarging
- Can be overridden with `TEMPLATE_SCALE_OVERRIDE` env var (`_template_scale()` in `main.py`)

## Debug Mode

Set `DEBUG_TEMPLATE_MATCHING="1"` in `.env` to log the score of every `find()` / `find_exact()` check (`Template <name>: score <value>`, DEBUG level, so in `autoplay.log`; on the console only with `LOG_LEVEL="DEBUG"`). Very noisy -- only use when tuning thresholds.

## Adding a New Template

1. Capture screenshot with the element visible (`PYTHONPATH=src python -m auto_eatventure.sandbox`)
2. Crop the element tightly as PNG, save to `matching_screenshots/`
3. Add its file name (without `.png`) to `TEMPLATE_NAMES` in `vision/templates.py`
4. Search it in an `actions/` module with `game.screen.find()` / `has()` (or `find_exact()` / `find_all()`), ideally in a `Region` from `coords/reference.py`
5. Wire the action into `GameLoop.play_once()` in `game_loop.py`

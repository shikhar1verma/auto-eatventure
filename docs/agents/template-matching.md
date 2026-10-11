# Template Matching

> <- Back to [AGENTS.md](../../AGENTS.md)

## Overview

The project uses **OpenCV template matching** (`cv2.matchTemplate` with `TM_CCOEFF_NORMED`; `TM_SQDIFF_NORMED` for the Food Delivery truck and the helper button, see strategy 5) to detect game UI elements in screenshots. No OCR is used. All matching logic lives in `template_matcher.py` (`TemplateMatcher` class).

## Matching Strategies

### 1. HSV Matching (Default)

`TemplateMatcher.match_hsv()` / `is_hsv_match()`:

```python
hsv_template = self.templates[key]['bgr2hsv']
result = self.find_template(screenshot_hsv, hsv_template, threshold)
```

- Converts both screenshot and template to HSV color space
- More robust to lighting variations in the game
- Used for most UI elements

### 2. Grayscale Matching

`TemplateMatcher.match_grayscale()` / `is_grayscale_match()`:

- Used for small investor icon, ad cross buttons
- Less affected by color shifts

### 3. Color-Masked Matching

Uses `apply_investor_mask()` or `apply_box_mask()` to isolate specific HSV color ranges before matching:

- Investor: isolates gold/khaki tones
- Box: isolates brown/gold tones
- Lower threshold needed (0.65) due to reduced information after masking

### 4. Raw BGR Matching

Direct matching without color space conversion:

- Used by `find_all_templates()` for box detection
- Fallback when masked matching fails on different devices

### 5. Brightness-Sensitive Matching (SQDIFF)

`TemplateMatcher.match_bgr_sqdiff()`:

- `TM_SQDIFF_NORMED` on raw BGR, match when the diff is below
  `max_diff` (default 0.02; 0 = identical)
- `TM_CCOEFF_NORMED` ignores brightness, so it can't tell a black icon
  from the same icon greyed out; SQDIFF can
- Used for the Food Delivery truck (available = black, cooldown /
  unavailable = grey) and the helper button (available = black
  person with an empty line under it; max diff 0.015, since the
  black person with only an ad icon under it scores ~0.03)

## Multi-Match Detection with DBSCAN

`TemplateMatcher.find_all_templates()` at `template_matcher.py`:

1. Finds **all** locations above threshold
2. Calculates center point for each match
3. Clusters with DBSCAN (`eps=10`, `min_samples=5`)
4. Returns cluster centroids as final positions

## Template Catalog

All templates are in `matching_screenshots/` and registered in `TemplateMatcher.__init__()`:

| Template | Detection Method (in `game_actions.py`) | Strategy | Threshold |
|----------|----------------------------------------|----------|-----------|
| `notification.png` | `is_having_notification()` | HSV | 0.8 |
| `open_button.png` | `is_having_open_button()` (first stand after renovate / fly) | HSV | 0.9 |
| `welcome_city_okay.png` | `is_having_welcome_city_okay()` ("Welcome to <city>" after fly) | HSV | 0.9 |
| `settings.png` | `is_having_settings()` | HSV | 0.8 |
| `offline_earnings.png` | `is_having_offline_earnings()` | HSV | 0.8 |
| `upgrade_button.png` | `is_having_upgrade()` | HSV | 0.97 |
| `buy_better_food_icon.png` | `get_food_icon_locations()` | Grayscale multi | 0.8 |
| `buy_better_food_button.png` | (available) | HSV | 0.8 |
| `box.png`, `box2.png` | `open_boxes()` | BGR multi | 0.7 |
| `go_next_level_icon.png` | `is_having_next_level_icon()` | HSV | 0.95 |
| `fly_next_city_icon.png` | `is_having_fly_next_city_icon()` | HSV | 0.95 |
| `small_investor_icon.png` | `is_having_small_investor_icon()` | Grayscale | 0.8 |
| `investor.png` | `is_having_investor()` | Color-masked | 0.65 |
| `chest_icon.png` | `is_having_chest_icon()` | HSV | 0.8 |
| `popup_close_cross.png` | `close_accidental_popups()` | HSV | 0.8 |
| `popular_dish_select.png`, `popular_dish_start.png`, `popular_dish_stop.png` | `get_popular_dish_button_state()` (ROI around the Popular Dish button) | HSV | 0.9 |
| `food_delivery_available.png` | `get_food_delivery_truck_coords()` (left button column) | BGR SQDIFF | < 0.02 |
| `food_delivery_accept.png` | `is_having_food_delivery_accept()` (ROI around the first order's Accept) | HSV | 0.9 |
| `helper_available.png` | `is_having_helper_available()` (ROI around the helper button) | BGR SQDIFF | < 0.015 |
| `helper_invite.png` | `is_having_helper_invite()` (ROI around the first helper's Invite) | HSV | 0.8 |
| `no_boost_indicator_2x.png` | (available) | HSV | 0.92 |
| `ads_crosses/cross1.png` | (available) | Grayscale | 0.8 |

## Template Scaling

Templates are resized at load time in `TemplateMatcher._resize_template()`:

```python
target_w = max(1, round(w * self.template_x_scale))
target_h = max(1, round(h * self.template_y_scale))
```

- Scale factors = `actual_resolution / reference_resolution` (1220x2712)
- Uses `INTER_AREA` when shrinking, `INTER_LINEAR` when enlarging
- Can be overridden with `TEMPLATE_SCALE_OVERRIDE` env var

## Debug Mode

Set `DEBUG_TEMPLATE_MATCHING="1"` in `.env` to print raw `cv2.minMaxLoc` values for every template check. Very noisy -- only use when tuning thresholds.

## Adding a New Template

1. Capture screenshot with the element visible
2. Crop the element tightly as PNG, save to `matching_screenshots/`
3. Add path to `self.matching_screenshots_path` dict in `TemplateMatcher.__init__()`
4. Add detection method in `GameActions` (call `self.matcher.match_hsv()` or similar)
5. Integrate into game loop in `adb_autoplay.py`

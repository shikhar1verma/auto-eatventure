# Game Loop

> <- Back to [AGENTS.md](../../AGENTS.md)

## Overview

The main game loop lives in `AutoEatventure.start_playing_game()` at `adb_autoplay.py:44`. It runs **indefinitely**, calling high-level methods from `GameActions`. The loop itself is ~40 lines of pure orchestration.

## Loop Structure

```python
while True:
    count += 1
    swipe_count = actions.handle_stale_state(...)
    device.capture_screenshot()
    actions.close_accidental_popups()       # every 150 iterations
    actions.try_upgrade_items(count, ...)   # every 5th iteration
    actions.open_boxes()                    # every 2nd iteration
    food_icons = actions.get_food_icon_locations()
    # reposition after new level (once)
    # adjust layout if icons too high
    # upgrade food items or check next level
```

## Periodic Actions

| Condition | Action | Method |
|-----------|--------|--------|
| Every iteration | Capture screenshot | `device.capture_screenshot()` |
| `count % 2 == 0` | Find and open boxes | `actions.open_boxes()` |
| `count % 5 == 0` | Open upgrade menu, click upgrades | `actions.try_upgrade_items()` |
| `count % 10 == 0` (no food) | Check next level / city | `actions.check_to_go_next_level()` |
| `count % 150 == 0` | Close accidental popups | `actions.close_accidental_popups()` |

## Stale State Recovery

Handled by `GameActions.handle_stale_state()` in `game_actions.py`:

- **`nothing_to_update_count >= 15`** (every 5th after): Swipe pattern to reveal hidden elements
- **`nothing_to_update_count > 50`**: Force-restart the app

Swipe pattern cycles through 5 down-swipes then 5 up-swipes
(`SWIPES_PER_DIRECTION = 5`), each 650px at reference resolution —
chosen so the total distance per direction still spans a tall level
before reversing.

## Level Transition Flow

`GameActions.check_to_go_next_level()` in `game_actions.py`:

### Same-city level (renovate):
1. Detect `go_next_level_icon` template (threshold 0.95)
2. Click next level button -> renovate -> first lemonade stand
3. Open all chests (recursive)

### New city (fly):
1. Detect `fly_next_city_icon` template (threshold 0.95)
2. Click next level -> fly -> welcome OK -> first stand
3. Open all chests (recursive)

### After transition:
Reset all loop state: `swipe_count=0`, `nothing_to_update_count=0`, `new_level_started=True`, `new_level_first_food_icon_swipe=False`

## Food Upgrade Logic

`GameActions.upgrade_food_items()` in `game_actions.py`:

For each food icon (max 3 per iteration):
1. Click the food icon (with Y offset)
2. Click-and-hold above (3000ms) to trigger "buy better food" menu
3. Dismiss (null zone or offset depending on Y boundary)

## Layout Adjustment Methods

| Method | Purpose | Trigger |
|--------|---------|---------|
| `reposition_after_new_level()` | Swipe first food icon to correct position | Once after new level, when food icons first appear |
| `adjust_layout_if_icons_too_high()` | Swipe up if icon near top edge | Every iteration with food icons above `food_icon_top_boundary_y` |

## Popup Closing

`GameActions.close_accidental_popups()` in `game_actions.py`:
- Uses `popup_close_cross` template (red X button)
- Clicks center of detected button
- Re-captures screenshot after closing

## Disabled Features

Currently not called in the game loop (methods exist in `game_actions.py`):

- `redeem_investor()` -- find and claim investor reward
- `run_full_boost_ads()` -- watch 12 ads for full boost
- `run_ad()` -- watch single ad

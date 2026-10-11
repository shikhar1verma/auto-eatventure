# Game Loop

> <- Back to [AGENTS.md](../../AGENTS.md)

## Overview

The main game loop lives in `AutoEatventure.start_playing_game()` at `adb_autoplay.py:44`. It runs **indefinitely**, calling high-level methods from `GameActions`. The loop itself is ~40 lines of pure orchestration.

## Loop Structure

```python
while True:
    count += 1
    swipe_count = actions.handle_stale_state(...)
    actions.select_popular_dish()           # when popular_dish_next_try passed
    device.capture_screenshot()
    actions.accept_food_delivery(...)       # truck available -> continue
    actions.invite_helper()                 # helper available -> continue
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
| `FOOD_DELIVERY_ENABLED` and truck available | Accept the first Food Delivery order | `actions.accept_food_delivery()` |
| `HELPER_INVITE_ENABLED` and helper available | Invite the first helper | `actions.invite_helper()` |
| `POPULAR_DISH_ENABLED` and `popular_dish_next_try` passed | Select first dish as Popular Dish, Start + Stop at once | `actions.select_popular_dish()` |

### Popular Dish (Masterchef quest farming, optional)

Disabled by default; enable with `POPULAR_DISH_ENABLED="1"` in `.env`.
It is only useful for the Masterchef quest that counts Popular Dish
selections - the skill effect is not used, so the bot selects the
first dish, starts the skill and stops it right away. Flow: skill
circle (top center) -> Active Skills -> Select -> first dish tile ->
Start -> Stop -> close dialogs with `close_accidental_popups()`.
Every tap is verified by the Select/Start/Stop templates.

- Success: next try after `POPULAR_DISH_COOLDOWN_S` (10.5 min cooldown)
- Failure (cooldown, no stand open yet): retry after
  `POPULAR_DISH_RETRY_S` (60 s)
- Renovation / new city resets the game cooldown, but no dish can be
  selected before the first stand is open, so the next try waits for
  the first food upgrade (`popular_dish_wait_for_upgrade`)
- The dish grid is centered with max 3 tiles per row, so the first
  tile's x depends on the dish count; all positions are tried in order

### Food Delivery (quest farming, optional)

Disabled by default; enable with `FOOD_DELIVERY_ENABLED="1"` in `.env`.
The screenshot of every loop iteration is checked (~15 ms) for an
available delivery truck button in the left button column
(`get_food_delivery_truck_coords()`). If found,
`accept_food_delivery()` taps it, verifies the "Food Delivery" dialog
by the first order's Accept button and taps Accept. The dialog closes
by itself and the delivery completes without any further tap. The
iteration then ends (`continue`), so its other steps are skipped.

- Truck states: available (black, nothing under it), running (black +
  green "N/M"), cooldown (grey + "Xm Ys", ~3 min), unavailable (grey)
- The button moves up when the button above it is missing, so it is
  searched in an area and tapped where it was found
- After any attempt the checks pause for `FOOD_DELIVERY_PAUSE_S`
  (60 s), so a failure can't loop; a delivery and its cooldown take
  longer anyway
- Failure (dialog not open / still open): it is closed with
  `close_accidental_popups()`
- Success is logged only to `autoplay.log` (too frequent for
  `key_events.log`)

### Invite a helper (on by default)

Enabled by default; disable with `HELPER_INVITE_ENABLED="0"` in `.env`.
Works like Food Delivery: the loop screenshot is checked for an
available helper (person) button, the top button of the left column
(`is_having_helper_available()`). If found, `invite_helper()` taps it,
waits up to `HELPER_DIALOG_TIMEOUT_S` (10 s) for the list of the
"Invite a helper" dialog ("Loading..." first) and taps the first
helper's Invite. The dialog closes by itself.

- Button states: available (black person, nothing under it), working
  (black + green countdown, ~4 min), ad offer (black + blue ad icon,
  ~30 s, never tapped), cooldown (grey + "29m 59s", ~30 min)
- The "!" badge in the button corner pulses and is outside the
  template; the template covers the line under the person, which
  tells the states apart
- Availability is confirmed on a second screenshot 1 s later, so a
  frame caught between two states can't tap the ad offer
- After a success the checks pause for `HELPER_INVITE_PAUSE_S`
  (60 s), after a failure for `HELPER_INVITE_RETRY_S` (10 min; a
  list that doesn't load costs ~15 s); failures close the dialog with
  `close_accidental_popups()`
- Success is logged only to `autoplay.log`

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
2. Click next level button -> renovate -> wait for the first stand's
   "Open" button and tap it
3. Open all chests (recursive)

### New city (fly):
1. Detect `fly_next_city_icon` template (threshold 0.95)
2. Click next level -> fly -> welcome OK (fixed 19 s wait) -> wait for
   the first stand's "Open" button and tap it
3. Open all chests (recursive)

### Waiting for the "Open" button:
`_wait_and_click_open_button()` polls the `open_button` template every
second, up to `OPEN_BUTTON_TIMEOUT_S` (45 s), so slow renovate / fly
animations no longer leave the dialog open. If the button never shows
up (e.g. it was tapped by hand), its position is tapped anyway, a
WARNING goes to both `autoplay.log` and `key_events.log` and the bot
continues.

### After transition:
Reset all loop state: `swipe_count=0`, `nothing_to_update_count=0`, `new_level_started=True`, `new_level_first_food_icon_swipe=False`, `popular_dish_wait_for_upgrade=True`

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

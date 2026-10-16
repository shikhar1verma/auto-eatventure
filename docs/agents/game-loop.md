# Game Loop

> <- Back to [AGENTS.md](../../AGENTS.md)

## Overview

The main game loop lives in `AutoEatventure.start_playing_game()` at `adb_autoplay.py:44`. It runs **indefinitely**, calling high-level methods from `GameActions`. The loop itself is ~40 lines of pure orchestration.

## Startup (`init_game`)

Before the loop, `GameActions.init_game()` polls every 5 s until the
settings icon is visible or the offline earnings dialog is closed.
If the bot is restarted while a dialog covers the screen, it taps the
known ones and keeps waiting: the "Welcome to <city>" "Okay" button
(after a flight) and the first stand's "Open" button (after a
renovation), via the same helpers as the level transition.
"Restaurant Race ended!" (no X) gets its Claim tapped
(`claim_race_reward()`, gems, no ad; only when the Claim button is
bright, i.e. not covered by another dialog). Any other dialog with a
red X is closed by it (`close_accidental_popups()`),
e.g. "While you were away..." (helper invite gems, its Claim buttons
are never tapped) or Offline Earnings on phones where its template
doesn't match (its "Collect x2" plays an ad and is never tapped).
Every wait logs `Init: waiting for game to be ready`, so an unknown
dialog shows up in the log instead of a silent hang.

These start dialogs come when the server answers, up to ~30 s after
the game is ready, and not on every start. The bot doesn't wait for
them: during the first `START_DIALOGS_WATCH_S` (60 s) of the game
loop, every `START_DIALOGS_CHECK_S` (15 s) the loop screenshot is
checked (`close_late_start_dialogs()`), and a dialog that dims it is
closed like in step 1 of the null spot below. Screenshots:
`experiments/start_dialogs/NOTES.md`.

## Null spot (ad protection)

`null_click_coords` is the spot tapped to close station popups. It
must be on the restaurant (the top bar catches taps there, so the
popup stays open) but must not hit a customer bubble: on Xiaomi the
spot at y=340 (301 there) hit the investor's bubble, its "Investor"
dialog opened and its blue **Claim** button (~(540, 1548), where the bot taps
stations) started an ad the bot could not leave for hours.

The spot can't be derived from the resolution, the status bar height
differs between phones. The top bar ends with a black line across
the screen (Xiaomi 1080x2400: y=226, OnePlus Nord 3 1240x2772:
y=284), so `GameActions.place_null_click_below_top_bar()` finds it
once at start, right after `init_game()`:

1. **Close dialogs.** On a dimmed screen the line comes out wrong, so
   a fresh screenshot is checked first: a dialog dims the white
   settings gear (max brightness < `SETTINGS_GEAR_MIN_BRIGHTNESS`,
   200, around `settings_x/y`; station popups don't dim it). A dimming
   dialog is closed by its "Okay" (Welcome to <city>), "Open" (first
   stand) or red X, else by a tap outside it on the fallback spot
   (Back doesn't close dialogs). Then 1 s wait and a new check, at
   most `DIMMING_DIALOG_CLOSE_TRIES` (5) times.
2. **Find the line.** Rows with over 90 % black pixels (every channel
   < 10) in the band 6-15 % of the screen height (ads and loading
   screens have black rows higher up). The line is the **end of the
   first run** of black rows, so a black row lower in the restaurant
   (e.g. a night city) can't move the spot down; a run reaching the
   band bottom is no line. Runs shorter than
   `TOP_BAR_LINE_MIN_ROWS_Y` (5 reference px) are gaps between HUD
   elements and are skipped (the Xiaomi line has 13 rows).
3. **Place the spot** `NULL_CLICK_BELOW_TOP_BAR_Y` (22 reference px)
   below the line: still on the restaurant, above the tables. Xiaomi:
   y=245, OnePlus: y=306. x stays from `coords.py`. Logged as
   `Null spot below the top bar (y=226): (784, 245)`.
4. **Fallback.** If the screen stays dimmed or no line is found, the
   spot stays at `null_click_x/y` from `coords.py` (y=278) and an
   ERROR goes to `autoplay.log` and `key_events.log` with the reason,
   the risk and the fix (check a screenshot of the phone, adjust
   `place_null_click_below_top_bar()`).

Nothing of this runs in the game loop.

## Loop Structure

```python
while True:
    count += 1
    nothing_to_update_count, swipe_count = actions.handle_stale_state(...)
    actions.select_popular_dish()           # when popular_dish_next_try passed
    actions.collect_adventure_rewards()     # after start, every 5 h
    device.capture_screenshot()
    actions.close_late_start_dialogs()      # first 60 s, every 15 s
    actions.accept_food_delivery(...)       # truck available -> continue
    actions.invite_helper()                 # helper available -> continue
    actions.close_accidental_popups()       # every 150 iterations
    actions.try_upgrade_items()             # upgrade badge shown
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
| Upgrade button shows its red badge | Open upgrade menu, buy affordable upgrades | `actions.try_upgrade_items()` |
| `count % 10 == 0` (no food) | Check next level / city | `actions.check_to_go_next_level()` |
| `count % 150 == 0` | Close accidental popups | `actions.close_accidental_popups()` |
| First 60 s, every 15 s | Close late start dialogs (dimmed screen) | `actions.close_late_start_dialogs()` |
| `FOOD_DELIVERY_ENABLED` and truck available | Accept the first Food Delivery order | `actions.accept_food_delivery()` |
| `HELPER_INVITE_ENABLED` and helper available | Invite the first helper | `actions.invite_helper()` |
| `COLLECT_ADVENTURES_ENABLED` and `adventures_next_check` passed (first loop, then every 5 h) | Collect the free Adventures rewards | `actions.collect_adventure_rewards()` |
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
  searched in an area and tapped at the found y
- Left column buttons (truck, helper) are tapped at
  `side_button_tap_x`, right of their center: on some phones
  (OnePlus Nord 3) the column is partly hidden behind the screen edge
  and taps on the buttons' left part are ignored
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

### Collect Adventures (on by default)

Enabled by default; disable with `COLLECT_ADVENTURES_ENABLED="0"` in
`.env`. Adventures (Zeus' Feast, Hangry Pirates) give rewards for
"Complete last level" (repeats the last completed level) while the
adventure has keys; keys refill about once a day. Checked in the
first loop after the start, then every `COLLECT_ADVENTURES_INTERVAL_S`
(5 h); a check that hit an unexpected screen is retried after
`COLLECT_ADVENTURES_RETRY_S` (1 h). Flow of
`collect_adventure_rewards()`:

1. Tap the party popper (first white button on the right) and verify
   the "Events" dialog by its red X.
2. Swipe the dialog to its bottom: the Events section on top varies,
   the Adventures are always last.
3. For each adventure search its key icon in the list (Zeus silver,
   Pirates brown). An ad icon instead means no free run: the
   adventure is skipped. The Enter button is tapped at a fixed offset
   from the found key, so the varying list doesn't matter.
4. In the level dialog (verified by its red X) tap the right arrow
   while it is shown, so the last level is selected.
5. Only while the counter above the buttons shows the key icon: tap
   "Complete last level". The ad icon (keys used up) is never tapped,
   it would play an ad for the run.
6. Reward cards: tap the screen center until the summary shows its
   red X (one card per tap, 1 to ~10 cards); one more tap closes the
   summary. Every tap is preceded by a check of the reward screen's
   background (Zeus dark blue, Pirates brown), so a tap never lands
   on anything else.
7. Back to step 4 (a bonus "Key" card adds a run). Then close the
   level dialog and, at the end, the "Events" dialog with their X.

- Safety limits: 30 arrow taps, 15 reveal taps, 10 runs per adventure
- Every close tap and the popper tap first check that the expected
  screen is shown (main screen = settings gear visible)
- Failure (dialog / reward screen not found): a WARNING goes to
  `autoplay.log`; reward cards still shown are tapped through (each
  tap after a check of the reward screen), then the open dialogs are
  closed with `close_accidental_popups()`. Runs collected before the
  failure still go to `key_events.log`.
- Collected rewards go to `key_events.log`
  (`ADVENTURES - Collected rewards: Zeus' Feast 2x, Hangry Pirates 1x`);
  a check with nothing to collect only to `autoplay.log`
- Screenshots and measurements: `experiments/adventures/NOTES.md`

## Stale State Recovery

Handled by `GameActions.handle_stale_state()` in `game_actions.py`:

- **`nothing_to_update_count >= 15`** (every 5th after): Swipe pattern to reveal hidden elements
- **`nothing_to_update_count > 50`** (`STALE_RECOVERY_THRESHOLD`):
  bring the game to the foreground (`device.start_app()`), claim
  the "Restaurant Race ended!" reward if shown, close up
  to `STALE_POPUP_CLOSE_TRIES` (3) dialogs by their red X (a dialog
  may block the game) and tap the null click spot, then reset
  `nothing_to_update_count` to 0, so this repeats once per ~50 empty
  loops (~2-3 min), not on every loop. The
  game is **not** restarted: `start_app()` only brings a running game
  to the foreground (a real restart would need `close_app()` first).

Swipe pattern cycles through 7 down-swipes then 7 up-swipes
(`SWIPES_PER_DIRECTION = 7`), each 650px at reference resolution —
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
2. Click next level -> fly -> wait for the "Welcome to <city>" dialog's
   "Okay" button and tap it -> wait for the first stand's "Open"
   button and tap it
3. Open all chests (recursive)

### Waiting for the "Okay" / "Open" buttons:
`_wait_and_click_button()` polls the button's template every second,
up to `WELCOME_OKAY_TIMEOUT_S` (60 s; the flight animation takes
~15-19 s) for `welcome_city_okay` and `OPEN_BUTTON_TIMEOUT_S` (45 s)
for `open_button`, so slow renovate / fly animations no longer leave
a dialog open. If the button never shows up (e.g. it was tapped by
hand), its position is tapped anyway, a WARNING goes to both
`autoplay.log` and `key_events.log` and the bot continues.

### After transition:
Reset all loop state: `swipe_count=0`, `nothing_to_update_count=0`, `new_level_first_food_icon_swipe=False`, `popular_dish_wait_for_upgrade=True`

## Upgrades (upgrade menu)

`GameActions.try_upgrade_items()` / `do_upgrades()` in
`game_actions.py`:

1. Every iteration that reaches the upgrade step (Food Delivery /
   helper invites end an iteration early) checks the loop screenshot
   for the red badge on the upgrade button (bottom right), shown
   while an upgrade can be bought. The badge pulses (size, tilt), so
   its red pixels are counted (`is_having_upgrade()`); template
   matching missed ~1/3 of the frames.
2. The null spot is tapped first: a station popup left open by the
   food upgrades stays open under the Upgrades dialog and, after it
   is closed, hides the station's food icon (the loop then finds
   nothing to upgrade). If the dialog does not open (red X not found,
   `is_having_upgrades_dialog()`), the null spot is tapped instead of
   the X, which would land on the restaurant.
3. The menu is opened (`UPGRADE_DIALOG_OPEN_DELAY_S`, 0.5 s) and,
   before every round, a screenshot checks the first row's buy button
   (`is_first_upgrade_affordable()`): blue = tap it
   `UPGRADE_CLICKS_PER_CHECK` (5) times, grey = too expensive, close
   the menu. A bought upgrade leaves the list and the next one moves
   to the first row. A dialog that did not open gets no taps. At most
   `UPGRADE_MAX_CLICKS` (50) taps (a new level has many cheap
   upgrades).
4. After closing, the bot waits `UPGRADE_DIALOG_CLOSE_DELAY_S`
   (0.8 s) for the dialog to fade out before the next screenshot;
   otherwise the food icons are hidden and the stations are skipped.

A usual visit takes ~5 s (2 checks + 5 taps + fade-out). Before, the
menu was opened only every 5th iteration (~1 min with several
stations, as each station takes ~4 s) and tapped blindly 10x
(~4.7 s; 50x after a new level).

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
- Called every 150 loops, in `init_game()` for start dialogs with a
  red X, in `_close_dimming_dialogs()` and in the stale recovery
  (`handle_stale_state()`, up to 3 popups)

## Disabled Features

Currently not called in the game loop (methods exist in `game_actions.py`):

- `redeem_investor()` -- find and claim investor reward
- `run_full_boost_ads()` -- watch 12 ads for full boost
- `run_ad()` -- watch single ad

# Popular Dish (Active Skills) – notes for automation

Captured 2026-10-08 on device 1080x2400 (reference in
src/auto_eatventure/coords/reference.py is 1220x2712, so convert:
ref = device * 1220/1080 ≈ * 1.1296).
All coordinates below are DEVICE pixels (1080x2400).

## Flow (manual, verified)

1. Main screen: small **black circle** top-center at ~(540, 288).
   - Screenshot: `00_main_no_stand.png`, `fav_07_now.png`
2. Tap circle -> dialog **"Active Skills"** (`fav_01_after_circle.png`):
   - Popular Dish row, button "Select" at ~(834, 1226), duration 3m
   - Sold Out row, button "Select" at ~(834, 1496), duration 2m
   - Red X close at ~(900, 924)
3. Tap Popular Dish "Select" -> dialog **"Select a dish"**
   (`fav_10_select_dish_active.png`):
   - Dish tiles in a row, first at ~(430, 1154), second at ~(650, 1154)
     (tile pitch ~220 px; more dishes likely add more tiles / rows)
   - Dish with NO open stand is greyed out (faded) – not selectable
     (`fav_02_after_select.png`: both grey right after city start)
   - Red X close at ~(806, 960) -> returns to Active Skills
4. Tap an active (colored) dish -> back to Active Skills
   (`fav_11_after_pick_waffle.png`):
   - Text changes to "Dish `Waffles` is more likely to be ordered"
   - Black circle in the row now shows the dish icon
   - Button changes from "Select" to **"Start"** (same position)
5. Tap "Start" (834, 1226) -> skill ACTIVE (`fav_12_after_start.png`):
   - Green countdown "2m 58s" + green "ACTIVE" badge
   - Button turns red **"Stop"** (same position) – do NOT tap again
6. Close with X (900, 924) -> main screen (`fav_13_main_skill_active.png`):
   - Top-center now shows TWO circles: green circle with dish icon
     ~(486, 288) = active Popular Dish, and black empty circle
     ~(594, 288) = still-free slot (Sold Out).
   - => The black circle MOVES when a skill is active. Detect it by
     template matching, not a fixed coordinate.

## GOAL (from user)

We do NOT care about the skill effect. There is an achievement for
selecting Popular Dish many times (~500x). So the bot should:
select FIRST dish -> Start -> immediately Stop -> close dialog.
Always pick the first (leftmost) colored dish tile.
Do it after every fly to a new city and whenever the cooldown is over.

## Stop + cooldown (verified 17:28)

7. While active, the top circle is GREEN with dish icon (~(486, 288)).
   Tapping it opens Active Skills (`fav_15_skills_while_active.png`).
8. Tap red "Stop" (834, 1226) -> Popular Dish row resets: no dish icon,
   text back to "Selected dish is more likely...", button turns GREY
   with countdown **"9m 58s"** (`fav_16_after_stop.png`).
   => After Stop the cooldown is ~10 min (not 3 min!).
   Confirmed by user: cooldown is the same whether stopped or expired
   naturally. Cooldown is RESET on every fly to a new city AND on every
   renovation (next level). So: try right after each renovation/fly,
   otherwise every ~10 min (or whenever the circle is black again).
9. Main screen during cooldown (`fav_17_main_cooldown.png`): left
   circle is GREY with a clock/pie hand (~(486, 288)), right circle
   black (Sold Out slot). Tapping the grey one presumably opens the
   same dialog with the grey countdown button.

## Dish grid layout (found while testing in the bot)

The "Select a dish" grid has max 3 tiles per row and is CENTERED.
With 3+ dishes the first tile is at ~(319, 1154)
(`fav_18_select_dish_3_columns.png`), with 2 dishes at ~(430, 1154),
1 dish presumably ~(540, 1154). The bot taps these x positions in
this order until the "Start" button appears (gap / grey tile taps do
nothing).

## Detection states of the top-left skill circle

- black empty  -> Popular Dish ready (Select)
- green + dish -> active (Stop)
- grey + clock -> cooldown, nothing to do
When no skill is used, only ONE black circle at (540, 288).

## Preconditions / gotchas

- Fresh city: no stand open -> dish list all grey -> nothing to do.
  Close both dialogs (inner X, then outer X).
- New stand after "Unlock" is a wooden crate (brown/yellow, slats,
  `fav_07_now.png` at ~(240, 1716)); it must be tapped once to open
  it before the dish becomes active (`fav_08_after_box.png`).
- Skill lasts 3 min; after it ends it can be started again (cooldown
  not yet observed – check).
- Which dish to pick: TBD with user (e.g. most expensive / newest
  stand = rightmost colored tile?).

## Template candidates to crop

- black empty skill circle (top center)
- "Active Skills" title / dialog
- blue "Select" button, blue "Start" button, red "Stop" + "ACTIVE"
- "Select a dish" title
- grey vs colored dish tile (to tell selectable)
- red X close button (maybe existing popup_close_cross.png works)

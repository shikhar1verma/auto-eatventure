# Adventures daily rewards (Zeus' Feast, Hungry Pirates)

Goal: collect Adventures rewards once a day. Device: Xiaomi e0cb42c1
(1080x2400). Coordinates below are device px unless noted.

## Flow so far (Zeus' Feast, verified by hand)

1. Main screen: tap the first white button on the right (party
   popper, ~1010, 380) -> "Events" dialog.
2. Always swipe down inside the dialog (540,1520)->(540,760); the
   Adventures section is always last, Events above it vary.
3. Tap the adventure's Enter -> level dialog ("Feast on Olympus").
4. Make sure the LAST level is selected: while the right blue arrow
   is visible (~795, 925), tap it. Last level = no right arrow /
   button text "Complete last level".
5. Check the counter icon above the buttons (~500, 1605):
   - key icon -> a free run is available, continue with step 6;
   - ad icon (clapperboard) -> stop, never tap (it plays an ad).
6. Tap "Complete last level" (~365, 1725) -> blue reward screen.
7. Tap the screen center (540, 1200) repeatedly (1.5 s apart). Each
   tap reveals one card. After the last card one more tap shows the
   summary with a red X top right (~990, 165) - that is the "all
   revealed" signal. Then one more center tap closes the summary
   (back to the level dialog).
8. Go to step 5 (bonus "Key x1" cards can add runs, so the number
   of runs is unknown in advance).

## Rules from the user

- Rewards can be collected only once a day (keys replenish).
- Never collect rewards for an ad (ad icon on the counter).
- Never tap ads or Claim (global rule).
- Adventures: Zeus' Feast and Hungry Pirates ("Hangry Pirates" in
  game).

## Open (not explored yet)

- Hangry Pirates - expected to be the same flow, not tried yet.
- DONE: closing back to the main screen = level dialog X (860, 650),
  then Events dialog X (935, 705) - see adv_16, adv_17.
- When/how often the bot should run this (once a day, at start?).

## Screenshots

- `adv_00_main.png` - main screen. White buttons on the right edge,
  top to bottom: party popper (~1010, 380), trophy (~1010, 570),
  Potion Shop cauldron with timer (~1010, 750), Merchant with timer
  (~1010, 940).
- `adv_01_after_first_button.png` - after tapping the party popper:
  "Events" dialog (red X at ~935, 705). Sections: Potion Shop (Enter),
  Merchant (Open), then "Adventures" with keys counter (0 now,
  "Keys replenish in 4h 30m"). Zeus' Feast card: keys 2/2, Enter
  button (~840, 1725). Next card (pirate flag, keys 2/2) is cut off
  below - probably Hungry Pirates; the dialog likely scrolls.
- `adv_02_scrolled_down.png` - after swipe (540,1520)->(540,760),
  600 ms. Dialog scrolled to the bottom (scrolled ~155 px only, list
  end). Zeus' Feast Enter (~840, 1570), "Hangry Pirates" (sic) keys
  2/2, Enter (~840, 1830). User: Events section varies (only when
  events run); Adventures are always last, so always scroll down
  before reading them.
- `adv_03_zeus_after_enter.png` - after Zeus' Feast Enter: dialog
  "Feast on Olympus" over the Events dialog. Red X (~860, 650), blue
  left arrow (~285, 925), Level 79, Rewards: ring x5, keys 2/2.
  Buttons: "Complete last level" (~365, 1725), "Enter" (~715, 1725).
  User: the last level must be selected. Last level = button text
  "Complete last level" OR only the LEFT arrow is shown (no right
  arrow at the mirrored position ~795, 925). Sometimes the last level
  is not selected (then a right arrow shows).
  User: if not on the last level, tap the right arrow until it is.
- `adv_04_zeus_previous_level.png` - after tapping the left arrow
  (285, 925): Level 78, both arrows visible (right arrow ~795, 925),
  button text just "Complete" (not "Complete last level"). Blue-pixel
  ratio in arrow ROIs (HSV h 95-115, s>120, v>150): left 0.46,
  right 0.46 (on level 79: right 0.00).
- `adv_05_zeus_back_to_last.png` - after tapping the right arrow
  (795, 925): back on Level 79, right arrow gone (blue ratio 0.00),
  button "Complete last level" again.
- `adv_06_zeus_after_complete.png` - after "Complete last level"
  (365, 1725): full-screen dark blue reward screen, "Zeus' Feast /
  Level 78 completed" (the last completed level, 79 is the next one),
  card stack with "5" (~520, 1735), text "Tap to reveal" (~560, 2035).
- `adv_07_zeus_after_center_tap.png` - after tapping the screen
  center (540, 1200): first card revealed (ring "Common", count 1),
  stack now shows 4. "Tap to reveal" text gone. Center tap works.
- `adv_08_zeus_tap1..3.png` - three more center taps, 1.5 s apart.
  Each tap reveals one card: Rare (stack 3), Common (stack 2),
  Rare (stack 1). Rewards per run: 1 to maybe ~10 (user), max 6 now.
- `adv_09_zeus_last_card.png` - one more center tap: last card
  (ring, Rare), stack shows 0. Still the same reward screen.
- `adv_10_zeus_after_zero.png` - tap after stack 0: summary of all
  revealed cards (5 rings, grid 3+2) and a red X top right
  (~990, 165) appears only now. The red X is the "all revealed"
  signal (taps until it shows; it never shows during revealing).
- `adv_11_zeus_extra_tap.png` - center tap on the summary CLOSES it
  (no need for the red X): back on "Feast on Olympus", Level 79,
  keys now 1/2 (one key spent per "Complete last level"). Extra
  center taps then land on the "Rewards" ribbon (540, 1200) of this
  dialog - not a button, so "tap center ~10x" looks safe.
  User: during center taps watch for the red X - it means all rewards
  are revealed. Keys can be won as a bonus card, so the number of runs
  is unknown - repeat while keys > 0.
- Red X check: ROI device px x 940-1040, y 115-215, HSV red (h<8 or
  h>172, s>120, v>150). Ratio 0.00 on all reveal screens, 0.89 on the
  summary (adv_10). Clean split.
- `adv_12_zeus2_after_complete.png` - 2nd "Complete last level"
  (keys 1/2 -> 0/2): again "Level 78 completed", stack 6.
- `adv_12_zeus2_tap01..07.png` - center taps, red X found after tap 7
  (6 cards + 1 to reach the summary). Summary: 4 rings, 1 Legendary
  (bee), 1 bonus "Key x1" card.
- `adv_13_zeus_after_bonus_key.png` - center tap closed the summary:
  back on "Feast on Olympus" Level 79, keys 1/2 (2nd run spent one,
  bonus key gave one back).
- `adv_14_zeus3_after_complete.png`, `adv_14_zeus3_tap01..06.png` -
  3rd run (last key): stack 5, red X after tap 6. Summary: 1 Epic,
  2 Rare, 2 Common rings, no bonus key.
- `adv_15_zeus_no_keys.png` - !!! IMPORTANT !!! After the keys run
  out, the counter above the buttons shows an AD (clapperboard) icon
  "2/2" instead of the key icon. "Complete last level" would now play
  an AD -> NEVER tap it then. Stop condition: the counter icon is a
  key (silver key) vs an ad icon (black clapperboard), ROI around
  (~500, 1605). Text 2/2 is the same in both cases.
- `adv_16_zeus_dialog_closed.png` - level dialog X (860, 650) closes
  it; back in the Events dialog, still scrolled down. The Zeus' Feast
  card now shows the AD icon "2/2" too (Hangry Pirates: key icon
  2/2). So the key/ad state is visible already in the Events list
  (Zeus icon ~770, 1470; Pirates icon ~770, 1730) - a card with the
  ad icon can be skipped without opening it.
- `adv_17_events_closed.png` - Events dialog X (935, 705) closes it;
  back on the main screen. Closing path confirmed: level dialog X,
  then Events dialog X.
- `adv_18_events_scrolled.png` - Events reopened and scrolled: Zeus
  ad icon 2/2, Hangry Pirates brown key 2/2.
- `adv_19_pirates_level_dialog.png` - Hangry Pirates Enter
  (840, 1830): level dialog "Sunken Ship" (title differs from the
  list name), Level 67, last level (left arrow only), brown key 2/2
  above the buttons, same layout and button positions as Zeus.
  Closed with X (860, 650) and Events X (935, 705), no key spent.

## User decisions (2026-10-13)

- Switch: COLLECT_ADVENTURES_ENABLED.
- Check after start and then every 5 hours.
- key_log line on success when something was collected; the check
  itself (nothing to collect) only goes to autoplay.log.

## Live test 1 (bot, 2026-10-13 20:08)

- Zeus' Feast skipped (ad icon in the list) - OK.
- Hangry Pirates: Complete tapped (key spent), then "reward screen not
  found": the Pirates reward screen is BROWN (HSV 21,157,166), not
  dark blue like Zeus. The bot stopped tapping (safe). The game loop
  then revealed one card by its own taps (`adv_20_live_after_abort`).
  Finished by hand: `adv_21_pirates_tap01..05` (5 cards, 2 Legendary,
  summary red X at the same place), `adv_22_pirates_after_summary`
  (keys 1/2). Fix: both background colors accepted.

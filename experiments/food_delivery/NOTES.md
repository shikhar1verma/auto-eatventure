# Food Delivery – notes for automation

Captured 2026-10-11 on device 1080x2400 (reference in
src/auto_eatventure/coords/reference.py is 1220x2712, so convert:
ref = device * 1220/1080 ≈ * 1.1296).
All coordinates below are DEVICE pixels (1080x2400).

Purpose (from user): mainly to complete a quest. Activate Food
Delivery whenever possible.

The screenshots referenced here are kept only locally (not committed,
~10 MB), same as in `experiments/popular_dish/`.

## Flow (verified manually)

1. Main screen: second white button top-left (below the person
   button) with a delivery truck at ~(66, 570). Usually there, but it
   can move (see "Truck button states"); the icon shows the state
   (`fd_01_available.png` = available).
2. Tap truck -> dialog **"Food Delivery"**, section "New Orders"
   (`fd_02_after_truck_tap.png`), 3 order rows (customer, food icon
   with count, coin reward). Each row has buttons:
   - Reject ~(312, y), Accept ~(540, y), video x2 ~(768, y)
   - row y: 1032, 1462, 1890
   - one row may have a "Best Deal" badge
   - Red X close at ~(900, 534)
3. Decision (user): always take the FIRST order -> tap its Accept
   ~(540, 1032).
4. After Accept the dialog closes by itself, back on main screen
   (`fd_03_after_accept_first.png`). The truck button now shows a
   green progress counter **"0/21"** under the truck (~(72, 614))
   = delivery running, 21 items of the ordered food to produce.
5. When the delivery is done, a ~3 min cooldown starts
   (`fd_04_cooldown.png`): truck is GREY/faded and a grey countdown
   ("1m 47s") is shown under it. Then it becomes available again
   (black truck, no text under it).

## Truck button states

- available: black truck, nothing under it -> tap it
  (`fd_05_available_excl_*.png`: with a pulsing red "!" badge in the
  top-right corner of the button, small/big size alternates)
- running:   black truck + green "N/M" counter under it
- cooldown:  grey truck + grey "Xm Ys" countdown under it
- unavailable: grey truck, nothing under it (seen in the Popular Dish
  screenshots, e.g. right after renovation; reason unknown)

Position is NOT fixed: usually button center ~(66, 570), but when
the person button above is missing the truck button moves up to
~(66, 390) (seen only in Popular Dish era screenshots with the truck
grey, never in the available state - not verified for tapping).
=> search in a left column ROI (x 0..200, y 250..850) and tap the
found position.

Not verified yet: a first order with a "Best Deal" badge. If the
badge shifts the Accept button out of its ROI, the bot just closes
the dialog and tries again after the 60 s pause.

## Detection analysis (template = truck lower half + empty text area,
## device crop [540:630, 8:128] of fd_05_available_excl_1.png)

- The "!" badge never reaches y >= 540, so it doesn't affect it.
- TM_CCOEFF_NORMED (HSV or BGR) can NOT tell black from grey truck
  (it is invariant to brightness): grey/unavailable scores 0.988.
- TM_SQDIFF_NORMED on BGR (lower = better):
  available 0.000 (all 8 badge frames), running 0.049, unavailable
  grey 0.092, cooldown 0.116, dimmed under a dialog >= 0.62.
  => threshold ~0.02 separates "available" from everything else.

## Implementation (branch foodDelivery)

- `FOOD_DELIVERY_ENABLED="1"` in `.env`, off by default.
- Every loop screenshot: `food_delivery.find_truck()`
  (SQDIFF, ~15 ms) -> `food_delivery.accept()`: tap truck, verify the
  first order's Accept button (HSV template, ROI), tap Accept, verify
  the dialog closed. After any attempt the checks pause for 60 s
  (code review: a falsely confirmed accept must not loop). Success logged to autoplay.log only (user: key_events.log
  would get cluttered).
- Templates: `food_delivery_available.png` (from
  `fd_05_available_excl_1.png` [540:630, 8:128]),
  `food_delivery_accept.png` (from `fd_02_after_truck_tap.png`
  [994:1080, 444:636]), both upscaled to reference resolution.
- What happens to a running delivery on renovation / fly is not
  investigated (user: doesn't matter much and it is rare).

## Observed in the bot run (2026-10-11)

- Accepted 11:39:49, renovation clicked ~11:40:57, at ~11:41:30 the
  truck showed cooldown "1m 51s" (`fd_06_after_renovation.png`), so the
  cooldown started ~11:40:20 = the delivery had already finished
  ~30 s after Accept, before the renovation. => Renovation does NOT
  reset the delivery cooldown.
- Second renovation 11:50:54, cooldown started ~11:50:29: again the
  delivery (accepted 11:50:02) finished ~30 s after Accept. Deliveries
  are short, so a renovation rarely hits a running one.

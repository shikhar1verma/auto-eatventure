# "Restaurant Race ended!" dialog

2026-10-14 ~22:40 both bots got stuck: the race ended and this dialog
covered the game on both phones.

- `re_01_xiaomi.png`, `re_01_oneplus.png` - dialog: checkered flag,
  "Restaurant Race ended!", ranking with gem rewards, own gems, blue
  "Claim" (no ad icon). NO red X. User: tap Claim.
  Xiaomi: Claim ~(540, 1843); OnePlus ~(619, 2132).
- Why the bot didn't recover: `get_food_icon_locations()` (grayscale
  template; since replaced, see `experiments/upgrade_icons/NOTES.md`)
  still finds a dimmed station upgrade arrow at the left
  edge (Xiaomi (70, 1756)), taps it (lands on the dark backdrop, does
  nothing), and since food icons were "found", nothing_to_update never
  grows, so the stale recovery never runs.
- `re_02_xiaomi_after_claim_1..6.png` - after Claim the dialog is gone;
  under it the bot's own Upgrades dialog was still open (it opened
  just before the race dialog came). No other dialog followed.
- `re_03_xiaomi_upgrades_closed.png` - Upgrades closed by its X.

Templates `race_ended_title.png`, `race_claim.png` (from Xiaomi,
upscaled to reference): HSV 0.96-1.00 on both phones, <= 0.51 on all
other 150+ saved screenshots (gray <= 0.57).

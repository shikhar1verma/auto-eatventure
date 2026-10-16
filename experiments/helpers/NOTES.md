# Invite a helper - notes

Device used: 1080x2400 (reference 1220x2712). Screenshots
(`hp_*.png`, `seq/s_*.png`) are not committed.

## Flow

1. Helper (person) button - the top white button in the left column,
   device ~(66, 384), always in the same place.
2. Tap it -> "Invite a helper" dialog. It shows "Loading..." first
   (~1.5-3.5 s), then a list of 5 players, each with **Invite** and
   **+4m** (ad - never tapped).
3. Tap the first **Invite** (device ~(713, 900)) -> the dialog closes
   by itself and the helper appears in the kitchen with their name.

## Button states (under the person)

| State | Look | Duration |
|-------|------|----------|
| available | black person, empty line | until used |
| working | black person, green "3m 58s" | ~4 min |
| ad offer | black person, blue ad icon + "29s" (at the end only the icon) | ~30 s |
| cooldown | grey person, grey "29m 25s" | ~30 min |

A red "!" badge sits in the top-right corner when available and during
the ad offer. It pulses: x 100..149 / y 299..348, grown x 95..154 /
y 294..353 (device px).

## Detection

`TM_SQDIFF_NORMED` on BGR (like the Food Delivery truck). Template =
device crop `[395:450, 8:92]` of `hp_01_available.png` (person's body
+ the empty line), upscaled to reference -> `helper_available.png`.
It is left of the "!" badge, so the badge never touches it.

Scores (min SQDIFF in the ROI, 1080x2400):

| State | Score |
|-------|-------|
| available (23 screenshots) | 0.0000 |
| ad icon only, no number (`s_20`) | 0.0298 |
| ad offer with countdown | 0.048-0.059 |
| working (green countdown) | 0.048-0.115 |
| cooldown (grey) | 0.093-0.098 |
| dialog fading in (`hp_02`) | 0.075 |
| dialog over it (dimmed) | >= 0.62 |

Threshold 0.015. A crop with the whole person (`[338:448, 8:92]`) was
worse: the "ad icon only" state scored 0.0137. At 720x1600,
1220x2712 and 1440x3200 the available max is 0.0009 and the closest
other state 0.029.

The screenshots are ~5 s apart, so a short frame with an empty line
between two states (e.g. "3s" -> ad offer) can't be ruled out; the
bot confirms availability on a second screenshot 1 s later.

Invite button: HSV template `[866:930, 642:782]` of
`hp_03_dialog_loaded.png` -> `helper_invite.png`, threshold 0.8 in a
ROI around the first row (match 0.95 after scaling). Scores
~0.13-0.37 on all other screenshots. The loaded dialog's red X is
found by the existing `popup_close_cross` (0.98), so
`popups.close_popup()` closes it on a failure.

## Unverified

- Fully shown "Loading..." dialog (list never loads, e.g. offline):
  its X is elsewhere and was only seen fading in (0.76), so the close
  after the 10 s timeout is unconfirmed. Retried after 10 min.
- What happens to a working helper on renovation / new city.

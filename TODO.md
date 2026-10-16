# TODO

Possible improvements, not planned yet.

## Real game restart when stuck for a long time

Stale recovery (`StaleWatch` in `src/auto_eatventure/actions/stale.py`) only brings the
game to the foreground (`Device.start_app()`), it never restarts it.
That does not help when the game itself is stuck, e.g. an ad that keeps
coming back to the front (2026-10-12: an ad opened at 16:34 and the bot
was stuck for 40 min, each foreground call showed the ad again 2 s
later).

Idea: when nothing can be updated for a long time (e.g. several stale
recoveries in a row, ~10+ min), restart the game for real:

1. `Device.close_app()` (`src/auto_eatventure/android/device.py`,
   `am force-stop`, already exists, unused)
2. `Device.start_app()`
3. `start_dialogs.wait_until_ready()` (waits for the settings icon,
   taps known dialogs)

Verified on the Xiaomi (2026-10-12): `am force-stop` kills the game
process (`pidof` empty, the launcher is in front), `start_app()` starts
a new process, the "Loading..." screen takes ~3 s and the game is
playable after ~15 s, without any dialog (short downtime).

Open questions:

- Threshold: how long to wait before a restart (the last level of a
  city can legitimately take 30+ min with stale swipes)
- A long downtime shows the offline earnings dialog;
  `wait_until_ready()` already closes it

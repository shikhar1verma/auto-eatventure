# Start dialogs (OnePlus Nord 3, Jenik's phone)

Device KZXCZ9HA79WKJR55, 1240x2772. 2026-10-14 the bot hung in
`init_game()` (now `start_dialogs.wait_until_ready()`) ("Init:
waiting for game to be ready" forever): two dialogs covered (dimmed)
the settings gear.

- `sd_01_oneplus_stuck.png` - "While you were away..." (gems from
  players who invited you: "<name> invited you", 1 gem, Claim buttons,
  "Daily 0/10"). Red X ~(1050, 845). Claim is never tapped (rule);
  closed by the X.
- `sd_02_after_x_1..6.png` - under it "Offline Earnings" (6.47M,
  "Collect x2" with an ad icon - never tapped). Red X ~(1000, 1046).
  The `offline_earnings` template scores only 0.71 here (threshold
  0.8), so `init_game()` didn't know it.
- `sd_03_after_offline_x_1..4.png` - main screen after both X's, no
  more dialogs.
- `restart1/` - force-stop + start, a frame every ~2 s for 67 s:
  launcher icon, Loading (~3-5 s), main screen from ~7 s, no dialogs
  (they come only after a longer absence and depend on the server).

`popup_close_cross` (HSV) finds both X's (0.98-0.99). The gear ROI
tells dimmed (both dialogs, loading screen) from clear (main) on this
phone too.

User (2026-10-14): the dialogs don't come every time, they depend on
the connection / server answer; count with up to ~30 s after the
start. Close them after the start; when the game is stuck, look for
close X's and close them.

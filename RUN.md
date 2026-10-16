# How to run

On the phone set "Do not disturb mode" (To stop notification popups)
Start eatventure
Set Settings -> Battery saving mode  (not mandatory, but telephone is not so hot)


Start android studio, connect my phone (resolution 1220x2712)

Start Intellij IDEA -  there you can debug Python

And run the module `auto_eatventure` (`src/auto_eatventure/__main__.py`)
from the project root with `src` on `PYTHONPATH`
(`PYTHONPATH=src python -m auto_eatventure`) - can be run in debug mode.


# Additional notes
Running in emulator was not successful, because eatventure use "Google Play Games".
And it recognizes emulator and do not allow you to login.

Most of coordinates are adjusted for my resolution

Removed functionality (no longer in the code)
 - add bonuses
 - investors

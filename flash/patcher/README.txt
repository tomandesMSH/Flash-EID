External Item Descriptions for The Binding of Isaac (Flash)
============================================================

Shows EID-style descriptions for item pedestals, trinkets, cards and pills in the original
Flash version of The Binding of Isaac (Steam, including Wrath of the Lamb).

This package contains NO game files. The patcher builds the modded game from your own copy.


Requirements
------------
- Windows
- The Binding of Isaac (Flash) installed, e.g. from Steam
- For the script version only: Python 3.8 or newer (https://www.python.org/downloads/),
  no extra packages needed


Install
-------
With the exe (EID_Flash_Patcher.exe):
1. Put EID_Flash_Patcher.exe in the folder where you want to keep the game (the "EID Flash"
   folder is created next to it) and double-click it.
2. A game window appears for a few seconds while the patcher reads the game, then closes.
3. At the end, the patcher shows a Steam launch option and copies it to your clipboard
   (see "Steam" below).
4. Start the game with Steam's Play button (after pasting the launch option) or with
   "EID Flash\EID Flash.exe".

With the Python script (this zip):
1. Unzip this folder anywhere.
2. Open a command prompt in this folder and run:

       python eid_flash_patcher.py --get-projector

3. Start the game with Steam's Play button (after pasting the launch option it shows) or with
   "EID Flash\EID Flash.exe".

If the game is not in your Steam library, add --game "<folder with Isaac.exe>"
(for the exe: run it from a command prompt with that option).

The exe and --get-projector download Adobe's official Flash Player 32 projector
(flashplayer_32_sa.exe) from fpdownload.macromedia.com and check its fingerprint. You can also put
your own copy into the "EID Flash" folder instead (exe: use --no-projector).


Steam
-----
At the end, the patcher shows a launch option like this and copies it to your clipboard:

    "<your folder>\EID Flash\EID Flash.exe" %command%

Paste it into Steam: Library > right-click The Binding of Isaac > Properties > General >
Launch Options. Steam's Play button then starts EID Flash instead of the normal game, and Steam
still shows the game as running and counts your playtime.

- If you move the "EID Flash" folder, run the patcher again and paste the new launch option.
- To play the normal game again, clear the Launch Options box.


Playing
-------
- Walk up to an item, trinket, card or pill to see its description.
- F2 shows/hides the descriptions.
- Pills show "Unidentified Pill" until you have taken a pill of that color.
- The modded game uses the same save as the Steam version: your unlocks and progress carry
  over in both directions. Don't run both versions at the same time, or one may overwrite the
  other's progress.
- Steam achievements: the launcher sends the achievements you unlock to Steam a few seconds
  later, with the game's own FlashAchievements.exe (Steam must be running). achievements.log
  next to the launcher shows what was sent.
- Your game files are never modified. To uninstall, clear the Steam launch option (if you set
  it) and delete the "EID Flash" folder.


Credits
-------
External Item Descriptions by Wofsauge and contributors:
https://github.com/wofsauge/External-Item-Descriptions
Item information based on The Binding of Isaac Wiki (CC BY-SA 3.0) and checked against the game.
The Binding of Isaac (c) Edmund McMillen & Florian Himsl.

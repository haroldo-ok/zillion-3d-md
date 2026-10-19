# Zillion 3D for the Sega Genesis / Mega Drive

A port of Zillion 3D (the Wolfenstein 3D mod with Akai Koudan Zillion characters,
ModDB file `Zillion_3D_SDL.rar`) to the Genesis, built on the wolf-3d-md SGDK port.

ROM: `out/rom.bin` (3,932,160 bytes, copied to `/home/user/Zillion3D_Genesis.bin`).

## What was converted from the mod's own data (no placeholders)
- Walls, sprites, pictures, fonts, help/end texts: from the mod's `VSWAP.WL6`, `VGAGRAPH.WL6`, `VGAHEAD.WL6`, `VGADICT.WL6`.
- All 20 levels (`Zillion3D_E1_L1` .. `Zillion3D_E2_L10`) from `GAMEMAPS.WL6` / `MAPHEAD.WL6`.
- 48 digitised sound effects and the 27 IMF music tracks from `AUDIOT.WL6` / `AUDIOHED.WL6`.
- Per-level ceiling colour, par time and music are read from the id Software WL6 source tables
  (`vgaCeiling`, `parTimes`, `songs`), which the mod's Wolf4SDL executable uses.

## Changes made for two episodes
- New Game asks for the episode first ("Episode 1" / "Episode 2"), then difficulty.
- Levels run 0..19; floor numbers shown on the HUD, intermission and save slots are per episode.
- Elevator / secret-level flow follows the original per episode (floor 10 is the secret level).
- Save slots, intermission ratios and high scores cover all 20 levels.

## Sound engine changes
- The sound effects now use the SGDK single-channel PCM driver (`SND_PCM_*`) instead of the 4-channel one.
  Wolfenstein plays one effect at a time, so this matches the original. It also lets each sound have its own rate.
- `tools/audio.py` clamps music chunks to the bytes actually present. In the mod's `AUDIOT.WL6`, each music chunk's length word is one byte larger than its data, so the last event of each track may be dropped.

## Known differences from the PC version
- Digitised effects are played at 8 kHz and AdLib-only effects at 11 kHz. Every sound with a
  digitised version uses it, in every sound mode (the Genesis has no OPL chip).
- Positional sound uses pan (left/right/centre) and mutes distant sounds; the single PCM channel
  has no per-sound volume.
- Some graphics in the Genesis screen (3-D view border effects, demo playback) are not ported.
- The end-of-episode and help texts are the WL6 texts in the data; no Zillion-specific text was found in the mod.

## Verification
- Builds with SGDK (libmd rebuilt with the same GCC 14.2 as the link) and gcc-m68k-linux-gnu.
- Boots in Genesis Plus GX (headless harness): splash -> Zillion 3D title -> main menu -> episode select -> difficulty -> gameplay with HUD (Floor 1, Lives 3, Health 100%).
- Not yet checked: episode 2 gameplay, the level-to-level elevator flow, the bosses, save/load, and sound output by ear.

## Build
Requirements: an SGDK tree (`GDK`), an m68k GCC (Debian/Ubuntu `gcc-m68k-linux-gnu`, GCC 14.2 was used),
Java for `rescomp`, and Python 3 with numpy and Pillow.

1. Build the SGDK helpers and library with the same toolchain (sjasm, bintos, convsym, then `make -f makelib.gen PREFIX=m68k-elf- release`).
2. Regenerate the assets (needs the Zillion `.WL6` files and the id Software `wolf3d` source tree for the palette and name tables):
       python3 -I tools/convert.py <dir with Zillion .WL6 files> <wolf3d id source dir> .
   Set `WOLF_EXT` to override the data extension (default WL6).
3. Build:
       make GDK=/path/to/sgdk EXTRA_FLAGS="-Isrc -g1"
   Output: `out/rom.bin`.

Headless test: build Genesis Plus GX as a libretro core and run `tools/libretro_harness.c` against `out/rom.bin`.

Credits: Wolfenstein 3D (c) id Software; Zillion 3D by smokingsimon; Akai Koudan Zillion characters (c) their owners. Unofficial fan port.

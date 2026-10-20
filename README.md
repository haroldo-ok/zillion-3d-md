# Zillion 3D for the Sega Genesis / Mega Drive

A port of **moonkey's [*Zillion 3D*](https://moonkey.itch.io/zillion-3d)** — the *Wolfenstein 3D* mod
featuring characters, art, and music inspired by the anime *Akai Koudan Zillion* — to the
Sega Genesis / Mega Drive, written in C for SGDK (68000) and built on
[wolf-3d-md](https://github.com/haroldo-ok/wolf-3d-md).

- **Original PC mod:** *Zillion 3D* by [moonkey](https://moonkey.itch.io/zillion-3d) (<https://moonkey.itch.io/zillion-3d>)
- **ROM:** `Zillion3D_Genesis.bin` (`out/rom.bin`, ~3.88 MB aligned image, 32 KB battery SRAM declared in header)

## Controls
- **D-pad:** move forward/back, turn left/right
- **B:** fire    **A:** run    **C:** use (door/switch); **C + Left/Right:** strafe
- **A + C:** next weapon;  **X / Y / Z:** knife / pistol / machine gun (6-button pad)
- **Start:** pause menu (New Game, Sound, Control, Load/Save Game, Read This!, View Scores, Back to Game)

## Performance & Bug Fixes (v0.0.2)
- **Precompiled 68000 column scalers (`tools/scalers.py`, `src/gen/scalers.c`):** replaces the runtime per-pixel fixed-point loop with straight-line generated 68000 machine code across 321 height steps (`0..512`). Uses 12-cycle `(a0)` / `(a0)+` indirect moves and `lea d16(a0),a0` skips to run ~25% faster per wall column while saving ~61 KB of ROM (`136,536` bytes total), keeping all 20 levels comfortably below the 4 MB cartridge limit without bank switching.
- **Ray interpolation (`src/render.c`):** skips casting odd columns when adjacent even rays hit the exact same `(tile, postsource)` wall column within `|H_left - H_right| <= 2`.
- **Faster distance math & DDA stepping (`src/render.c`):** replaces 32-bit `FixedByFrac` projection math with 16-bit signed hardware multiplies (`muls`) and keeps pre-shifted `xtile << 6` + signed 16-bit map indices (`s16`) for single-instruction `d8(An,Dn.w)` 68000 indexed lookups.
- **Incremental floor/ceiling clear & tighter HUD weapon blitter (`src/render.c`):** fills only newly exposed rows between frames (`prev_ClearTop` / `prev_ClearBot`) and trims transparent spans on weapon sprites.
- **Low-framerate button tap latching (`src/input.c`, `src/input.h`):** latches short button presses across frame boundaries so quick taps on Start, fire, or use are never dropped between renders.
- **Cyan square VDP sprite bug fixed (`src/vid.c`):** moves SGDK's sprite attribute table away from `0xF400` (inside active tile RAM used by the software framebuffer) to zeroed VRAM (`0xB800`), eliminating the stray `8x8` cyan/teal square on screen.
- **20-level SRAM Save/Load fix (`src/save.c`):** updates `rtm[]` in `Save_Read()` from `8` entries to `NUM_LEVELS` (`20`) so loading saved games never overflows stack state.

### Measured Frame Rates (Genesis Plus GX, `59.9227 Hz` NTSC)
- **Start corridor benchmark (`./tools/fps.sh`, 1,190 vblanks):** **9.04 fps** (up from 5.45 fps, **+65.9%**)
- **Wide spawn room view (1,200 vblanks):** **7.49 fps** (up from 5.54 fps, **+35.1%**)
- **Episode 2 hallway walk + doors + combat (1,000 vblanks):** **6.59 fps** (up from ~4.85 fps, **+35.9%**)

## What was converted from the mod's own data (no placeholders)
- Walls, sprites, pictures, fonts, help/end texts: from *Zillion 3D*'s `VSWAP.WL6`, `VGAGRAPH.WL6`, `VGAHEAD.WL6`, `VGADICT.WL6` (<https://moonkey.itch.io/zillion-3d>).
- All 20 levels (2 episodes of 10 levels each, `Zillion3D_E1_L1` .. `Zillion3D_E2_L10`) from `GAMEMAPS.WL6` / `MAPHEAD.WL6`.
- 48 digitised sound effects and the 27 IMF music tracks from `AUDIOT.WL6` / `AUDIOHED.WL6`.
- Per-level ceiling colour, par time and music are read from the id Software WL6 source tables
  (`vgaCeiling`, `parTimes`, `songs`), matching the Wolf4SDL build used by the mod.

## Changes made for two episodes
- New Game asks for the episode first ("Episode 1" / "Episode 2"), then difficulty.
- Levels run `0..19`; floor numbers shown on the HUD, intermission and save slots are per episode.
- Elevator / secret-level flow follows the original per episode (floor 10 is the secret level).
- Save slots, intermission ratios and high scores cover all 20 levels.

## Sound engine changes
- Sound effects use the SGDK single-channel PCM driver (`SND_PCM_*`) instead of the 4-channel one.
  Wolfenstein plays one effect at a time, matching the original while allowing per-sound playback rates.
- `tools/audio.py` clamps music chunks to the bytes actually present (in the mod's `AUDIOT.WL6`, each music chunk's length word is one byte larger than its data).

## Known differences from the PC version
- Digitised effects play at 8 kHz and AdLib-only effects at 11 kHz. Every sound with a digitised version uses it in every sound mode (the Genesis has no OPL chip).
- Positional sound uses stereo pan (left/right/centre) and mutes distant sounds; the single PCM channel has no per-sound volume.
- Some PC graphics (3-D view border flashes, demo playback) are not ported.
- The end-of-episode and help texts are the WL6 texts present in the mod's data files.

## Verification
- Builds cleanly with SGDK (`libmd` compiled with the same GCC 14.2 LTO toolchain) and `gcc-m68k-linux-gnu`.
- Verified headlessly in Genesis Plus GX (`tools/libretro_harness.c`):
  - Splash -> Zillion 3D title -> main menu -> Episode 1 & Episode 2 gameplay with HUD.
  - Full in-game SRAM Save -> Walk -> Load round-trip verified pixel-for-pixel (`0 / 57,600` differing 3D view pixels).
  - Visual comparison confirms complete removal of the stray `8x8` cyan VDP sprite artifact across all screens.

## Build & Benchmark
Requirements: an SGDK tree (`GDK`), an m68k GCC (`gcc-m68k-linux-gnu`, GCC 14.2),
Java for `rescomp`/`sizebnd.jar`, and Python 3 with `numpy` and `Pillow`.

1. Build the SGDK helpers and library with the same toolchain (`sjasm`, `bintos`, `convsym`, then `make -f makelib.gen GDK=. PREFIX=m68k-elf- release`).
2. Regenerate the assets (needs *Zillion 3D*'s `.WL6` files from <https://moonkey.itch.io/zillion-3d> and the id Software `wolf3d` source tree for the palette and name tables):
   ```sh
   python3 -I tools/convert.py <dir with Zillion .WL6 files> <wolf3d id source dir> .
   ```
   Set `WOLF_EXT` to override the data extension (default `WL6`).
3. Build release ROM:
   ```sh
   make GDK=/path/to/sgdk -j$(nproc)
   ```
   Output: `out/rom.bin`.
4. Run headless Genesis Plus GX FPS benchmark:
   ```sh
   ./tools/fps.sh out/rom.bin
   ```

## Credits
- *Zillion 3D* mod by **[moonkey](https://moonkey.itch.io/zillion-3d)** (<https://moonkey.itch.io/zillion-3d>).
- *Wolfenstein 3D* engine (c) id Software; Sega Genesis port built on [wolf-3d-md](https://github.com/haroldo-ok/wolf-3d-md).
- *Akai Koudan Zillion* characters, art, and music (c) Sega / Tatsunoko.
- Non-commercial fan port; none of the rights holders were involved in this project.

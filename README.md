# ZMK keyboard configurations

This repository builds El Chibre, Totem (left, right and dongle), and Endgame in parallel using the ZMK v0.3 GitHub Actions workflow. Push a change or run the workflow manually, then download the combined firmware artifact from the Actions run. The matrix also builds settings-reset firmware for both wireless controllers.

`config/shared.keymap` is the El Chibre layout and the source of truth for all three keyboards. The individual `.keymap` files select the key positions and map the extra keys around that layout. Totem's extra bottom-row keys are transparent and its inner thumb keys are unused on the base layers; Endgame's outer keys are unused on the base layers. Hardware-specific settings remain in the respective shield and configuration files.

Endgame uses the RP2040 Zero board definition from [nmunnich/zmk at aa2294c](https://github.com/nmunnich/zmk/tree/aa2294c/app/boards/arm/waveshare_rp2040_zero), included locally so all keyboards can use the same ZMK version.

## Local builds with Nix

Install Nix with flakes enabled, then from this repository run (Nix requires `flake.nix` and `flake.lock` to be tracked or staged in Git):

```sh
nix develop
west init -l config               # first time only
west update --fetch-opt=--filter=tree:0
python build-local.py
```

The first update downloads ZMK, Zephyr and their modules into this directory. Run `west update` again after changing `config/west.yml`. The script builds every entry in `build.yaml` in parallel; each firmware is at `build/<shield>-<board>/zephyr/zmk.uf2`, with a corresponding `build/<shield>-<board>.log`. A failed target is reported and makes the command exit unsuccessfully. Set `CMAKE_BUILD_PARALLEL_LEVEL` before running the script to change the per-target compilation concurrency (default: 2).

For a single target, for example:

```sh
west build -s zmk/app -d build/elchibre -b nice_nano_v2 -- \
  -DZMK_CONFIG="$PWD/config" -DSHIELD=elchibre
```

Nix pins the build tools in `flake.lock`; West downloads the ZMK and Zephyr revisions from their manifests. The Nix toolchain is not identical to the one used by GitHub Actions, so verify firmware on the actual keyboard before relying on it.

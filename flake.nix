{
  description = "Local ZMK firmware build environment";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";

  outputs = { nixpkgs, ... }:
    let
      systems = [ "aarch64-darwin" "x86_64-darwin" "aarch64-linux" "x86_64-linux" ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in {
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            cmake ninja dtc git gperf gcc-arm-embedded
            (python3.withPackages (p: with p; [
              west pyelftools pyyaml pykwalify canopen packaging progress psutil
              pylink-square pyserial requests anytree intelhex
            ]))
          ];
          ZEPHYR_TOOLCHAIN_VARIANT = "gnuarmemb";
          GNUARMEMB_TOOLCHAIN_PATH = "${pkgs.gcc-arm-embedded}";
        };
      });
    };
}

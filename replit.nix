{pkgs}: {
  deps = [
    pkgs.mailutils
    pkgs.libxcrypt
    pkgs.rustc
    pkgs.libiconv
    pkgs.cargo
    pkgs.libyaml
    pkgs.bash
    pkgs.zlib
    pkgs.xcodebuild
  ];
}

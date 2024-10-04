{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.discord
    pkgs.python310Packages.flask
  ];
}

{
  description = "learning project, do not use";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs";

  outputs = { self, nixpkgs, flake-utils }:
    (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python3;
        python3Packages = pkgs.python3Packages;
        debugPython = python.overrideAttrs(oa: {
          configureFlags = oa.configureFlags ++ [ "--with-pydebug" ];
        });

        aiohttp_cap = python3Packages.buildPythonPackage {
            pname = "aiohttp_cap";
            version = "0.0.1";
            src = ./.;
            propagatedBuildInputs = with pkgs.python3Packages; [
              aiohttp
            ];
            checkInputs = with pkgs.python3Packages; [
              pytest pytest-asyncio
              mypy
            ];
          };
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            ((python.withPackages (ps: with ps; [
              aiohttp aiodns brotli
              pytest pytest-asyncio
            ])).override { python = debugPython ;})
          ];
          nativeBuildInputs = (with python3Packages; [
            mypy
          ]);
          shellHook = ''
            export PYTHONASYNCIODEBUG=1
          '';
        };
        packages.project-name = aiohttp_cap;
        defaultPackage = aiohttp_cap;
      }
    ));
}

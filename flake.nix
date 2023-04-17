{
  description = "learning project, do not use";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs";

  outputs = { self, nixpkgs, flake-utils }:
    (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python3Packages = pkgs.python3Packages;

        aiohttp_cap = python3Packages.buildPythonPackage {
            pname = "aiohttp_cap";
            version = "0.0.1";
            src = ./.;
            propagatedBuildInputs = with python3Packages; [
              aiohttp
            ];
            checkInputs = with python3Packages; [
              pytestCheckHook pytest pytest-asyncio
              mypy
            ];
          };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            (python3Packages.python.withPackages (ps: with ps; [
              aiohttp aiodns brotli
              pytest pytest-asyncio
            ]))
          ];
          nativeBuildInputs = (with python3Packages; [
            mypy
          ]);
          shellHook = ''
            export PYTHONASYNCIODEBUG=1 PYTHONMALLOC=debug PYTHONFAULTHANDLER=1
            #export PYTHONWARNINGS=error
            #export PYTHONTRACEMALLOC=1
          '';
        };
        packages.project-name = aiohttp_cap;
        packages.default = aiohttp_cap;
      }
    ));
}

{
  description = "learning project, do not use";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python3Packages = pkgs.python3Packages;

        pylama = python3Packages.pylama.overridePythonAttrs (_: {
          # https://github.com/klen/pylama/issues/232
          patches = [
            (pkgs.fetchpatch {
              url = "https://github.com/klen/pylama/pull/233.patch";
              hash = "sha256-jaVG/vuhkPiHEL+28Pf1VuClBVlFtlzDohT0mZasL04=";
            })
          ];
        });

        deps = pyPackages: with pyPackages; [
          aiohttp aiodns brotli
        ];
        tools = pkgs: pyPackages: (with pyPackages; [
          pytest pytestCheckHook
          coverage pytest-cov
          pylint pydocstyle
          pylama pyflakes pycodestyle mypy mccabe
          eradicate
          pytest-asyncio
        ]);

        aiohttp_cap = python3Packages.buildPythonPackage {
          pname = "aiohttp_cap";
          version = "0.0.1";
          src = ./.;
          format = "pyproject";
          propagatedBuildInputs = deps python3Packages;
          nativeBuildInputs = [ python3Packages.setuptools ];
          checkInputs = tools pkgs python3Packages;
        };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [(python3Packages.python.withPackages deps)];
          nativeBuildInputs = tools pkgs python3Packages;
          shellHook = ''
            export PYTHONASYNCIODEBUG=1 PYTHONMALLOC=debug PYTHONFAULTHANDLER=1
          '';
        };
        packages.aiohttp_cap = aiohttp_cap;
        packages.default = aiohttp_cap;
      }
    );
}

{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      pyproject = builtins.fromTOML (builtins.readFile ./pyproject.toml);

      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      forEachSupportedSystem =
        f:
        nixpkgs.lib.genAttrs supportedSystems (
          system:
          f {
            pkgs = import nixpkgs { inherit system; };
          }
        );
    in
    {
      packages = forEachSupportedSystem (
        { pkgs }:
        let
          python = pkgs.python3;
          trafikverket-client = python.pkgs.buildPythonPackage {
            pname = pyproject.project.name;
            version = pyproject.project.version;
            src = ./.;
            pyproject = true;

            build-system = [ python.pkgs.hatchling ];

            dependencies = with python.pkgs; [
              aiohttp
              pydantic
            ];

            optional-dependencies = {
              qr = [ python.pkgs.qrcode ];
            };

            pythonImportsCheck = [ "trafikverket_client" ];
          };
        in
        {
          default = trafikverket-client;
          inherit trafikverket-client;
        }
      );

      devShells = forEachSupportedSystem (
        { pkgs }:
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              (python3.withPackages (
                ps: with ps; [
                  aiohttp
                  pydantic
                  qrcode
                  mypy
                ]
              ))
              pyright
              pre-commit
              ruff
              ripgrep
              cowsay
              clolcat
              fzf
            ];

            shellHook = ''
              eval "$(fzf --bash)"
              echo "Sometimes you just need to try again" | cowsay -r | clolcat
            '';
          };
        }
      );
    };
}

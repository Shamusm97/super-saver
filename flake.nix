{
  description = "Python development environment";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        pythonPackages = pkgs.python3Packages;
      in
        {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python packages
            (python3.withPackages (ps: with ps; [
              httpie
              aiohttp
              aiofiles
              requests
              fuzzywuzzy
              pandas
              tqdm
              scikit-learn
              textual
            ]))
          ];
          shellHook = ''
      echo "Super Scraper 2 -- Python development environment activated!"
      python --version
      '';
        };
      }
    );
}

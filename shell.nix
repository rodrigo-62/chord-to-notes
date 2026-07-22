{ pkgs ? import <nixpkgs> {} }:

let
  python = pkgs.python310;
  pythonEnv = python.withPackages (ps: with ps; [
    ply
    pytest
  ]);
in
pkgs.mkShell {
  packages = [
    pythonEnv
  ];
}

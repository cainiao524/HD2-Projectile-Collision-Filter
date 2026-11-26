# Projectile Self Hit (local.p11-self-hit-fast) as a CMake project: copy this folder into HellForge's mods folder, then open it in Rider, CLion or VS Code, or build it with
#   cmake --preset default && cmake --build --preset default
# (or, without CMake: HellForge.Cli build-mod --mod <this folder>, or Build now in the mod's menu on the Mods page).
cmake_minimum_required(VERSION 3.25)
project(p11_self_hit_fast C)
include(../../app/sdk/cmake/HellForgeMod.cmake)

hellforge_add_mod(p11_self_hit_fast src/p11_self_hit_fast.c)

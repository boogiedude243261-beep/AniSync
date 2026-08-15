<div align="center">

<img src="https://raw.githubusercontent.com/boogiedude243261-beep/AniSync/main/icon.png" width="120" height="120" style="border-radius: 35%;" alt="AniSync Logo">

#  AniSync
### *Lightweight Service Add-On/Background Daemon for Kodi*

[![Kodi Version](https://img.shields.io/badge/Kodi-v20%2B%20(Nexus%2FOmega)-blue.svg?style=flat-square&logo=kodi)](https://kodi.tv)
[![Platform](https://img.shields.io/badge/Platform-All-lightgrey.svg?style=flat-square)]()

<div align="center">

---

## Overview

When streaming anime through third-party Kodi add-ons like **Otaku**, media streams often rely on absolute episode numbering or messy internal layout parameters. This breaks standard television indexing, leaving subtitle add-ons (such as OpenSubtitles or a4kSubtitles) unable to automatically match files.

**AniSync** runs silently as a lightweight background service daemon in Kodi. The moment an anime stream starts, AniSync intercepts the playback event, queries the **AniList GraphQL API** and **AniZip mappings**, translates split-cour offsets and structural mismatches, and injects clean TMDB metadata tags directly into Kodi's active player. 

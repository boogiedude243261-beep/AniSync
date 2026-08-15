<div align="center">

# ⚡ AniSync
### *Lightweight background metadata sync daemon for Kodi*

[![Kodi Version](https://img.shields.io/badge/Kodi-v20%2B%20(Nexus%2FOmega)-blue.svg?style=flat-square&logo=kodi)](https://kodi.tv)
[![Platform](https://img.shields.io/badge/Platform-All-lightgrey.svg?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)]()

</div>

---

## 🎯 Overview

When streaming anime through third-party Kodi add-ons like **Otaku**, media streams often rely on absolute episode numbering or messy internal layout parameters. This breaks standard television indexing, leaving subtitle add-ons (such as OpenSubtitles or a4kSubtitles) unable to automatically match files.

**AniSync** runs silently as a lightweight background service daemon in Kodi. The moment an anime stream starts, AniSync intercepts the playback event, queries the **AniList GraphQL API** and **AniZip mappings**, translates split-cour offsets and structural mismatches, and injects clean TMDB metadata tags directly into Kodi's active player.

---

## ✨ Features

* 🚀 **Real-Time Playback Monitoring** — Listens continuously in the background for active video playback inside the Otaku plugin.
* 🔍 **Smart ID Resolution** — Automatically extracts direct AniList IDs or falls back to intelligent title searches via the AniList GraphQL API.
* ⚖️ **Offset & Mismatch Correction** — Smoothly resolves multi-cour and structural indexing errors using real-time AniZip mapping data.
* 🔄 **Metadata Bridge** — Dynamically injects standard season and episode metadata tags (`updateInfoTag`) straight into Kodi's active media player.
* ⚡ **Frictionless Subtitles** — Pre-fills player states so background subtitle services can instantly and silently fetch matching `.srt` files without manual queries.

---

## 📂 Project Structure

To package **AniSync** for local installation or GitHub distribution, organize your repository directory like this:

```text
service.anisync/
├── addon.xml
├── service.py
└── icon.png

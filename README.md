<div align="center">

<img src="https://raw.githubusercontent.com/boogiedude243261-beep/Anubis/main/icon.png" width="120" height="120" style="border-radius: 5%;" alt="AniSync Logo">

#  Anubis
### *Lightweight Service Add-On/Background Daemon for Kodi*

[![Kodi Version](https://img.shields.io/badge/Kodi-v20%2B%20(Nexus%2FOmega)-blue.svg?style=flat-square&logo=kodi)](https://kodi.tv)
[![Platform](https://img.shields.io/badge/Platform-All-lightgrey.svg?style=flat-square)]()

<div align="center">

---

## Overview
**Anubis** is an automated subtitle-fetching daemon for Kodi meant to be used in conjunction with Otaku. When you play a video, Anubis inspects Kodi's active player metadata, maps the show title and episode number using the **AniList** and **AniZip** APIs to resolve exact **TVDB/TMDB** keys, and uses **Subliminal** to automatically pull and apply matching English subtitles in real time. This add-on is only useful if Otaku's video streams don't come with subtitles or if you are getting wrong subtitles for the episode you are watching. 

**IN ORDER TO KEEP THIS REPOSITORY OPEN SOURCE, AS OF NOW THE ONLY SUBTITLE PROVIDERS MY SCRAPER USES ARE PODNAPISI AND TVSUBTITLES. HARDCODED API KEYS MAY BE PUT IN LATER FOR ACCESS TO BETTER SCRAPERS BUT FOR NOW THOSE TWO ARE THE ONLY ONES WITHOUT STRICT API RATE-LIMITERS AND REST API THAT REQUIRE API TOKENS.**

---

## Installation 

1. Enable **"Unknown Sources"** in Kodi's system settings (`Settings` > `System` > `Add-ons`). 
2. Go to Kodi's **File Manager** and select **Add Source**. 
3. Enter the following repository URL: `https://boogiedude243261-beep.github.io/Anubis/` 
4. Name the media source **Anubis** and click **OK**. 
5. Return to the main menu, select **Add-ons**, and click **Install from Zip File**. 
6. Select **Anubis** from the list, choose `anubis-1.0.0.zip` (or `Anubis-1.0.0.zip`), and install.


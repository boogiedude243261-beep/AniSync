import json
import threading
import urllib
import urllib.request 
import xbmcvfs
import xbmcgui
import sys
import os
import xbmc
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'lib'))
from subliminal import region, list_subtitles, download_subtitles
from subliminal.video import Episode
from babelfish import Language
region.configure('dogpile.cache.memory')
def log_msg(msg, is_error=True): #AI COMPLETELY
    level = xbmc.LOGERROR if is_error else xbmc.LOGINFO
    xbmc.log(f"[SubScript] {msg}", level=level)
def anilist(search_title): #HUMAN CODED
    url = "https://graphql.anilist.co"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Test1" }
    query = """
    { Media(search:"TITLE", type: ANIME){
        id
        title {
          english
          romaji
        }
      }
    }
    """
    try:
        req = urllib.request.Request(url=url, data=json.dumps({"query": query.replace("TITLE", search_title)}).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        log_msg(f"AniList API request failed for '{search_title}': {e}")
        return {}
def anizip(id): #HUMAN CODED
    if not id:
        return {}
    url = f"https://api.ani.zip/mappings?anilist_id={id}"
    headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Test1" }
    try:
        req = urllib.request.Request(url=url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        log_msg(f"AniZip API request failed for ID '{id}': {e}")
        return {}

def subliminal1(title, season, episode, seriestvdbid, tvdbid): #HUMAN REVIEWED 
    if not title:
        log_msg("subliminal1 missing series title.")
        return None
    try:
        season = int(season) if season is not None else 1
        episode = int(episode) if episode is not None else 1
    except (ValueError, TypeError) as e:
        log_msg(f"Invalid season/episode format: season={season}, episode={episode}. Error: {e}")
        season, episode = 1, 1
    episodeData = {
        "series": title,
        "season": season,
        "episode": episode }
    if seriestvdbid:
        episodeData["series_tvdb_id"] = seriestvdbid
    if tvdbid:
        episodeData["tvdb_id"] = tvdbid
    video = Episode(**episodeData)
    try:
        subs = list_subtitles([video], {Language('eng')}, providers=['podnapisi', 'tvsubtitles'])
    except Exception as e:
        log_msg(f"Subliminal list_subtitles search failed: {e}")
        return None
    vidsubs = subs.get(video, [])
    if not vidsubs:
        log_msg(f"No subtitles found for {title} S{season:02d}E{episode:02d}")
        return None
    bestvidsub = vidsubs[0]
    try:
        download_subtitles([bestvidsub])
    except Exception as e:
        log_msg(f"Failed to download selected subtitle: {e}")
        return None
    if not getattr(bestvidsub, 'content', None):
        log_msg("Downloaded subtitle object is empty.")
        return None
    try:
        temp_dir = xbmcvfs.translatePath('special://temp/')
        sub_filename = f"{title.replace(' ', '_')}_S{season:02d}E{episode:02d}.srt"
        sub_path = os.path.join(temp_dir, sub_filename)
        with open(sub_path, 'wb') as f:
            f.write(bestvidsub.content)
        return sub_path
    except Exception as e:
        log_msg(f"Failed writing subtitle file to disk: {e}")
        return None
def metadata(): #AI COMPLETELY
    """Fetches the player data and returns it as a dictionary."""
    tag = xbmc.Player().getVideoInfoTag()
    title = tag.getTVShowTitle() or xbmc.getInfoLabel('VideoPlayer.TVShowTitle') or tag.getTitle() or xbmc.getInfoLabel('VideoPlayer.Title')
    episode = tag.getEpisode()
    if not episode or episode < 1:
        try: 
            episode = int(xbmc.getInfoLabel('VideoPlayer.Episode'))
        except ValueError: 
            episode = 1
    return {
        "title": title.strip() if title else "",
        "episode": episode }
################ EXECUTION ###############
def fetchsub(): #HUMAN CODED
    try:
        existing_subs = xbmc.Player().getAvailableSubtitleStreams()
        if existing_subs and len(existing_subs) > 0:
            log_msg(f"Stream already has {len(existing_subs)} native subtitle track(s). Daemon backing off.", is_error=False)
            return
    except Exception as e:
        log_msg(f"Could not check existing subtitle streams: {e}")
    data = metadata()
    inp_title = data.get("title")
    if not inp_title:
        log_msg("Could not retrieve video title from Kodi player.")
    else: 
        anilist_data = anilist(inp_title)
        id = anilist_data.get("data", {}).get("Media", {}).get("id")
        if not id:
            log_msg(f"AniList returned no media ID for '{inp_title}'.")
        else: 
            currentepisode = str(data.get("episode"))
            anime_data = anizip(id)
            episode = anime_data.get("episodes", {}).get(currentepisode, {}).get("episodeNumber")
            season = anime_data.get("episodes", {}).get(currentepisode, {}).get("seasonNumber")
            media_titles = anilist_data.get("data", {}).get("Media", {}).get("title", {})
            title = (
                media_titles.get("english")
                or anime_data.get("titles", {}).get("en")
                or media_titles.get("romaji")
                or inp_title )
            if episode == None:
                episode = anime_data.get("episodes", {}).get(currentepisode, {}).get("episode")
            tvdbseries = anime_data.get("episodes", {}).get(currentepisode, {}).get("tvdbShowId")
            tvdbid = anime_data.get("episodes", {}).get(currentepisode, {}).get("tvdbId")
            srt = subliminal1(title, season, episode, tvdbseries, tvdbid)
            if srt:
                if xbmc.Player().isPlayingVideo():
                    xbmc.Player().setSubtitles(srt)
                    xbmcgui.Dialog().notification("Subtitles", "Downloaded and applied successfully", xbmcgui.NOTIFICATION_INFO, 3000)
class OtakuPlayerMonitor(xbmc.Player): #COMPLETELY AI FROM HERE DOWN
    def __init__(self):
        super().__init__()
    def onPlayBackStarted(self):
        xbmc.sleep(2000)
        try:
            playing_file = self.getPlayingFile()
            if "plugin.video.otaku" in playing_file:
                log_msg("Otaku playback detected. Fetching subtitles...", is_error=False)
                threading.Thread(target=fetchsub).start()
        except Exception as e:
            log_msg(f"Failed during playback check: {e}")
if __name__ == '__main__': 
    monitor = xbmc.Monitor()
    player = OtakuPlayerMonitor()
    log_msg("Anubis Daemon Started", is_error=False)
    while not monitor.abortRequested():
        if monitor.waitForAbort(10):
            break
            
    del player
    log_msg("Anubis Daemon Stopped", is_error=False)
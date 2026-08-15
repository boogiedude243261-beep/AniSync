import json
import xbmcgui
import urllib.request 
import urllib.error 
import xbmc
import urllib.parse

def query_anilist(search_title): 
    url = "https://graphql.anilist.co"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Test1"
    }
    query = """
    { Media(search:"TITLE", type: ANIME){
        title {
          english
        }
        id
        title {
          english 
        }
      }
    }
    """
    complete_query = query.replace("TITLE", search_title)
    end_query = {
        "query": complete_query
    }
    data = json.dumps(end_query).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")  
    try:
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode("utf-8")
            result = json.loads(response_body)
            return result.get("data", {}).get("Media")   
    except urllib.error.HTTPError as e:
        xbmc.log(f"HTTP Error {e.code}: {e.reason}", xbmc.LOGERROR)
    except urllib.error.URLError as e:
        xbmc.log(f"Connection Error: {e.reason}", xbmc.LOGERROR)
    return None 
def anizip_plugin(id): 
    url = f"https://api.ani.zip/mappings?anilist_id={id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Test1"
    }
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode("utf-8")
            return json.loads(response_body)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        xbmc.log(f"[OtakuMonitor] AniZip Error: {e}", xbmc.LOGERROR)
    return None
class OtakuPlayerObserver(xbmc.Player):
    def __init__(self):
        super(OtakuPlayerObserver, self).__init__()
        self.current_anilist_id = None
        self.current_episode = None
        self.current_title = None  
        self.is_playing_otaku = False
    def onPlayBackStarted(self):
        xbmc.sleep(2000) 
        anilist_id = xbmc.getInfoLabel('ListItem.Property(anilist_id)') or xbmc.getInfoLabel('ListItem.Property(item.info.anilist_id)')
        episode = xbmc.getInfoLabel('VideoPlayer.Episode')
        title = xbmc.getInfoLabel('VideoPlayer.TVShowTitle') or xbmc.getInfoLabel('VideoPlayer.Title')
        plugin_url = xbmc.getInfoLabel('Player.Filenameandpath') 
        xbmc.log(f"[OtakuMonitor Diag [START]] Raw Filenameandpath: {plugin_url}", xbmc.LOGWARNING)
        xbmc.log(f"[OtakuMonitor Diag [START]] Initial InfoLabel Season: {xbmc.getInfoLabel('VideoPlayer.Season')}", xbmc.LOGWARNING)
        xbmc.log(f"[OtakuMonitor Diag [START]] Initial InfoLabel Episode: {xbmc.getInfoLabel('VideoPlayer.Episode')}", xbmc.LOGWARNING)
        xbmc.log(f"[OtakuMonitor Diag [START]] Initial InfoLabel TVShowTitle: {xbmc.getInfoLabel('VideoPlayer.TVShowTitle')}", xbmc.LOGWARNING)
        xbmc.log(f"[OtakuMonitor Diag [START]] Initial InfoLabel Title: {xbmc.getInfoLabel('VideoPlayer.Title')}", xbmc.LOGWARNING)
        if 'plugin.video.otaku' in plugin_url or xbmc.getInfoLabel('Container.PluginName') == 'plugin.video.otaku':
            self.is_playing_otaku = True
            if '?' in plugin_url:
                parsed_url = urllib.parse.urlparse(plugin_url)
                params = dict(urllib.parse.parse_qsl(parsed_url.query))
                anilist_id = anilist_id or params.get('anilist_id') or params.get('id')
                episode = params.get('episode') or episode
                title = params.get('title') or params.get('name') or params.get('media_title') or title
            self.current_anilist_id = anilist_id
            self.current_episode = episode
            self.current_title = title
    def onPlayBackStopped(self):
        self._clear_data()
    def onPlayBackEnded(self):
        self._clear_data()
    def _clear_data(self):
        self.current_anilist_id = None
        self.current_episode = None
        self.current_title = None
        self.is_playing_otaku = False
if __name__ == "__main__":
    monitor = xbmc.Monitor()
    player = OtakuPlayerObserver()
    last_seen_identifier = None
    while not monitor.abortRequested():
        if player.isPlayingVideo() and player.is_playing_otaku:
            current_id = player.current_anilist_id
            current_ep = player.current_episode
            current_title = player.current_title
            if current_ep:
                base_id = current_id if current_id else current_title
                identifier = f"{base_id}_Ep{current_ep}"
                if identifier != last_seen_identifier:
                    anizip_data = None
                    if current_id:
                        xbmc.log(f"[OtakuMonitor] Primary Target Acquired: Native AniList ID {current_id}. Querying AniZip...", xbmc.LOGINFO)
                        anizip_data = anizip_plugin(current_id)
                    elif current_title:
                        xbmc.log(f"[OtakuMonitor] [BACKUP TRIGGERED] No AniList ID provided by Otaku. Falling back to fuzzy title search for: '{current_title}'", xbmc.LOGWARNING)
                        anilist_result = query_anilist(current_title)
                        if anilist_result:
                            fallback_id = anilist_result.get("id")
                            xbmc.log(f"[OtakuMonitor] [BACKUP SUCCESS] AniList found ID {fallback_id} for '{current_title}'. Querying AniZip...", xbmc.LOGINFO)
                            anizip_data = anizip_plugin(fallback_id)
                        else:
                            xbmc.log(f"[OtakuMonitor] [BACKUP FAILED] Could not find an AniList ID for title '{current_title}'.", xbmc.LOGERROR)
                    if anizip_data:
                        brick = anizip_data.get("episodes", {})
                        ep_data = None
                        try:
                            target_ep = int(current_ep)
                        except ValueError:
                            target_ep = str(current_ep)
                        for key, info in brick.items():
                            try:
                                k_val = int(key)
                            except ValueError:
                                k_val = key
                            if target_ep == k_val:
                                ep_data = info
                                break
                        if not ep_data:
                            for key, info in brick.items():
                                try:
                                    tvdb_ep = int(info.get("episodeNumber", -1))
                                except ValueError:
                                    tvdb_ep = -1
                                if target_ep == tvdb_ep:
                                    ep_data = info
                                    break
                        if ep_data:
                            tmdb_season = ep_data.get("seasonNumber")
                            tmdb_episode = ep_data.get("episodeNumber")
                            if tmdb_season is not None and tmdb_episode is not None:
                                tmdb_GEM = f"S{tmdb_season:02d}E{tmdb_episode:02d}"
                                xbmc.log(f"[OtakuMonitor] SUCCESS! Final Scraper Target: {tmdb_GEM}", xbmc.LOGINFO)
                                try: 
                                    current_path = xbmc.Player().getPlayingFile()
                                    current_tag = xbmc.Player().getVideoInfoTag()
                                    listitem = xbmcgui.ListItem(path=current_path) 
                                    video_tag = listitem.getVideoInfoTag() 
                                    video_tag.setTitle(current_tag.getTitle())
                                    video_tag.setTVShowTitle(current_tag.getTVShowTitle())
                                    video_tag.setSeason(int(tmdb_season)) 
                                    video_tag.setEpisode(int(tmdb_episode)) 
                                    video_tag.setMediaType('episode') 
                                    xbmc.Player().updateInfoTag(listitem) 
                                    active_tag = xbmc.Player().getVideoInfoTag() 
                                    xbmc.log(f"[OtakuMonitor Diag [POST]] InfoTag Season: {active_tag.getSeason()}", xbmc.LOGWARNING) 
                                    xbmc.log(f"[OtakuMonitor Diag [POST]] InfoTag Episode: {active_tag.getEpisode()}", xbmc.LOGWARNING) 
                                    xbmc.log("[OtakuMonitor] Successfully updated player metadata.", xbmc.LOGINFO)  
                                except Exception as e: 
                                    xbmc.log(f"[OtakuMonitor] Failed to update player metadata: {e}", xbmc.LOGERROR)
                            else:
                                xbmc.log(f"[OtakuMonitor] AniZip data found for episode {current_ep}, but TVDB mapping is missing.", xbmc.LOGWARNING)
                        last_seen_identifier = identifier
                else:
                    last_seen_identifier = None
        else:
            last_seen_identifier = None
        if monitor.waitForAbort(5):
            break


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
        xbmc.sleep(1000) 
        anilist_id = xbmc.getInfoLabel('ListItem.Property(anilist_id)')
        episode = xbmc.getInfoLabel('VideoPlayer.Episode')
        title = xbmc.getInfoLabel('VideoPlayer.TVShowTitle') or xbmc.getInfoLabel('VideoPlayer.Title')
        plugin_url = xbmc.getInfoLabel('Player.Filenameandpath') 
        
        if 'plugin.video.otaku' in plugin_url or xbmc.getInfoLabel('Container.PluginName') == 'plugin.video.otaku':
            self.is_playing_otaku = True
            if '?' in plugin_url:
                parsed_url = urllib.parse.urlparse(plugin_url)
                params = dict(urllib.parse.parse_qsl(parsed_url.query))
                if not anilist_id:
                    anilist_id = params.get('anilist_id') or params.get('id')
                if not episode:
                    episode = params.get('episode')
                if not title:
                    title = params.get('title') or params.get('name') or params.get('media_title')
                    
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
                        xbmc.log(f"[OtakuMonitor] Found AniList ID directly: {current_id}. Querying AniZip...", xbmc.LOGINFO)
                        anizip_data = anizip_plugin(current_id)
                    elif current_title:
                        xbmc.log(f"[OtakuMonitor] No AniList ID found. Falling back to search title: '{current_title}'", xbmc.LOGINFO)
                        anilist_result = query_anilist(current_title)
                        if anilist_result:
                            fallback_id = anilist_result.get("id")
                            xbmc.log(f"[OtakuMonitor] AniList found ID {fallback_id} for '{current_title}'. Querying AniZip...", xbmc.LOGINFO)
                            anizip_data = anizip_plugin(fallback_id)
                            
                    if anizip_data:
                        brick = anizip_data.get("episodes", {})
                        ep_data = brick.get(str(current_ep), {})
                        if ep_data:
                            tmdb_season = ep_data.get("tvdbSeason")
                            tmdb_episode = ep_data.get("tvdbEpisode")
                            
                            if tmdb_season is not None and tmdb_episode is not None:
                                tmdb_GEM = f"S{tmdb_season:02d}E{tmdb_episode:02d}"
                                xbmc.log(f"[OtakuMonitor] SUCCESS! Final Scraper Target: {tmdb_GEM}", xbmc.LOGINFO)
                                try:
                                    listitem = xbmcgui.ListItem()
                                    listitem.setInfo('video', {
                                        'season': int(tmdb_season),
                                        'episode': int(tmdb_episode),
                                        'mediatype': 'episode'
                                    })
                                    xbmc.Player().updateInfoTag(listitem)
                                    xbmc.log("[OtakuMonitor] Successfully updated player metadata with TMDB layout.", xbmc.LOGINFO) 
                                except Exception as e:
                                    xbmc.log(f"[OtakuMonitor] Failed to update player metadata: {e}", xbmc.LOGERROR)
                            else:
                                xbmc.log(f"[OtakuMonitor] AniZip data found for episode {current_ep}, but TVDB mapping is missing.", xbmc.LOGWARNING)
                                
                    last_seen_identifier = identifier
        else:
            last_seen_identifier = None
            
        if monitor.waitForAbort(5):
            break
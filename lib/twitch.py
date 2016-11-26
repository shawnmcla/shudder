import requests
import time
from lib.cfg import config

"""Twitch API module

Contains various methods making calls to the Twitch API
"""

#HTTP Header to send with API requests.
_headers = {'Client-ID' : config['apiKey']}

_mods = {}
_followers = []
_lastCacheRefresh = None

def _validateModCache():
    """Validate the mod cache.
    
    If the time elapsed since the last cache clear is greater
    than the time specified as privilegeCacheTimeout in the config,
    clear the mod cache.

    Returns True if the cache was still valid, False otherwise.
    """
    global _lastCacheRefresh
    if _lastCacheRefresh == None or (time.time() - _lastCacheRefresh) > config['modCacheTimeout']*60:
        _mods.clear()
        _lastCacheRefresh = time.time()
        return False
    return True

def _get_cached_follower(userName):
    """Verify if the user has a cached follower status.
    
    If the user is in the cache, returns a boolean indicating
    whether or not they are a follower.

    If the cache was expired or the user was not present, return None
    """
    if userName in _followers:
        return True
    return False

def _get_cached_mod(userName):
    """Verify if the user has a cached moderator status.
    
    If the user is in the cache, returns a boolean indicating
    whether or not they are a moderator.

    If the cache was expired or the user was not present, return None
    """
    if _validateModCache():
        if userName in _mods:
            return _mods[userName]
    return None

#GET /users/:user/follows/channels/:target
def is_follower(userName):
    """Verify if user is a follower of the channel.
    
    The caches will be verified first to avoid unnecessary
    repeated API calls and reduce load.
    """
    cacheStatus = _get_cached_follower(userName)
    if cacheStatus != False:
        return cacheStatus
    else:
        url = config['apiUrl']+"users/{}/follows/channels/{}".format(userName, config['channelName'])
        r = requests.get(url, headers=_headers)
        json = r.json()
        isFollower = "created_at" in json
        if isFollower:
            _followers.append(userName)
        return isFollower

def is_mod(userName):
    """Verify if user is a moderator of the channel.
    
    The caches will be verified first to avoid unnecessary
    repeated API calls and reduce load.
    """
    cacheStatus = _get_cached_mod(userName)
    if cacheStatus != None:
        return cacheStatus
    else:
        url = "https://tmi.twitch.tv/group/user/{}/chatters".format(config['channelName'])
        r = requests.get(url)
        json = r.json()
        isMod = userName in json["chatters"]["moderators"]
        _mods[userName] = isMod
        return isMod

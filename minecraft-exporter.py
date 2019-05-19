from prometheus_client.core import GaugeMetricFamily, REGISTRY, Counter
from prometheus_client import start_http_server
import requests
import json
import os
import functools
import re
import NBTparser
from signal import pause

# load config file
CONFIG = json.loads(open('config.json', 'r').read())
STATS_DIR = CONFIG['world_dir'] + "/stats"
PLAYER_DIR = CONFIG['world_dir'] + "/playerdata"
GROUPS = CONFIG['custom_groups']


@functools.lru_cache()
def uuid_to_username(uuid):
    resp = requests.get('https://sessionserver.mojang.com/session/minecraft/profile/' + uuid.replace('-', ''))
    name = json.loads(resp.content)['name']
    return name

def handle_groups(k1, k2, stats):
    for gname in GROUPS.keys():
        if k1 in GROUPS[gname].keys():
            for regex in GROUPS[gname][k1]:
                if re.fullmatch(regex, k2.replace('minecraft:','')) is not None:
                    if gname not in stats['group'].keys():
                        stats['group'][gname] = 0
                    stats['group'][gname] += stats[k1][k2]

def handle_stats(players):
    # finds the stats file for each player
    files = os.listdir(STATS_DIR)
    # loop through players
    for f in files:
        player_stats = json.loads(open(os.path.join(STATS_DIR, f), 'r').read())['stats']
        stats = {}
        # find their username
        uuid = os.path.splitext(f)[0]
        name = uuid_to_username(uuid)
        players[name] = stats

        stats['group'] = {}

        for k1 in player_stats.keys():
            if not k1 in stats.keys():
                # if a stat is not already in the global list, add it
                stats[k1] = {}
                # add an 'all' subcategory if one does not exist already
                if not 'all' in stats[k1]:
                    stats[k1]['all'] = 0
            for k2 in player_stats[k1]:
                # add stat to global list if not already there
                if k2 not in stats[k1].keys():
                    stats[k1][k2] = 0
                # sum stat with global list
                stats[k1][k2] += player_stats[k1][k2]
                stats[k1]['all'] += player_stats[k1][k2]
                handle_groups(k1, k2, stats)

def handle_nbt(players):
    files = os.listdir(PLAYER_DIR)
    for f in files:
        player_nbt = NBTparser.read_nbt(os.path.join(PLAYER_DIR, f))
        uuid = os.path.splitext(f)[0]
        name = uuid_to_username(uuid)
        nbt = {}
        players[name]['nbt'] = nbt
        for tag in CONFIG['nbt_exports']:
            if tag in player_nbt:
                if type(player_nbt[tag]) in [list, dict]:
                    nbt[tag] = len(player_nbt[tag])
                else:
                    nbt[tag] = player_nbt[tag]

class MinecraftMetricCollector(object):
    def collect(self):
        # create stats storage for each player
        players = {}
    
        handle_stats(players)

        if CONFIG['nbt']:
            handle_nbt(players)

        # generate exports
        metrics = {}
        for player in players:
            for k1 in players[player].keys():
                for k2 in players[player][k1].keys():
                    name = 'minecraft_{}_{}'.format(k1, k2)
                    name = name.replace('minecraft:','')
                    if name not in metrics:
                        stat = GaugeMetricFamily(name, 'a minecraft statistic', labels=["player"])
                        metrics[name] = stat
                    else:
                        stat = metrics[name]
                    value = int(players[player][k1][k2])
                    stat.add_metric([player], value)

        for metric in metrics:
            yield metrics[metric]

REGISTRY.register(MinecraftMetricCollector())

start_http_server(8000)

# suspend the program indefinitely so the exporter can run in the background
pause()

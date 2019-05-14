from prometheus_client.core import CounterMetricFamily, REGISTRY, Counter
from prometheus_client import start_http_server
import requests
import json
import os
import functools
from signal import pause

# replace this with the path to the world which you intend to export metrics from
STATS_DIR='REPLACE-ME-TO-SAVE/stats'


@functools.lru_cache()
def uuid_to_username(uuid):
    resp = requests.get('https://sessionserver.mojang.com/session/minecraft/profile/' + uuid.replace('-', ''))
    name = json.loads(resp.content)['name']
    return name


class MinecraftMetricCollector(object):
    def collect(self):
        # finds the stats file for each player
        files = os.listdir(STATS_DIR)
        # create stats storage for each player
        players = {}
        # loop through players
        for f in files:
            player = json.loads(open(STATS_DIR + '/' + f,'r').read())['stats']
            stats = {}
            # find their username
            uuid = os.path.splitext(f)[0]
            name = uuid_to_username(uuid)
            players[name] = stats
            for k1 in player.keys():
                if not k1 in stats.keys():
                    # if a stat is not already in the global list, add it
                    stats[k1] = {}
                    # add an 'all' subcategory if one does not exist already
                    if not 'all' in stats[k1]:
                        stats[k1]['all'] = 0
                for k2 in player[k1]:
                    # add stat to global list if not already there
                    if k2 not in stats[k1].keys():
                        stats[k1][k2] = 0
                    # sum stat with global list
                    stats[k1][k2] += player[k1][k2]
                    stats[k1]['all'] += player[k1][k2]


        # generate exports
        for player in players:
            stats = players[player]
            for k1 in stats.keys():
                for k2 in stats[k1].keys():
                    name = 'minecraft_{}_{}'.format(k1, k2)
                    name = name.replace('minecraft:','')
                    value = int(stats[k1][k2])
                    stat = CounterMetricFamily(name, 'a minecraft statistic', labels=["player"])
                    stat.add_metric([player], value)
                    yield stat

REGISTRY.register(MinecraftMetricCollector())

start_http_server(8000)

# suspend the program indefinitely so the exporter can run in the background
pause()

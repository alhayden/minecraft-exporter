from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server
import json, os
from signal import pause

STATS_DIR='PATH-TO-WORLD-SAVE/stats'

class MinecraftMetricCollector(object):
    def collect(self):
        files = os.listdir(STATS_DIR)
        stats = {}
        for f in files:
            player = json.loads(open(STATS_DIR + '/' + f,'r').read())['stats']
            for k1 in player.keys():
                if not k1 in stats.keys():
                    stats[k1] = {}
                    if not 'all' in stats[k1]:
                        stats[k1]['all'] = 0
                for k2 in player[k1]:
                    if k2 not in stats[k1].keys():
                        stats[k1][k2] = 0
                    stats[k1][k2] += player[k1][k2]
                    stats[k1]['all'] += player[k1][k2]


        for k1 in stats.keys():
            for k2 in stats[k1].keys():
                name = 'minecraft_' + k1 + '_' + k2
                name = name.replace('minecraft:','')
                value = int(stats[k1][k2])
                yield GaugeMetricFamily(name, 'a minecraft statistic', value)

REGISTRY.register(MinecraftMetricCollector())

start_http_server(8000)


pause()

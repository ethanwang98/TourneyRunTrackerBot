from pysmashgg import SmashGG, tournaments, api, filters
from custom_start_gg_queries import *

import time


class StartGG(SmashGG):
    def __init__(self, key):
        SmashGG.__init__(self, key)

    def tournament_show_sets(self, tournament_name: str, event_name: str, page_num: int) -> dict:
        data = {}
        event_id = tournaments.get_event_id(tournament_name, event_name, self.header, self.auto_retry)
        variables = {"eventId": event_id, "page": page_num, "filters": {"updatedAfter": int(time.time()) - 70, "state": 3}}
        response = api.run_query(SHOW_SETS_WITH_SEED_QUERY, variables, self.header, self.auto_retry)
        sets = filters.show_sets_filter(response)

        # adding seed to data
        if sets is not None:
            nodes = response['data']['event']['sets']['nodes']
            for i in range(len(sets)):
                if len(nodes[i]['slots']) < 2:
                    continue  # This fixes a bug where player doesn't have an opponent
                if nodes[i]['slots'][0]['entrant'] is None or nodes[i]['slots'][1]['entrant'] is None:
                    continue  # This fixes a bug when tournament ends early

                sets[i]['entrant1Seed'] = nodes[i]['slots'][0]['entrant']['initialSeedNum']
                sets[i]['entrant2Seed'] = nodes[i]['slots'][1]['entrant']['initialSeedNum']

        data['sets'] = sets
        data['complete'] = response['data']['event']['state'] == 'COMPLETED'
        return data

    def show_event_metadata(self, tournament_name: str, event_name: str) -> dict or None:
        data = None
        variables = {"tourneySlug": tournament_name}
        response = api.run_query(SHOW_EVENT_METADATA, variables, self.header, self.auto_retry)

        if response['data']['tournament'] is None:
            return

        if event_name is not None:
            for event in response['data']['tournament']['events']:
                if event['slug'].split("/")[-1] == event_name:
                    data = {'tourney_name': response['data']['tournament']['name'], 'event_name': event['name'],
                            'event_id': event['id'], 'complete': event['state'] == 'COMPLETED'}
                    break
        else:
            data = {'tourney_name': response['data']['tournament']['name'], 'event_name': response['data']['tournament']['events'][0]['name'],
                    'event_id': response['data']['tournament']['events'][0]['id'], 'complete': response['data']['tournament']['events'][0]['state'] == 'COMPLETED'}

        return data

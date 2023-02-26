from pysmashgg import SmashGG, tournaments, api, filters
from custom_start_gg_queries import *


class StartGG(SmashGG):
    def __init__(self, key):
        SmashGG.__init__(self, key)

    def tournament_show_sets(self, tournament_name, event_name, page_num):
        event_id = tournaments.get_event_id(tournament_name, event_name, self.header, self.auto_retry)
        variables = {"eventId": event_id, "page": page_num}
        response = api.run_query(SHOW_SETS_WITH_SEED_QUERY, variables, self.header, self.auto_retry)
        data = filters.show_sets_filter(response)

        # adding seed to data
        if data is not None:
            nodes = response['data']['event']['sets']['nodes']
            for i in range(len(data)):
                if len(nodes[i]['slots']) < 2:
                    continue  # This fixes a bug where player doesn't have an opponent
                if nodes[i]['slots'][0]['entrant'] is None or nodes[i]['slots'][1]['entrant'] is None:
                    continue  # This fixes a bug when tournament ends early

                data[i]['entrant1Seed'] = nodes[i]['slots'][0]['entrant']['initialSeedNum']
                data[i]['entrant2Seed'] = nodes[i]['slots'][1]['entrant']['initialSeedNum']

        return data

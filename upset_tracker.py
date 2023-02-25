from discord.ext import tasks
from start_gg import StartGG

from math import log, floor, ceil


class UpsetTracker:

    def __init__(self, tourney: str, event: str, startgg_client: StartGG):
        self._tourney = tourney
        self._event = event
        self._startgg_client = startgg_client
        self._sets_processed = {}
        self._current_page = 1

        self.check_for_tourney_updates.start()

    @tasks.loop(seconds=60)
    async def check_for_tourney_updates(self):
        if len(self._sets_processed.keys()) >= 18:
            self._current_page += 1

        for tourney_set in self._startgg_client.tournament_show_sets(self._tourney, self._event, self._current_page):
            if tourney_set['id'] not in self._sets_processed and tourney_set['completed']:
                pass # check if there was an upset here

    def _calculate_upset_factor(self, seed_1: int, seed_2: int) -> int:
        """Uses the upset factor formula used on PGStats"""
        return abs(self._calculate_losers_rounds_to_victory(seed_1) - self._calculate_losers_rounds_to_victory(seed_2))

    def _calculate_losers_rounds_to_victory(self, seed: int) -> int:
        if seed == 1:
            return 0

        return floor(log(seed - 1, 2)) + ceil(log(seed * (2 / 3), 2))

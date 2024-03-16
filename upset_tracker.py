from discord.ext import tasks
from start_gg import StartGG

from math import log, floor, ceil
import logging


class UpsetTracker:

    def __init__(self, tourney: str, event: str, tourney_name: str, event_name: str, startgg_client: StartGG, channel: 'discord channel'):
        self._tourney = tourney
        self._event = event
        self._tourney_name = tourney_name
        self._event_name = event_name
        self._startgg_client = startgg_client
        self._channel = channel
        self._minutes_since_last_change = 0
        self._logger = logging.getLogger()
        self.complete = False

        self.check_for_tourney_updates.start()

    @tasks.loop(seconds=60)
    async def check_for_tourney_updates(self):
        """Checks for newly completed tournament sets every 60 seconds"""
        current_page = 1

        while True:
            sets_dict = self._startgg_client.tournament_show_sets(self._tourney, self._event, current_page)
            sets_num = len(sets_dict['sets'])

            if current_page == 1 and sets_num == 0:
                self._minutes_since_last_change += 1
            elif sets_num == 0:
                # should only occur if the last page had exactly 18 sets
                return
            else:
                self._minutes_since_last_change = 0

            if sets_dict['complete'] or self._minutes_since_last_change >= 2880:
                self.complete = True
                await self._channel.send("Event {} in {} is complete and upset tracking has stopped.".format(self._event_name, self._tourney_name))
                self.check_for_tourney_updates.cancel()
                return

            await self._send_upset_messages(sets_dict['sets'])

            # if less than 18 sets, it was the last page; otherwise go to the next page
            if sets_num < 18:
                return
            current_page += 1

    async def _send_upset_messages(self, sets: dict) -> None:
        """Checks if the lower seed won and sends messages to the Discord channel if so"""
        for tourney_set in sets:
            self._logger.info("Set completed: {} - {}".format(tourney_set['entrant1Name'], tourney_set['entrant2Name']))
            if tourney_set['winnerId'] == tourney_set['entrant1Id'] and tourney_set['entrant1Seed'] > tourney_set['entrant2Seed'] and tourney_set['entrant2Score'] > -1:
                upset_factor = self._calculate_upset_factor(tourney_set['entrant1Seed'], tourney_set['entrant2Seed'])
                if upset_factor > 0:
                    await self._channel.send(
                        "UPSET in {} {}: {} {} - {} {}, Upset Factor: {}".format(self._tourney_name, self._event_name,
                                                                                 tourney_set['entrant1Name'],
                                                                                 tourney_set['entrant1Score'],
                                                                                 tourney_set['entrant2Score'],
                                                                                 tourney_set['entrant2Name'],
                                                                                 upset_factor))
            elif tourney_set['winnerId'] == tourney_set['entrant2Id'] and tourney_set['entrant2Seed'] > tourney_set['entrant1Seed'] and tourney_set['entrant1Score'] > -1:
                upset_factor = self._calculate_upset_factor(tourney_set['entrant1Seed'], tourney_set['entrant2Seed'])
                if upset_factor > 0:
                    await self._channel.send(
                        "UPSET in {} {}: {} {} - {} {}, Upset Factor: {}".format(self._tourney_name, self._event_name,
                                                                                 tourney_set['entrant2Name'],
                                                                                 tourney_set['entrant2Score'],
                                                                                 tourney_set['entrant1Score'],
                                                                                 tourney_set['entrant1Name'],
                                                                                 upset_factor))

    def _calculate_upset_factor(self, seed_1: int, seed_2: int) -> int:
        """Uses the upset factor formula used on PGStats"""
        return abs(self._calculate_losers_rounds_to_victory(seed_1) - self._calculate_losers_rounds_to_victory(seed_2))

    def _calculate_losers_rounds_to_victory(self, seed: int) -> int:
        if seed == 1:
            return 0

        return floor(log(seed - 1, 2)) + ceil(log(seed * (2 / 3), 2))

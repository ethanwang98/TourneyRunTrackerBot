import discord
from discord.ext import commands
from upset_tracker import UpsetTracker
from start_gg import StartGG


class TrackerBot(commands.Bot):

    def __init__(self, startgg_token: str):
        self._upset_tournies = {}
        self._startgg_token = startgg_token
        self._startgg_client = StartGG(startgg_token)

        intents = discord.Intents.default()
        intents.message_content = True

        commands.Bot.__init__(self, command_prefix='!', intents=intents, help_command=None)
        self.add_commands()

    def add_commands(self):
        @self.command(name="upset", pass_context=True)
        async def upset(ctx, arg1, arg2):
            if self._check_if_tourney_and_event_exists(arg1, arg2):
                self._upset_tournies[arg1] = UpsetTracker(arg1, arg2, self._startgg_client)
                await ctx.channel.send("Now tracking upsets for event " + arg2 + " in tournament " + arg1)
            else:
                await ctx.channel.send("Unable to find event in tourney. Please check your spelling or type !help for help on formatting.")

        @self.command(name="help", pass_context=True)
        async def bot_help(ctx):
            await ctx.channel.send("Upset tracker format: !upset {tourney name} {tourney event}")

        @self.command(name="test", pass_context=True)
        async def test_query(ctx):
            print(self._startgg_client.tournament_show_sets("game-lab-smash-80-singles-bys-new-beer-release-jel", "game-lab-smash-80-singles", 1))

    def _check_if_tourney_and_event_exists(self, tourney: str, event: str):
        return self._startgg_client.tournament_show_event_id(tourney, event) is not None
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
            event_id = self._startgg_client.tournament_show_event_id(arg1, arg2)
            if event_id is not None and event_id not in self._upset_tournies:
                self._upset_tournies[event_id] = UpsetTracker(arg1, arg2, self._startgg_client, ctx.channel)
                await ctx.channel.send("Now tracking upsets for event " + arg2 + " in tournament " + arg1)
            elif event_id is not None and event_id in self._upset_tournies:
                await ctx.channel.send("Bot is already tracking this event")
            else:
                await ctx.channel.send("Unable to find event in tourney. Please check your spelling or type !help for help on formatting.")

        @self.command(name="untrackupset", pass_context=True)
        async def untrack_upset(ctx, arg1, arg2):
            event_id = self._startgg_client.tournament_show_event_id(arg1, arg2)
            if event_id is not None and event_id in self._upset_tournies:
                del self._upset_tournies[event_id]
                await ctx.channel.send("Stopped tracking upsets for event " + arg2 + " in tournament " + arg1)
            elif event_id is not None and event_id not in self._upset_tournies:
                await ctx.channel.send("Bot is not currently tracking this event")
            else:
                await ctx.channel.send("Unable to find event in tourney. Please check your spelling or type !help for help on formatting.")

        @self.command(name="help", pass_context=True)
        async def bot_help(ctx):
            await ctx.channel.send("To track upsets: !upset {tourney name} {tourney event}\n" +
                                   "To untrack upsets: !untrackupset {tourney name} {tourney event}")

        @self.command(name="test", pass_context=True)
        async def test_query(ctx):
            print(self._startgg_client.tournament_show_sets("sync-up-saturdays-99", "ultimate-singles", 1))

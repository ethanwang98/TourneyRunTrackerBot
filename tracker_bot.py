import discord
from discord.ext import commands, tasks
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

    async def on_ready(self):
        self.check_for_completed_tournies.start()

    def add_commands(self):
        @self.command(name="upset", pass_context=True)
        async def upset(ctx, arg1, arg2=None):
            event_data = self._startgg_client.show_event_metadata(arg1, arg2)
            if event_data is not None:
                if event_data['event_id'] not in self._upset_tournies and not event_data['complete']:
                    self._upset_tournies[event_data['event_id']] = UpsetTracker(arg1, arg2, event_data['tourney_name'], event_data['event_name'], self._startgg_client, ctx.channel)
                    await ctx.channel.send("Now tracking upsets for {} in event {}".format(event_data['tourney_name'], event_data['event_name']))
                elif event_data['event_id'] in self._upset_tournies:
                    await ctx.channel.send("Bot is already tracking this event")
                else:
                    await ctx.channel.send("Unable to track upsets for event {} in {}; event is already complete.".format(event_data['event_name'], event_data['tourney_name']))
            else:
                await ctx.channel.send("Unable to find event in tourney. Please check your spelling or type !help for help on formatting.")

        @self.command(name="untrackupset", pass_context=True)
        async def untrack_upset(ctx, arg1, arg2):
            event_data = self._startgg_client.show_event_metadata(arg1, arg2)
            if event_data is not None:
                if event_data['event_id'] in self._upset_tournies:
                    del self._upset_tournies[event_data['event_id']]
                    await ctx.channel.send("Stopped tracking upsets for event {} in {}".format(event_data['event_name'], event_data['tourney_name']))
                else:
                    await ctx.channel.send("Bot is not currently tracking this event")
            else:
                await ctx.channel.send("Unable to find event in tourney. Please check your spelling or type !help for help on formatting.")

        @self.command(name="help", pass_context=True)
        async def bot_help(ctx):
            await ctx.channel.send("To track upsets: !upset {tourney name} {tourney event}\n" +
                                   "To untrack upsets: !untrackupset {tourney name} {tourney event}")

        @self.command(name="test", pass_context=True)
        async def test_query(ctx):
            print(self._startgg_client.show_event_metadata("sync-up-saturdays-99", "ultimate-singles"))

    @tasks.loop(seconds=30)
    async def check_for_completed_tournies(self):
        completed_upset_tournies = [k for k in self._upset_tournies.keys() if self._upset_tournies[k].complete]
        for tourney in completed_upset_tournies:
            del self._upset_tournies[tourney]

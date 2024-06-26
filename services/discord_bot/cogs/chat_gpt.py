from discord.ext.commands import Context, command

from services.discord_bot.botty import Botty
from services.discord_bot.cogs.generic_cog import GenericCog
from services.discord_bot.config import CONFIG


class ChatGPT(GenericCog):
    def __init__(self, bot: Botty):
        self.bot = bot
        if not hasattr(self.bot, "openai_client"):
            self.bot.logger.error("Attempting to use ChatGPT Cog without openai_client")
            raise AttributeError("Attempting to use ChatGPT Cog without openai_client")

    @command(name="explain")
    async def explain(self, context: Context):
        if not CONFIG.chatgpt_roles & {role.name for role in context.author.roles}:
            self.bot.logger.info("Unauthorized call to !explain by %s", context.author.name)
            await context.message.reply("Sorry, You are not currently authorized to use this command.")
        elif context.message.reference is None:
            self.bot.logger.info("Misuse of !explain command by %s: Not a reply.", context.author.name)
            await context.message.reply("This command only works in reply to another message.")
        else:
            reference_message = await context.channel.fetch_message(context.message.reference.message_id)
            response = self.bot.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize content you are provided with for a fifth-grade student."
                        " Use the same language as the input text.",
                    },
                    {"role": "user", "content": reference_message.content},
                ],
                temperature=0,
                max_tokens=1024,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            await context.message.reply(
                f"{context.author.mention}, here is a summarized and simplified version of the message:\n"
                f"{response.choices[0].message.content}"
            )
            self.bot.logger.debug("Successful use of !explain on message %s", context.message.reference.message_id)

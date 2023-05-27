from .madlib import madlib


async def setup(bot):
    await bot.add_cog(madlib(bot))
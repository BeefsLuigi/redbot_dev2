from .chohan import chohan


async def setup(bot):
    await bot.add_cog(chohan(bot))
from .madlib import madlib


def setup(bot):
    bot.add_cog(madlib(bot))
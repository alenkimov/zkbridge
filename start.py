import asyncio

from bot.worker import work

if __name__ == '__main__':
    asyncio.run(work())

#  logging
from pathlib import Path
import logging
import sys

from aiofile import async_open  # poetry add aiofile
from aiopath import AsyncPath  # poetry add aiopath


logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
async_log_file = 'frt_photo_share_asynclog.txt'
async_log_file = str(Path(sys.argv[0]).parent.absolute().joinpath('logs', async_log_file))


async def async_logging_to_file(message: str) -> None:
    """Asunc write log to file."""
    apath = AsyncPath(async_log_file)
    if await apath.exists() and await apath.is_file():  # rewrite to try
        mode_file_open: str = 'a+'

    elif not await apath.exists():
        mode_file_open: str = 'w+'

    else:
        logging.warning(f'Sorry, no log-file and can\'t create "{async_log_file}".')
        return None
    
    async with async_open(async_log_file, mode_file_open) as afp:
        await afp.write(f'{message}\n')


'''
from datetime import datetime
import traceback

from src.services.asynclogging import async_logging_to_file
await async_logging_to_file(f'\n500:\t{datetime.now()}\t{MSC500_DATABASE_CONNECT}\t{traceback.extract_stack(None, 2)[1][2]}')
'''

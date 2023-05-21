from pathlib import Path
import logging
import sys

from aiofile import async_open
from aiopath import AsyncPath


logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
async_log_file = 'frt_photo_share_asynclog.txt'
async_log_file = str(Path(sys.argv[0]).parent.absolute().joinpath('logs', async_log_file))


async def async_logging_to_file(message: str) -> None:
    apath = AsyncPath(Path(async_log_file).parent)
    await apath.mkdir(parents=True, exist_ok=True)
    if apath.exists() and apath.is_file():
        mode_file_open: str = 'a+'

    elif not apath.exists():
        mode_file_open: str = 'w+'

    else:
        logging.warning(f'Sorry, no log-file and can\'t create "{async_log_file}".')
        return None

    async with async_open(async_log_file, mode_file_open) as afp:
        await afp.write(f'{message}\n')

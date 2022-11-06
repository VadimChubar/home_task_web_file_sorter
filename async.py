import argparse
import asyncio
import re

from aiopath import AsyncPath
from aioshutil import copyfile


"""
--source [-s] 
--output [-o]
"""

parser = argparse.ArgumentParser(description='Sorting folder')
parser.add_argument("--source", "-s", help="Source folder", required=True)
parser.add_argument("--output", "-o", help="Output folder", default="Cleared Folder Async")

args = vars(parser.parse_args())

source = args.get("source")
output = args.get("output")
output_folder = AsyncPath(output)

CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "u", "ja", "je", "ji", "g")

TRANS = {}
for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()


def normalize(name: str) -> str:
    t_name = name.translate(TRANS)
    t_name = re.sub(r'\W', '_', t_name)
    return t_name


async def read_folder(path: AsyncPath) -> None:
    async for el in path.iterdir():
        if await el.is_dir():
            await read_folder(el)
        else:
            await copy_file(el)


async def copy_file(file: AsyncPath) -> None:
    ext = file.suffix
    new_path = output_folder / ext
    try:
        await new_path.mkdir(exist_ok=True, parents=True)
        await copyfile(file, new_path / normalize(file.name))
    except OSError as err:
        print(err)


if __name__ == '__main__':
    base_folder = AsyncPath(source)
    asyncio.run(read_folder(base_folder))

    print(f"Created new cleared folder '{output}'")
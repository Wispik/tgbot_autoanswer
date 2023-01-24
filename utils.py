from pathlib import Path
from settings import bot, DOWNLOAD_PATH


async def download_file(file_id: str):
    filename = file_id
    if file_id.endswith('.jpg'):
        file_id = file_id.split('.jpg')[0]
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    src = Path(DOWNLOAD_PATH, filename)
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file.getvalue())
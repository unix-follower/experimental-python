import asyncio
from pathlib import Path

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

from src.utils import fs_utils


async def fetch_page_data(
    session: aiohttp.ClientSession,
    url: str,
    semaphore: asyncio.Semaphore,
    failed_urls: list[str],
) -> str | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:152.0) Gecko/20100101 Firefox/152.0"
    }

    try:
        async with semaphore:  # Only lets X tasks pass through at a time
            print(f"Fetching {url}")
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status == 429 or response.status == 403:
                    print(f"Anti-bot triggered (Status {response.status}) for {url}")
                    failed_urls.append(url)
                    return None

                html = await response.text()

        soup = BeautifulSoup(html, "html.parser")
        target_form = soup.find("form", id="imageStatsThumbsRowForm")

        if not target_form:
            print(f"Target form is missing on {url}")
            failed_urls.append(url)
            return None

        images = target_form.find_all("img")
        if len(images) > 1:
            raise ValueError(
                "Ambiguous image selection: multiple images found in the target form"
            )

        [img] = images
        return img.get("data-original")
    except Exception as e:  # noqa: BLE001
        print(
            f"An error occured while fetching. Error Class: {type(e).__name__}. Details: {e}"
        )
        failed_urls.append(url)
        return None


async def fetch_images(data_dir: Path):
    df = pd.read_csv(data_dir / "GPU_UserBenchmarks.csv")
    df = df[["URL"]].drop_duplicates()
    print(df.head())

    failed_urls = []
    semaphore = asyncio.Semaphore(3)  # Limit to 5 concurrent requests
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_page_data(session, url, semaphore, failed_urls) for url in df["URL"]
        ]
        completed_tasks = await asyncio.gather(*tasks)

    print(f"completed_tasks: {completed_tasks}")
    output_path = data_dir / "GPU_UserBenchmarks_with_images.csv"
    pd.DataFrame(completed_tasks, columns=["ImageURL"]).dropna().to_csv(
        output_path, index=False
    )

    if len(failed_urls) > 0:
        print(f"failed_urls: {failed_urls}")
        output_path = data_dir / "GPU_UserBenchmarks_with_images-failed_urls.csv"
        pd.DataFrame(failed_urls, columns=["URL"]).to_csv(output_path, index=False)


if __name__ == "__main__":
    _, data_dir = fs_utils.get_data_dir()
    asyncio.run(fetch_images(data_dir))

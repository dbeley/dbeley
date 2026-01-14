import logging
import time
import argparse
from concurrent.futures import ThreadPoolExecutor
import pylast

logger = logging.getLogger()


def main():
    args = parse_args()
    start_time = time.time()
    network = pylast.LastFMNetwork(api_key=args.API_KEY, api_secret=args.API_SECRET)
    limit = args.rows * args.columns
    user = network.get_user(args.username)
    top_albums = user.get_top_albums(period=args.timeframe, limit=limit + 5)

    readme_content = """### Hi there 👋, I'm [dbeley](https://dbeley.ovh/en)!\n
![dbeley's github stats](./profile/stats.svg)\n
![dbeley's top languages](./profile/top-langs.svg)\n
![dbeley's pinned repositories](./profile/pin-readme-tools-github-readme-stats.svg)\n
### My most listened-to albums on [last.fm](https://www.last.fm/user/d_beley) over the past week\n
"""

    image_size = "16%"
    albums = [item.item for item in top_albums]

    def fetch_cover(album):
        try:
            return album.get_cover_image()
        except Exception as e:
            logger.warning(e)
            return None

    with ThreadPoolExecutor(max_workers=8) as executor:
        images = list(executor.map(fetch_cover, albums))

    correct_images = 0
    for album, image_url in zip(albums, images):
        if not image_url:
            continue
        readme_content += "[<img src='{}' width='{}' alt='{}'>]({})&nbsp;\n".format(
            image_url,
            image_size,
            f"{album.get_artist()} - {album.get_name()}".replace("'", ""),
            album.get_url(),
        )
        if correct_images > 1 and (correct_images + 1) % args.columns == 0:
            readme_content += "<br>\n"
        correct_images += 1
        if correct_images == limit:
            break
    with open("README.md", "w") as f:
        f.write(readme_content)
    logger.info("Runtime : %.2f seconds." % (time.time() - start_time))


def parse_args():
    format = "%(levelname)s :: %(message)s"
    parser = argparse.ArgumentParser(description="Python skeleton")
    parser.add_argument(
        "--debug",
        help="Display debugging information",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "--timeframe",
        "-t",
        help="Timeframe (Accepted values : 7day, 1month,\
                              3month, 6month, 12month, overall.\
                              Default : 7day).",
        type=str,
        default="7day",
    )
    parser.add_argument(
        "--rows",
        "-r",
        help="Number of rows (Default : 5).",
        type=int,
        default=5,
    )
    parser.add_argument(
        "--columns",
        "-c",
        help="Number of columns (Default : number of rows).",
        type=int,
    )
    parser.add_argument(
        "--username",
        "-u",
        help="Lastfm username.",
        type=str,
    )
    parser.add_argument("--API_KEY", help="Lastfm API key (optional).")
    parser.add_argument("--API_SECRET", help="Lastfm API secret (optional).")
    parser.set_defaults(disable_cache=False)
    args = parser.parse_args()
    if args.columns is None:
        args.columns = args.rows

    logging.basicConfig(level=args.loglevel, format=format)
    return args


if __name__ == "__main__":
    main()

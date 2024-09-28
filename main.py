import logging
import time
import argparse
import pylast

logger = logging.getLogger()
temps_debut = time.time()


def main():
    args = parse_args()
    network = pylast.LastFMNetwork(api_key=args.API_KEY, api_secret=args.API_SECRET)
    limit = args.rows * args.columns
    user = network.get_user(args.username)
    top_albums = user.get_top_albums(period=args.timeframe, limit=limit + 5)

    readme_content = """### Hi there 👋, I'm [dbeley](https://dbeley.ovh/en)!\n
![dbeley's github stats](https://github-readme-stats.vercel.app/api?username=dbeley)\n
### My most listened-to albums on [last.fm](https://www.last.fm/user/d_beley) over the past week\n
"""

    image_size = "16%"
    correct_images = 0
    for item in top_albums:
        album = item.item
        try:
            image_url = album.get_cover_image()
        except Exception as e:
            logger.warning(e)
            continue
        if not image_url:
            continue
        readme_content += (
            "[<img src='{}' width='{}' height='{}' alt='{}'>]({})&nbsp;\n".format(
                image_url,
                image_size,
                image_size,
                f"{album.get_artist()} - {album.get_name()}".replace("'", ""),
                album.get_url(),
            )
        )
        if correct_images > 1 and (correct_images + 1) % args.columns == 0:
            readme_content += "<br>\n"
        correct_images += 1
        if correct_images == limit:
            break
    with open("README.md", "w") as f:
        f.write(readme_content)
    logger.info("Runtime : %.2f seconds." % (time.time() - temps_debut))


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

    logging.basicConfig(level=args.loglevel, format=format)
    return args


if __name__ == "__main__":
    main()

"""
Plex Thumbnail Generator

This script will check your TV Show library for missing thumbnails and create them if needed.

Usage: python plex_thumbnail_generator.py -m MODE

where MODE is either "REPORT" or "CREATE".

In REPORT mode, the script will only print out which episodes have missing thumbnails.
In CREATE mode, the script will attempt to create thumbnails for episodes that are missing them.

Note: This script assumes that you have a configuration file called "config.conf" that contains
the following settings:

[CONFIG]
baseurl = http://your.plex.server:32400
token = your_plex_token
library_name = TV Shows

"""

import os
import argparse
import configparser
import requests
from plexapi.server import PlexServer
from moviepy.editor import VideoFileClip


def main():
    # Read the configuration file
    config = configparser.RawConfigParser()
    config.read("config.conf")
    config_dict = dict(config.items("CONFIG"))

    # Parse the command-line arguments
    parser = argparse.ArgumentParser(
        prog="Plex Thumbnail Generator",
        description="Will Check your TV Show library for missing thumbnails",
        epilog="Can create them if mode is set to WRITE",
    )
    parser.add_argument(
        "-m", "--mode", dest="mode", required=True, help="extraction mode, REPORT/CREATE"
    )

    args = parser.parse_args()

    # Connect to Plex
    baseurl = config_dict["baseurl"]
    token = config_dict["token"]
    plex = PlexServer(baseurl, token)

    # Get the TV Show library
    shows = plex.library.section(config_dict["library_name"])

    # Iterate over all TV shows in the library
    shows_list = shows.all()
    print("--Starting--")
    print(f"Processing - {config_dict['library_name']}")
    print(f"Mode = {args.mode}")
    for tv_show in shows_list:
        # Get the selected TV show
        selected_tv_show = shows.get(tv_show.title)

        # Get a list of all episodes in the show
        list_of_episodes_in_show = selected_tv_show.episodes()

        # Print the name of the TV show and the number of episodes
        print(f"{selected_tv_show.title}, episodes = {len(list_of_episodes_in_show)}")

        # Iterate over all episodes in the show
        for single_episode_in_show in list_of_episodes_in_show:
            # Check if the episode has a poster
            if single_episode_in_show.posterUrl:
                # Make a request to the poster URL
                r = requests.get(single_episode_in_show.posterUrl)

                # If the request returns a 404, the poster is missing
                if r.status_code == 404:
                    # Get the file name of the episode
                    file_name = os.path.basename(single_episode_in_show.locations[0])[:-4]

                    # Get the directory where the episode is located
                    file_path = os.path.dirname(single_episode_in_show.locations[0])

                    # Print a message indicating that the poster is missing
                    print(f"Poster missing for - {file_name}")

                    # Check if we are in CREATE mode
                    if args.mode == "WRITE":
                        # Create a VideoFileClip for the episode
                        clip = VideoFileClip(single_episode_in_show.locations[0])

                        # Save a frame from the clip as a PNG file
                        clip.save_frame(f"{file_path}/{file_name}.png", t=clip.duration / 2)

                        # Print a message indicating that the poster was created
                        print(f"Poster generated for - {file_name}")

                        # Refresh the episode to get the updated metadata
                        single_episode_in_show.refresh()

    print("--Finished--")


if __name__ == "__main__":
    main()
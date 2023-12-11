import os
import argparse
import configparser
import requests
from plexapi.server import PlexServer
from moviepy.editor import VideoFileClip

config = configparser.RawConfigParser()
config.read("config.conf")
config_dict = dict(config.items("CONFIG"))

parser = argparse.ArgumentParser(
    prog="Plex Thumbnail Generator",
    description="Will Check your TV Show library for missing thumbnails",
    epilog="Can create them if mode is set to WRITE",
)
parser.add_argument(
    "-m", "--mode", dest="mode", required=True, help="extraction mode, REPORT/CREATE"
)

args = parser.parse_args()
baseurl = config_dict["baseurl"]
token = config_dict["token"]
plex = PlexServer(baseurl, token)
shows = plex.library.section(config_dict["library_name"])
shows_list = shows.all()
print("--Starting--")
print(f"Processing - {config_dict['library_name']}")
print(f"Mode = {args.mode}")
for tv_show in shows_list:
    selected_tv_show = shows.get(tv_show.title)
    list_of_episodes_in_show = selected_tv_show.episodes()
    print(f"{selected_tv_show.title}, episodes = {len(list_of_episodes_in_show)}")
    for single_episode_in_show in list_of_episodes_in_show:
        if single_episode_in_show.posterUrl:
            r = requests.get(single_episode_in_show.posterUrl)
            if r.status_code == 404:
                file_name = os.path.basename(single_episode_in_show.locations[0])[:-4]
                file_path = os.path.dirname(single_episode_in_show.locations[0])
                print(f"Poster missing for - {file_name}")
                if args.mode == "WRITE":
                    clip = VideoFileClip(single_episode_in_show.locations[0])
                    clip.save_frame(f"{file_path}/{file_name}.png", t=clip.duration / 2)
                    print(f"Poster generated for - {file_name}")
                    single_episode_in_show.refresh()
print("--Finished--")

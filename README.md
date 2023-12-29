This repository contains a docker compose implementation of:
https://github.com/alexta69/metube

however instead of implementing the queue functionality with
a web interface the script is intended to derive the downloadable 
videos directly from a youtube account.

the downloading of videos is split into 3 phases namely:

fetching:

    - all Subscriptions are downloaded and persisted.
    
    - all videos are downloaded and persisted (with aiomultiprocess)
    
selecting:

    - videos are selected from the postgres Video table by means of a new
      command to be implemented in dlp that takes a list of video_id and selects
      video from the videos table to be transferred to the Download table
      
downloading:

    - videos from the Download table with the status 
      pending and are scheduled to be asynchronously
      downloaded with yt-dlp via a multiprocessing queue.
      
    - yt-dlp requests a download from the postgres database 
    
      and proceeds to download a video.
    - callbacks are used to update the state in postgres.


the downlaoder is implemented in the worker directory and occurs behind a vpn
using the gluetun service

env vars with associated parameters are set as follows:

set -a
source .env
docker-compose up -d


the project is incomplete however is complete to the extent that the workings herein
can be ascertained.

Please complete it as per the job spec.

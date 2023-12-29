import logging
import os
import yt_dlp
from sqlalchemy import Session, func
from pkg.models import Download

AUDIO_FORMATS = ("m4a", "mp3", "opus", "wav")

def get_format(format: str, quality: str) -> str:
    """
    Returns format for download

    Args:
      format (str): format selected
      quality (str): quality selected

    Raises:
      Exception: unknown quality, unknown format

    Returns:
      dl_format: Formatted download string
    """
    format = format or "any"

    if format.startswith("custom:"):
        return format[7:]

    if format == "thumbnail":
        # Quality is irrelevant in this case since we skip the download
        return "bestaudio/best"

    if format in AUDIO_FORMATS:
        # Audio quality needs to be set post-download, set in opts
        return "bestaudio/best"

    if format in ("mp4", "any"):
        if quality == "audio":
            return "bestaudio/best"
        # video {res} {vfmt} + audio {afmt} {res} {vfmt}
        vfmt, afmt = ("[ext=mp4]", "[ext=m4a]") if format == "mp4" else ("", "")
        vres = f"[height<={quality}]" if quality != "best" else ""
        vcombo = vres + vfmt

        return f"bestvideo{vcombo}+bestaudio{afmt}/best{vcombo}"

    raise Exception(f"Unkown format {format}")


def download_video(
    engine,
):
    with Session(engine) as session:
        vid = session.query(Video).first()
        print(vid)
        print(vid.subscription.title)
        download = Download(**{
            'video_id': vid.video_id,
            'status': 'pending',
            'msg': '',
            'url': 'https://www.youtube.com/watch?v=DWXq4Q3vjPY',
            'filename': slugify(vid.title) + "_" + vid.video_id,
            'folder': slugify(vid.subscription.title) + "_" + vid.subscription.resource_channel_id,
            'path': slugify(vid.subscription.title) + "_" + vid.subscription.resource_channel_id,
            'temp_path': slugify(vid.subscription.title) + "_" + vid.subscription.resource_channel_id,
            'outtmpl': '%(title)s.%(ext)s',
            'chaptmpl': '%(title)s - %(section_number)s %(section_title)s.%(ext)s',
        })
        print(download.filename)
        print(download.folder)
        session.add(download)
        session.commit()
        print(download.id)

        format = get_format("any", 'best')

        def put_status(st):
            print(st)
            download.update(st)
            session.commmit()

        def put_status_postprocessor(d):
            print(d)
            print("bam")
            if d['postprocessor'] == 'MoveFiles' and d['status'] == 'finished':
                if '__finaldir' in d['info_dict']:
                    filename = os.path.join(d['info_dict']['__finaldir'], os.path.basename(d['info_dict']['filepath']))
                else:
                    filename = d['info_dict']['filepath']

                download.update({'status': 'finished', 'filename': filename})
                session.commit()

        if download.ytdl_opts:
            opts = download.ytdl_opts
        else:
            opts = {}

        print(download.url)

        try:
            ret = yt_dlp.YoutubeDL(params={
                'quiet': True,
                'no_color': True,
                # 'write_all_thumbnails':True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'writelink': True,
                'writedesktoplink': True,
                'break_on_existing': True,
                'writeannotations': True,
                'writedescription': True,
                'getcomments': True,
                'writeinfojson': True,
                'subtitleslangs': ['en.*'],
                # 'allsubtitles':True,
                # 'skip_download': True,
                'paths': {
                    "home": download.path,
                    "temp": download.temp_path
                },
                'outtmpl': {
                    "default": download.outtmpl,
                    "chapter": download.chaptmpl
                },
                'format': format,
                'socket_timeout': 30,
                'ignore_no_formats_error': True,
                'progress_hooks': [put_status],
                'postprocessor_hooks': [put_status_postprocessor],
                **opts,
            }).download([download.url])
        except Exception as e:
            logging.exception(e)
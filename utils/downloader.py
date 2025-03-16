import os
import yt_dlp
import re
from urllib.parse import urlparse

def validate_url(url):
    """Validate if URL is from supported platforms"""
    parsed = urlparse(url)
    valid_domains = ['youtube.com', 'youtu.be', 'facebook.com', 'fb.com', 'instagram.com']
    return any(domain in parsed.netloc for domain in valid_domains)

def download_video(url, format_type, temp_dir):
    """Download video using yt-dlp with progress callback"""
    
    output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')
    
    # Configure yt-dlp options
    if format_type == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_template,
        }
    else:  # mp4
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': output_template,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Adjust filename for mp3
            if format_type == 'mp3':
                filename = re.sub(r'\.[^.]+$', '.mp3', filename)
                
            return os.path.basename(filename)
            
    except Exception as e:
        raise Exception(f"Erro no download: {str(e)}")

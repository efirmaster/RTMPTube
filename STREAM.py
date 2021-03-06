# This software manages the 2UBE/2UBE Extra streaming to YouTube from the
# Catalyst Mac via dvgrab and ffmpeg.

# Author: Callum McLean
# Version: 1.02
# Changelog:
#   1.02:   Added general configuration abilities for most options
#           Fixed issue #1 (https://github.com/calmcl1/RTMPTube/issues/1)
#	1.01: Added default fullscreen, opening instructions
#	1.01: Initial version

"""
Set the stream parameters below. This will then call dvgrab and ffmpeg
with these parameters and start streaming to the provided YouTube server via
RTMP.
"""

import subprocess

# General config
OPTIONS = {
    "ffmpeg_path": "/home/ubuntu/Desktop/ffmpeg",
    "audio_bitrate": 192,  # in kbps
    "video_codec": "libx264",  # this must match the FFMPEG codec name
    "audio_codec": "aac",  # this must match the FFMPEG codec name
    "audio_sample_rate": 44100,
    "stream_format": "flv",  # this must match the FFMPEG format name
    "gop_length": 15,  # length of GOP; one keyframe per xx frames
    "fps": 30,
    "pal_expansion": True,  # whether or not 16-235 PAL luminance values\
    # should be expanded to 0-255
    "video_offset": 0.15  # video offset time in seconds (for A/V sync)
}

###########################################################################
# BELOW THIS BLOCK SHOULD NOT REQUIRE CONFIG UNLESS CHANGING INPUT METHOD #
###########################################################################

# Video resolution presets
RESOLUTION_PRESETS = {
    "1080p": {
        "res_h": "1920",
        "res_v": "1080",
        "bitrate": "4500"
    },
    "720p": {
        "res_h": "1280",
        "res_v": "720",
        "bitrate": "2500",
    },
    "480p": {
        "res_h": "854",
        "res_v": "480",
        "bitrate": "1000",
    },
    "360p": {
        "res_h": "640",
        "res_v": "360",
        "bitrate": "750",
    },
    "240p": {
        "res_h": "426",
        "res_v": "240",
        "bitrate": "400",
    }
}

resolution = stream_name = stream_url = None

print """RTMPTube Stream Provider
Version 1.2 - 31/03/14

Press CTRL + C at any time to exit this programme and terminate the stream.

Use CTRL + SHIFT + C to copy and CTRL + SHIFT + V to paste.

"""

# Begin data entry part
print "Please provide the following data. Press Enter to accept defaults."

# Request the stream ID (second part of rtmp URL)
while not stream_name:
    stream_name = raw_input("Stream Name: ")
    if not stream_name: print "Sorry, try again."

# Request the stream base URL
stream_url = raw_input("Primary Server URL\
[default: rtmp://a.rtmp.youtube.com/live2]: ")
if not stream_url: stream_url = "rtmp://a.rtmp.youtube.com/live2"


# Request desired resolution
print """Available resolutions:
\t1. 1080p
\t2. 720p
\t3. 480p
\t4. 360p
\t5. 240p"""

res_input = None
while not res_input in ["1", "2", "3", "4", "5"]:
    res_input = raw_input("Resolution (1/2/3/4/5) [default: 720p]: ")
    if not res_input:
        res_input = "2"
    elif not res_input in ["1", "2", "3", "4", "5"]:
        "Sorry, try again."

if res_input == "1":
    resolution = RESOLUTION_PRESETS["1080p"]
elif res_input == "2":
    resolution = RESOLUTION_PRESETS["720p"]
elif res_input == "3":
    resolution = RESOLUTION_PRESETS["480p"]
elif res_input == "4":
    resolution = RESOLUTION_PRESETS["360p"]
elif res_input == "5":
    resolution = RESOLUTION_PRESETS["240p"]

# Display the final stream settings

print """
Broadcast parameters:
\tResolution: %(res_h)sx%(res_v)s
\tVideo bitrate: %(video_bitrate)s
\tAudio bitrate: %(audio_bitrate)s
\tVideo codec: %(video_codec)s
\tAudio codec: %(audio_codec)s
\tStream container: %(stream_format)s
\tGOP length: %(gop_length)s
\tFPS: %(fps)s
\tPAL luminance expansion: %(pal_expansion)s

\tServer URL: %(stream_url)s
\tStream name: %(stream_name)s
""" % {"res_h": resolution["res_h"],
       "res_v": resolution["res_v"],
       "video_bitrate": resolution["bitrate"] + "kbps",
       "audio_bitrate": OPTIONS["audio_bitrate"] + "kbps",
       "video_codec": OPTIONS["video_codec"],
       "audio_codec": OPTIONS["audio_codec"],
       "stream_format": OPTIONS["stream_format"],
       "gop_length": OPTIONS["gop_length"],
       "fps": OPTIONS["fps"],
       "pal_expansion": OPTIONS["pal_expansion"],
       "stream_url": stream_url, "stream_name": stream_name}

# Approve the stream settings
raw_input("Press Enter to accept the settings and begin the stream.")

# Build the command
cmd = "dvgrab - | %(ffmpeg_path)s -itsoffset:0 %s(offset) -i - -s %(res_h)sx%(res_v) " \
      "-b:v %(video_bitrate)sk -r %(fps)s -ar %(sample_rate)s -ab %(audio_bitrate)sk " \
      "-f %(stream_format)s -c:v %(video_codec)s -aspect 16:9 "
      % {"ffmpeg_path": OPTIONS["ffmpeg_path"],
         "offset": OPTIONS["video_offset"],
         "res_h": resolution["res_h"],
         "res_v": resolution["res_v"],
         "video_bitrate": resolution["bitrate"],
         "fps": OPTIONS["fps"],
         "sample_rate": OPTIONS["audio_sample_rate"],
         "audio_bitrate": OPTIONS["audio_bitrate"],
         "stream_format": OPTIONS["stream_format"],
         "video_codec": OPTIONS["video_codec"]}

if OPTIONS["pal_expansion"]: cmd += '-vf lutyuv="y=(val-16)*(255/219)" '

cmd += "-c:a %(audio_codec)s -strict experimental -g %(gop_length)s" \
       % {"audio_codec": OPTIONS["audio_codec"],
          "gop_length": OPTIONS["gop_length"]}

cmd += stream_url + "/" + stream_name

# Start the stream
subprocess.call(cmd, shell=True)

# Ideal command:
#dvgrab - | options["ffmpeg_path"] -ik - -s 1080x720 -b 3000k -ar 44100 -ab 128k -f flv -vcodec libx264 -acodec aac -strict experimental -g 15 -r 30 rtmp://a.rtmp.youtube.com/live2/the2ubeLIPA.fuas-hqvr-gzwu-7gyd

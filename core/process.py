import json
import re
import subprocess

from config import *

def get_redirected_rtsp(rtsp_url):
    command = ["ffprobe", "-print_format", "json", "-i", rtsp_url]

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, timeout=5
        )
        output = result.stderr

        redirect_match = re.search(r"Redirecting to (rtsp://[^\s]+Uni\.sdp)", output)
        if redirect_match:
            return redirect_match.group(1)
    except Exception as e:
        print(f"Error occurred while running ffprobe: {e}")
        return None

    return None


def gen_iptv_json():
    with open("raw.json", "r", encoding="utf-8") as file:
        json_data = json.load(file)

    output_data = []

    for channel in json_data:
        if "ChannelURL" in channel and channel["ChannelURL"].startswith("igmp://"):

            udpxy_url = f"{udpxy_base_url}{channel['ChannelURL'].replace('igmp://', '')}"

            tvg_id = channel["UserChannelID"]

            channel_name = channel["ChannelName"]

            tvg_name = (
                channel_name.replace("超高清", "")
                .replace("高清", "")
                .replace("标清", "")
                .replace(" ", "")
            )

            group_title = "其他频道"
            for keyword, group in group_keywords.items():
                if keyword in channel_name:
                    group_title = group
                    break

        else:
            print(f"频道 {channel.get('ChannelID', '?')} 没有 ChannelURL,跳过")
            continue

        if "ChannelSDP" in channel:
            print(f"Processing: {channel_name}")
            uni_live = "Not Found"
            uni_playback = "Not Found"
            match = re.search(r"rtsp://\S+", channel["ChannelSDP"])
            if match:
                uni_live = match.group(0)
                redirected = get_redirected_rtsp(uni_live)
                if redirected is not None:
                    uni_live = redirected
                    pattern = r"(rtsp://\S+:\d+).*?(ch\d*)"
                    match = re.search(pattern, uni_live)
                    if match:
                        url = match.group(1)
                        cid = match.group(2)
                        uni_playback = (
                            f"{url}/iptv/Tvod/iptv/001/001/{cid}.rsc?tvdr={timeshift}"
                        )
                else:
                    print(f"Not Found unicast address of: {channel_name}")

        record = {
            "tvg_id": tvg_id,
            "tvg_name": tvg_name,
            "group_title": group_title,
            "channel_name": channel_name,
            "udpxy_url": udpxy_url,
            "uni_live": uni_live,
            "uni_playback": uni_playback,
        }

        output_data.append(record)

    with open("iptv.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)


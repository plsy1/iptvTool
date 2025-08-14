import json
from pathlib import Path
from config import *


def gen_m3u_playlist(
    json_file: str, output_file: str, mode: str = "uni", sort_file: str | None = None
) -> None:
    """
    生成 M3U 播放列表，可按 sort_file 指定顺序写入
    :param json_file: JSON 数据文件
    :param output_file: 输出的 .m3u 路径
    :param mode: 'uni' 单播；'mul' 组播
    :param sort_file: 包含 tvg_id 的排序文件，一行一个；若为 None 则保持原顺序
    """
    # ------- 1. 读频道数据 -------
    with Path(json_file).open("r", encoding="utf-8") as fp:
        channels: list[dict] = json.load(fp)

    # ------- 2. 如果给了排序文件，就按照排序文件的 tvg_id 顺序重排 -------
    if sort_file:
        with Path(sort_file).open("r", encoding="utf-8") as fp:
            order_list = [line.strip() for line in fp if line.strip()]

        # 建立 id → 频道 映射（如果同 id 有多个频道，用列表容纳）
        bucket: dict[str, list[dict]] = {}
        for ch in channels:
            bucket.setdefault(ch.get("tvg_id", ""), []).append(ch)

        ordered_channels: list[dict] = []
        for tid in order_list:
            ordered_channels.extend(bucket.pop(tid, []))  # 若 id 不存在就跳过

        # 剩余没被列出的频道附加在末尾
        for remaining in bucket.values():
            ordered_channels.extend(remaining)

        channels = ordered_channels

    # ------- 3. 写入 .m3u -------
    with Path(output_file).open("w", encoding="utf-8") as fp:
        fp.write(f"#EXTM3U url-tvg=\"{url_tvg}\" \n")

        for ch in channels:
            tvg_id = ch.get("tvg_id", "")
            tvg_name = ch.get("tvg_name", "")
            tvg_name = name_map_by_name.get(tvg_name, tvg_name)
            tvg_name = name_map_by_id.get(tvg_id, tvg_name)
            # if tmp != tvg_name:
            #     tvg_name = tmp
            group_title = ch.get("group_title", "")
            channel_name = ch.get("channel_name", "")

            # 选择 URL
            if mode == "uni":
                url = ch.get("uni_live", "")
            else:  # mul
                if "CCTV" in channel_name and "高清" not in channel_name:
                    continue
                url = ch.get("udpxy_url", "")

            if not url:
                continue  # 没流地址跳过

            # 处理 logo
            tvg_logo = (
                f"{logo_base}{name_map_by_name.get(tvg_name, tvg_name)}.png".replace(
                    "超高清", ""
                )
                .replace("高清", "")
                .replace(" ", "")
            )

            # 构造 #EXTINF 行
            extinf = (
                # f'#EXTINF:-1 tvg-id="{tvg_id}" '
                f'#EXTINF:-1 '
                f'tvg-name="{tvg_name}" '
                f'group-title="{group_title}" '
                f'tvg-logo="{tvg_logo}" '
            )

            catchup = ch.get("uni_playback")
            if catchup:
                extinf += f'catchup="default" catchup-source="{catchup}"'

            extinf += f", {tvg_name}"
            fp.write(f"{extinf}\n{url}\n")



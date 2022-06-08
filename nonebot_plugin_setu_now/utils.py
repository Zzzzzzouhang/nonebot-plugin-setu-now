from typing import List, Optional
import numpy as np
import cv2
from httpx import AsyncClient
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent


async def download_pic(url: str, proxies: Optional[str] = None) -> Optional[bytes]:
    async with AsyncClient(proxies=proxies) as client:  # type: ignore
        headers = {
            "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        }
        logger.debug(f"正在下载...{url}")
        re = await client.get(url=url, headers=headers, timeout=60)
        if re.status_code == 200:
            logger.debug("成功获取图片")
            # bytes 转 numpy
            img_buffer_numpy = np.frombuffer(re.content, dtype=np.uint8)                
            # 将 图片字节码bytes  转换成一维的numpy数组 到缓存中
            img_numpy = cv2.imdecode(img_buffer_numpy, 1)   
            # 从指定的内存缓存中读取一维numpy数据，并把数据转换(解码)成图像矩阵格式
            dst= cv2.resize(img_numpy, None,fx=0.99,fy=0.99, interpolation=cv2.INTER_CUBIC)
            # numpy 转 bytes
            _, img_encode = cv2.imencode('.jpg', dst)
            img_bytes = img_encode.tobytes()                 
            return img_bytes
        else:
            logger.error(f"获取图片失败: {re.status_code}")
            return


async def send_forward_msg(
    bot: Bot,
    event: GroupMessageEvent,
    name: str,
    uin: str,
    msgs: List[Message],
):
    """
    :说明: `send_forward_msg`
    > 发送合并转发消息

    :参数:
      * `bot: Bot`: bot 实例
      * `event: GroupMessageEvent`: 群聊事件
      * `name: str`: 名字
      * `uin: str`: qq号
      * `msgs: List[Message]`: 消息列表
    """

    def to_json(msg: Message):
        return {"type": "node", "data": {"name": name, "uin": uin, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    await bot.call_api(
        "send_group_forward_msg", group_id=event.group_id, messages=messages
    )

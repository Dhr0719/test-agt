"""
七牛云对象存储工具。
提供上传、下载、删除等基本操作，供 knowledge.py 调用。
"""

import os
import hashlib
import logging
from io import BytesIO

import httpx
import hmac
import time
import base64
import urllib.parse
from hashlib import sha1

logger = logging.getLogger(__name__)


def _get_config():
    """延迟读取七牛云配置（确保 .env 已加载到 os.environ）。"""
    ak = os.getenv("QINIU_ACCESS_KEY", "").strip()
    sk = os.getenv("QINIU_SECRET_KEY", "").strip()
    bucket = os.getenv("QINIU_BUCKET", "lqragent").strip()
    domain = os.getenv("QINIU_DOMAIN", f"http://{bucket}.qiniucdn.com").strip()
    return ak, sk, bucket, domain


def _make_token(key: str) -> str:
    """生成七牛云上传凭证（put policy token）。"""
    ak, sk, bucket, _ = _get_config()
    if not ak or not sk:
        raise RuntimeError("七牛云 QINIU_ACCESS_KEY / QINIU_SECRET_KEY 未配置")

    logger.info(f"[Qiniu] generating token: bucket={bucket}, key={key}, ak_prefix={ak[:8]}...")

    policy = {
        "scope": f"{bucket}:{key}",
        "deadline": int(time.time()) + 3600,
    }
    import json
    policy_encoded = base64.urlsafe_b64encode(
        json.dumps(policy, separators=(",", ":")).encode()
    ).decode()
    sign = hmac.new(sk.encode(), policy_encoded.encode(), sha1).digest()
    sign_encoded = base64.urlsafe_b64encode(sign).decode()
    token = f"{ak}:{sign_encoded}:{policy_encoded}"
    logger.info(f"[Qiniu] token generated, length={len(token)}")
    return token


def _make_download_token(key: str, deadline: int) -> str:
    """生成七牛云私有空间下载签名。"""
    ak, sk, _, domain = _get_config()
    if not ak or not sk:
        raise RuntimeError("七牛云 AK/SK 未配置")

    base_url = f"{domain}/{urllib.parse.quote(key, safe='')}"
    sign_str = f"{base_url}?e={deadline}"
    sign = hmac.new(sk.encode(), sign_str.encode(), sha1).digest()
    sign_encoded = base64.urlsafe_b64encode(sign).decode().rstrip("=")
    return f"{base_url}?e={deadline}&token={ak}:{sign_encoded}"


def upload_to_qiniu(key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    """
    上传文件到七牛云。

    Args:
        key: 对象 key（如 uploads/1/xxx.pdf）
        data: 文件字节
        content_type: MIME 类型

    Returns:
        上传后的 key
    """
    token = _make_token(key)
    # 根据 CDN 域名判断区域: hb-bkt 通常是华北 z1
    _, _, bucket, domain = _get_config()
    if "z1" in domain or "hb-bkt" in domain:
        upload_host = "upload-z1.qiniup.com"
    elif "z2" in domain:
        upload_host = "upload-z2.qiniup.com"
    elif "na0" in domain:
        upload_host = "upload-na0.qiniup.com"
    else:
        upload_host = "upload.qiniup.com"
    url = f"https://{upload_host}/"

    form_data = {
        "token": token,
        "key": key,
    }
    files = {"file": (key.split("/")[-1], BytesIO(data), content_type)}

    logger.info(f"[Qiniu] uploading to {upload_host}, bucket={bucket}, key={key}")
    resp = httpx.post(url, data=form_data, files=files, timeout=60)
    if resp.status_code != 200:
        logger.error(f"[Qiniu] upload failed: status={resp.status_code}, body={resp.text}")
    resp.raise_for_status()
    logger.info(f"[Qiniu] uploaded: key={key}, size={len(data)}")
    return key


def download_from_qiniu(key: str) -> bytes:
    """
    从七牛云下载文件。

    Args:
        key: 对象 key

    Returns:
        文件字节
    """
    deadline = int(time.time()) + 3600
    url = _make_download_token(key, deadline)

    resp = httpx.get(url, timeout=30, follow_redirects=True)
    resp.raise_for_status()
    logger.debug(f"[Qiniu] downloaded: key={key}, size={len(resp.content)}")
    return resp.content


def delete_from_qiniu(key: str) -> bool:
    """从七牛云删除文件。"""
    ak, sk, _, _ = _get_config()
    if not ak or not sk:
        return False

    path = f"/delete/{urllib.parse.quote(key, safe='')}"
    url_to_sign = f"{ak}:{path}"
    sign = hmac.new(sk.encode(), url_to_sign.encode(), sha1).digest()
    sign_encoded = base64.urlsafe_b64encode(sign).decode().rstrip("=")

    delete_url = f"https://rs.qiniuapi.com{path}"
    headers = {"Authorization": f"QBox {ak}:{sign_encoded}"}

    try:
        resp = httpx.delete(delete_url, headers=headers, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.warning(f"[Qiniu] delete failed: key={key}, error={e}")
        return False


def compute_sha256(data: bytes) -> str:
    """计算字节数据的 SHA256 哈希。"""
    return hashlib.sha256(data).hexdigest()

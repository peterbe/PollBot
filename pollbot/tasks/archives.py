from pollbot.utils import build_version_id, Channel, get_version_channel, get_version_from_filename
from . import get_session, heartbeat_factory


async def archives(product, version):
    with get_session() as session:
        channel = get_version_channel(version)
        if channel is Channel.NIGHTLY:
            url = 'https://archive.mozilla.org/pub/{}/nightly/latest-date-l10n/'.format(product)
            async with session.get(url, headers={"Accept": "application/json"}) as resp:
                if resp.status != 200:
                    return False
                body = await resp.json()
                files = sorted([(r["last_modified"], r["name"]) for r in body["files"]
                                if r["name"].startswith("{}-".format(product))],
                               key=lambda x: x[0],
                               reverse=True)
                last_release = get_version_from_filename(files[0][1])
                return build_version_id(last_release) >= build_version_id(version)
        else:
            url = 'https://archive.mozilla.org/pub/{}/releases/{}/'.format(product, version)
            async with session.get(url) as resp:
                return resp.status != 404


heartbeat = heartbeat_factory('https://archive.mozilla.org/pub/firefox/releases/')

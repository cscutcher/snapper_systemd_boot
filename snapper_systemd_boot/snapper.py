# -*- coding: utf-8 -*-
"""
Wrap Snapper DBUS client.

In a few places I convert dbus types to native. I know this isn't strictly
necessary, as the dbus ones subclass the native, but it was irritating when
dumping repr to console, and I really didn't need the dbus metadata.
"""
from datetime import datetime
from enum import Enum
from pathlib import Path
import logging

from reprutils import GetattrRepr

import dbus

DEV_LOGGER = logging.getLogger(__name__)


def test_get_snapshots(snapper):
    snapshot = next(snapper.get_snapshots_iter("root"))
    assert snapshot.description == "current"


class SnapshotType(Enum):
    SINGLE = 0
    PRE = 1
    POST = 2


class Snapper:
    """
    Wrap Snapper DBUS client.
    """
    def __init__(self, bus):
        self.snapper = dbus.Interface(
            bus.get_object(
                'org.opensuse.Snapper',
                '/org/opensuse/Snapper'),
            dbus_interface='org.opensuse.Snapper'
        )

    def get_configs_iter(self):
        configs = self.snapper.ListConfigs()
        for config in configs:
            yield SnapperConfig(*config)

    def get_snapshots_iter(self, config_name):
        for snapshot in self.snapper.ListSnapshots(config_name):
            yield Snapshot(*snapshot)


class SnapperConfig:
    def __init__(self, name, path, config):
        self.name = str(name)
        self.path = Path(path)
        self.config = config

    __repr__ = GetattrRepr(
        "name",
        "path",
        "config",
    )


class Snapshot:
    def __init__(
            self,
            num,
            type_raw,
            pre_num,
            timestamp,
            uid,
            description,
            cleanup,
            userdata):
        self.type = SnapshotType(type_raw)
        self.num = int(num)
        self.pre_num = int(pre_num)
        self.timestamp = datetime.fromtimestamp(timestamp)
        self.uid = int(uid)
        self.description = str(description)
        self.cleanup = str(cleanup)
        self.userdata = {
            str(key): str(value)
            for key, value in userdata.items()
        }

    @property
    def iso_timestamp(self):
        """
        Outputs timestamp in isoformat string.
        """
        return self.timestamp.isoformat()

    __repr__ = GetattrRepr(
        "num",
        "type",
        pre_num="pre_num",
        timestamp="timestamp",
        uid="uid",
        description="description",
        cleanup="cleanup",
        userdata="userdata",
    )

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
import pytest

import dbus

DEV_LOGGER = logging.getLogger(__name__)


@pytest.mark.real_config
def test_get_snapshots(snapper):
    """Test we can access snapshots via dbus."""
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
        """
        Get all snapper configs wrapped in helper class.
        """
        configs = self.snapper.ListConfigs()
        for config in configs:
            yield SnapperConfig(*config)

    def get_snapshots_iter(self, config_name):
        """
        Get all existing snapshots for config.

        Also discover the mountpoint for each snapshot on filesystem.
        """
        for snapshot in self.snapper.ListSnapshots(config_name):
            snapshot = Snapshot(*snapshot)
            snapshot.mount_point = Path(
                self.snapper.GetMountPoint(
                    config_name, snapshot.num))
            yield snapshot


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
    """
    Wrap individual snapper snapshot.
    """
    def __init__(
            self,
            num,
            type_raw,
            pre_num,
            timestamp,
            uid,
            description,
            cleanup,
            userdata,
            mount_point=None,
            ):
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
        self.mount_point = mount_point

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
        mount_point="mount_point",
    )

from datetime import datetime
from enum import Enum
from pathlib import Path

from reprutils import GetattrRepr

import dbus


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
            date,
            uid,
            description,
            cleanup,
            userdata):
        self.type = SnapshotType(type_raw)
        self.num = int(num)
        self.pre_num = int(pre_num)
        self.date = datetime.fromtimestamp(date)
        self.uid = int(uid)
        self.description = str(description)
        self.cleanup = str(cleanup)
        self.userdata = userdata

    __repr__ = GetattrRepr(
        "num",
        "type",
        pre_num="pre_num",
        data="date",
        uid="uid",
        description="description",
        cleanup="cleanup",
    )

    def __str__(self):
        return f"Snapshot({self.num}, {self.type}, {self.description!r})"

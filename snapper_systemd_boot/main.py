from collections import namedtuple
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from io import StringIO
from pathlib import Path
from pprint import pprint

from dbus.mainloop.glib import DBusGMainLoop
import dbus
import gi
import pytest
from reprutils import GetattrRepr

gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "3.0")


@pytest.fixture
def bus():
    return dbus.SystemBus(mainloop=DBusGMainLoop())


@pytest.fixture
def inst(bus):
    outputs = {}

    @contextmanager
    def write_factory(p):
        io_inst = StringIO()
        yield io_inst
        outputs[p] = io_inst.getvalue()

    inst = SnapperSystemDBootManager(bus, write_factory)
    inst.OUTPUTS = outputs
    yield inst
    pprint(outputs)


def test_get_root_config(inst):
    root_config = inst.get_root_config()
    name, path, config = inst.snapper.GetConfig(root_config.name)

    assert name == root_config.name
    assert path == root_config.path == "/"


def test_get_root_snapshots(inst):
    snapshots = inst.get_root_snapshots()
    assert snapshots[0].description == "current"


def test_generate_configs(inst):
    inst.generate_boot_configs()


SnapperConfigListing = namedtuple(
    "SnapperConfigListing", ["name", "path", "config"])


class SnapshotType(Enum):
    SINGLE = 0
    PRE = 1
    POST = 2


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


BOOT_DIR = Path("/boot")
ENTRIES_DIR = BOOT_DIR / "loader/entries"

ENTRY_FILENAME_GLOB = "arch-auto-snapshot-*.conf"
ENTRY_FILENAME_TEMPLATE = "arch-auto-snapshot-{snapshot.num}.conf"
ENTRY_TEMPLATE = """
title Arch Linux (Snapshot {date} [{snapshot.num}])
linux /vmlinuz-linux
initrd /initramfs-linux.img
options cryptdevice=UUID=d79c85d5-0ed6-4b92-b3dd-e7b6fc7dee9f:aeryn-root-crypt\
    root=/dev/mapper/aeryn-root-crypt quiet rw\
    rootflags=subvol=@/.snapshots/{snapshot.num}/snapshot
"""


class SnapperSystemDBootManager:
    def __init__(self, bus, write_factory=lambda p: p.open("w")):
        self.snapper = dbus.Interface(
            bus.get_object(
                'org.opensuse.Snapper',
                '/org/opensuse/Snapper'),
            dbus_interface='org.opensuse.Snapper'
        )
        self.write_factory = write_factory

    def get_root_config(self):
        configs = self.snapper.ListConfigs()
        for config in configs:
            config = SnapperConfigListing(*config)
            if config.path == "/":
                return config
        raise KeyError("Unable to find root config.")

    def get_root_snapshots_iter(self):
        config = self.get_root_config()
        for snapshot in self.snapper.ListSnapshots(config.name):
            yield Snapshot(*snapshot)

    def get_root_snapshots(self):
        return list(self.get_root_snapshots_iter())

    def generate_boot_configs(self):
        for snapshot in self.get_root_snapshots_iter():
            if snapshot.description == "current":
                continue

            p = ENTRY_FILENAME_TEMPLATE.format(snapshot=snapshot)
            p = ENTRIES_DIR / p
            with self.write_factory(p) as output:
                output.write(ENTRY_TEMPLATE.format(
                    snapshot=snapshot, date=snapshot.date.isoformat()))

    def remove_boot_configs(self):
        for p in ENTRIES_DIR.glob(ENTRY_FILENAME_GLOB):
            p.unlink()


def main():
    bus = dbus.SystemBus(mainloop=DBusGMainLoop())
    inst = SnapperSystemDBootManager(bus)
    inst.remove_boot_configs()
    inst.generate_boot_configs()


# TODO:
#  * Look at user metadata to decide whether to clone vmlinuz and initramfs
#  * Script from setup.py
#  * Hook into snapper
#  * Cleanup and commit


if __name__ == "__main__":
    main()

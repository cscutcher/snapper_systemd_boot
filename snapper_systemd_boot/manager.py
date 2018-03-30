# -*- coding: utf-8 -*-
"""
Main module for managing systemd-boot entries from snapper snapshots.
"""
import logging
from pathlib import Path

from distutils.util import strtobool
import pytest

DEV_LOGGER = logging.getLogger(__name__)


@pytest.fixture
def inst(snapper, config):
    return SnapperSystemDBootManager(snapper, config)


def test_get_root_config(inst):
    root_config = inst.get_root_config()
    name, path, config = inst.snapper.snapper.GetConfig(root_config.name)

    assert name == root_config.name
    assert path == str(root_config.path) == "/"


def test_write_entries(inst):
    inst.write_boot_entries()


def test_generate_entries(inst):
    for entry in inst.get_boot_entries():
        print(entry)


class BootEntry:
    """Boot entry generated from snapshot."""
    class SnapshotWrapper:
        def __init__(self, entry, snapshot):
            self.entry = entry
            self.snapshot = snapshot

        def __getattr__(self, name):
            return getattr(self.snapshot, name)

    def __init__(self, snapshot, config):
        self.snapshot = snapshot
        self.config = config

    @property
    def copy_images(self):
        return strtobool(
            self.snapshot.userdata.get("copy_images", False)
        )

    def get_contents(self):
        snapshot = self.SnapshotWrapper(self, self.snapshot)
        return self.config.entry_template.format(snapshot=snapshot)

    def get_entry_path(self):
        name = "{config.entry_prefix}{snapshot.num}.conf".format(
            config=self.config, snapshot=self.snapshot)
        return self.config.systemd_entries_path / name

    def write(self):
        with open(self.get_entry_path(), 'w') as output:
            output.write(self.get_contents())


class SnapperSystemDBootManager:
    """
    Manage systemd-boot entries derived from snapper snapshots.
    """

    def __init__(self, snapper, config):
        self.snapper = snapper
        self.config = config

    def get_root_config(self):
        for config in self.snapper.get_configs_iter():
            if config.path == Path("/"):
                return config
        raise KeyError("Unable to find root config.")

    def get_snapshots_iter(self):
        config = self.get_root_config()
        for snapshot in self.snapper.get_snapshots_iter(config.name):
            if snapshot.description == "current":
                continue
            if "bootable" in snapshot.userdata:
                is_bootable = strtobool(snapshot.userdata["bootable"].lower())
                if not is_bootable:
                    continue

            yield snapshot

    def get_boot_entries(self):
        for snapshot in self.get_snapshots_iter():
            yield BootEntry(snapshot, self.config)

    def write_boot_entries(self):
        for entry in self.get_boot_entries():
            entry.write()

    def get_existing_entries(self):
        glob = "{config.entry_prefix}*.conf".format(config=self.config)
        return self.config.systemd_entries_path.glob(glob)

    def remove_boot_configs(self):
        for p in self.get_existing_entries():
            DEV_LOGGER.info("Removing: %s", p)
            p.unlink()

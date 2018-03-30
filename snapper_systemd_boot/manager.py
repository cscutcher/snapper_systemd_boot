# -*- coding: utf-8 -*-
"""
Main module for managing systemd-boot entries from snapper snapshots.
"""
import logging
from pathlib import Path

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


def test_get_root_snapshots(inst):
    snapshots = inst.get_root_snapshots()
    assert snapshots[0].description == "current"


def test_generate_configs(inst):
    inst.generate_boot_configs()


class BootEntry:
    """Boot entry generated from snapshot."""

    def __init__(self, snapshot, config):
        self.snapshot = snapshot
        self.config = config

    def get_contents(self):
        return self.config.entry_template.format(
            snapshot=self.snapshot, date=self.snapshot.date.isoformat())

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

    def get_root_snapshots_iter(self):
        config = self.get_root_config()
        return self.snapper.get_snapshots_iter(config.name)

    def get_root_snapshots(self):
        return list(self.get_root_snapshots_iter())

    def generate_boot_configs(self):
        for snapshot in self.get_root_snapshots_iter():
            if snapshot.description == "current":
                continue
            entry = BootEntry(snapshot, self.config)
            entry.write()

    def get_existing_entries(self):
        glob = "{config.entry_prefix}*.conf".format(config=self.config)
        return self.config.systemd_entries_path.glob(glob)

    def remove_boot_configs(self):
        for p in self.get_existing_entries():
            DEV_LOGGER.info("Removing: %s", p)
            p.unlink()

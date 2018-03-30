# -*- coding: utf-8 -*-
"""
CLI for snapper_systemd_boot
"""
import json
import logging
import textwrap

import argh

from snapper_systemd_boot import context
from snapper_systemd_boot.manager import SnapperSystemDBootManager

DEV_LOGGER = logging.getLogger(__name__)


def update():
    """
    Update systemd-boot entries based on snapper snapshots.
    """
    DEV_LOGGER.info("Update entries.")
    inst = context.get_manager()
    inst.remove_boot_configs()
    inst.write_boot_entries()


def remove():
    """
    Remove all systemd-boot entries generated from snapper snapshots.
    """
    DEV_LOGGER.info("Remove existing entries.")
    inst = context.get_manager()
    snapper = context.get_snapper()
    config = context.get_config()
    inst = SnapperSystemDBootManager(snapper, config)
    inst.remove_boot_configs()


def view_config():
    """
    Print config
    """
    config = context.get_config()
    print(config)


class SnapshotListWrapper:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    def __getattr__(self, name):
        return getattr(self.snapshot, name)

    @property
    def userdata_compact_str(self):
        """
        Outputs userdata in compact one line string.
        """
        return textwrap.shorten(
            json.dumps(self.userdata),
            width=70,
            placeholder="...}")

    @property
    def description(self):
        """
        Shorten description for output.
        """
        return textwrap.shorten(
            self.snapshot.description,
            width=80,
            placeholder="...")

    def __str__(self):
        return textwrap.dedent("""\
            {s.num:04}: {s.description}
                created: {s.iso_timestamp}
                type: {s.type.name}
                user_data: {s.userdata_compact_str:.70}
                mount_point: {s.mount_point}
        """.format(s=self))


def list_snapshots():
    """
    List snapshots that will be converted into entries.
    """
    DEV_LOGGER.info("List applicable snapshots")
    inst = context.get_manager()
    snapper = context.get_snapper()
    config = context.get_config()
    inst = SnapperSystemDBootManager(snapper, config)

    yield "Snapshots to make entries:"

    for snapshot in map(SnapshotListWrapper, inst.get_snapshots_iter()):
        yield textwrap.indent(str(snapshot), "  ")


def list_generated():
    """
    List the filenames of already generated entries.
    """
    DEV_LOGGER.info("List generated snapshots")
    inst = context.get_manager()
    snapper = context.get_snapper()
    config = context.get_config()
    inst = SnapperSystemDBootManager(snapper, config)
    for p in inst.get_existing_entries():
        yield str(p)


def list_entries():
    """
    List entries that will be written.
    """
    DEV_LOGGER.info("List generated entries.")
    inst = context.get_manager()
    snapper = context.get_snapper()
    config = context.get_config()
    inst = SnapperSystemDBootManager(snapper, config)
    for entry in inst.get_boot_entries():
        yield "Will write to path:"
        yield textwrap.indent(str(entry.get_entry_path()), "  ")
        yield "\nWill write:"
        yield textwrap.indent(str(entry.get_contents()), "  ")
        yield "=" * 80
        yield "\n"


def main():
    parser = argh.ArghParser()
    parser.add_commands([
        update,
        remove,
        view_config,
        list_generated,
        list_snapshots,
        list_entries,
    ])
    parser.add_argument(
        "--log-level",
        action="store",
        default="WARNING",
        help="Set the log level for the process.",
    )
    parser.set_default_command(update)

    ns = parser.parse_args()
    logging.basicConfig(level=getattr(logging, ns.log_level))

    parser.dispatch()


if __name__ == "__main__":
    main()

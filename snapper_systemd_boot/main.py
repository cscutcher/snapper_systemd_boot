# -*- coding: utf-8 -*-
"""
CLI for snapper_systemd_boot
"""
import logging

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
    inst.generate_boot_configs()


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


# TODO:
#  * Look at user metadata to decide whether to clone vmlinuz and initramfs
#  * Script from setup.py
#  * Hook into snapper
#  * Cleanup and commit
def main():
    parser = argh.ArghParser(add_help=False, conflict_handler="resolve")
    parser.add_argument(
        "--log-level",
        action="store",
        default="INFO",
        help="Set the log level for the process.",
    )
    parser.add_argument(
        "--help", "-h",
        action="store_true",
        default=False)
    ns, remaining_args = parser.parse_known_args()
    if ns.help:
        if remaining_args:
            parser.add_argument(
                "--help", "-h",
                action="help",
            )
            remaining_args.append("--help")
        else:
            parser.print_help()
            return

    logging.basicConfig(level=getattr(logging, ns.log_level))
    parser.add_commands([
        update,
        remove,
        view_config,
    ])
    parser.set_default_command(update)
    parser.dispatch(remaining_args)


if __name__ == "__main__":
    main()

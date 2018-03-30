# -*- coding: utf-8 -*-
"""
Process context
"""
from dbus.mainloop.glib import DBusGMainLoop
import dbus
from functools import lru_cache

import gi

from snapper_systemd_boot.config import SnapperSystemDBootConfig
from snapper_systemd_boot.manager import SnapperSystemDBootManager
from snapper_systemd_boot.snapper import Snapper

gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "3.0")


@lru_cache()
def get_bus():
    return dbus.SystemBus(mainloop=DBusGMainLoop())


@lru_cache()
def get_config():
    return SnapperSystemDBootConfig.from_filename(
        "/etc/snapper_systemd_boot.conf")


@lru_cache()
def get_snapper():
    return Snapper(get_bus())


@lru_cache()
def get_manager():
    return SnapperSystemDBootManager(
        get_snapper(), get_config())

from typing import Callable
from .shop import open_shop, reset_shop, edit_shop
from endstone._internal.endstone_python import (
    ColorFormat,
    Player,
    RenderType,
)
from endstone.command import Command, CommandSender
from endstone.event import event_handler
from endstone.plugin import Plugin
import json


class EasyAsShops(Plugin):
    prefix = "EasyAsShops"
    api_version = "0.5"
    load = "POSTWORLD"

    commands = {
        # Player Commands
        "shop": {
            "description": "Opens the server shop.",
            "usages": ["/shop"],
            "aliases": ["market"],
            "permissions": ["easyas.command.default"],
        },
        # Admin Commands
        "resetshop": {
            "description": "Resets the shop configuration to default.",
            "usages": ["/resetshop"],
            "permissions": ["easyas.command.admin"],
        },
        "editshop": {
            "description": "Opens the shop editor.",
            "usages": ["/editshop"],
            "permissions": ["easyas.command.admin"],
        },
    }

    permissions = {
        "easyas.command.default": {
            "description": "Allow default players to access.",
            "default": True,
        },
        "easyas.command.admin": {
            "description": "Allow only admins to access.",
            "default": "op",
        },
    }

    def on_enable(self) -> None:
        self.register_events(self)

    def on_load(self):
        self.logger.info(
            f"""
        {ColorFormat.GREEN}
        ___                _       ___ _                
       | __|__ _ ____  _  /_\   __/ __| |_  ___ _ __ ___
       | _|/ _` (_-< || |/ _ \ (_-<__ \ ' \/ _ \ '_ (_-<
       |___\__,_/__/\_, /_/ \_\/__/___/_||_\___/ .__/__/   by palm1
                    |__/                       |_|      
        {ColorFormat.RESET}"""
        )

    def on_command(self, sender: CommandSender, command: Command, args: list[str]):
        # You can also handle commands here instead of setting an executor in on_enable if you prefer
        server = self.server
        if not (isinstance(sender, Player)):
            server.logger.info("Only players can use this command.")
            return
        player = sender
        if command.name == "shop":
            open_shop(self, player)
        elif command.name == "resetshop":
            reset_shop(self)
            player.send_message("§eShop has been reset to default.")
        elif command.name == "editshop":
            edit_shop(self, player)
        return True

from endstone import ColorFormat, Player
from endstone.command import Command, CommandSender
from endstone.plugin import Plugin

from .shop import edit_shop, open_shop, reset_shop


class EasyAsShops(Plugin):
    prefix = "EasyAsShops"
    api_version = "0.10"
    load = "POSTWORLD"

    commands = {
        # Player Commands
        "shop": {
            "description": "Opens the server shop.",
            "usages": ["/shop"],
            "aliases": ["market"],
            "permissions": ["easyas.command.shop"],
        },
        # Admin Commands
        "resetshop": {
            "description": "Resets the shop configuration to default.",
            "usages": ["/resetshop"],
            "permissions": ["easyas.command.resetshop"],
        },
        "editshop": {
            "description": "Opens the shop editor.",
            "usages": ["/editshop"],
            "permissions": ["easyas.command.editshop"],
        },
    }

    permissions = {
        "easyas.command.shop": {
            "description": "Shop command permission.",
            "default": True,
        },
        "easyas.command.resetshop": {
            "description": "Reset shop command permission.",
            "default": "op",
        },
        "easyas.command.editshop": {
            "description": "Edit shop command permission.",
            "default": "op",
        },
    }

    def on_enable(self) -> None:
        self.register_events(self)

    def on_load(self):
        self.logger.info(
            f"""
        {ColorFormat.GREEN}                                   
      _____             _____     _____ _               
     |   __|___ ___ _ _|  _  |___|   __| |_ ___ ___ ___ 
     |   __| .'|_ -| | |     |_ -|__   |   | . | . |_ -|
     |_____|__,|___|_  |__|__|___|_____|_|_|___|  _|___|   by palm1
                   |___|                       |_|      

        {ColorFormat.RESET}"""
        )
        self.logger.info(
            f"\n> {ColorFormat.GREEN}{ColorFormat.BOLD}Welcome to EasyAsShops!{ColorFormat.RESET}\n> {ColorFormat.YELLOW}API Version: {self.api_version}{ColorFormat.RESET}\n> {ColorFormat.LIGHT_PURPLE}For help and updates, visit [ {ColorFormat.BLUE}https://github.com/palmmc/EasyAsShops {ColorFormat.LIGHT_PURPLE}]{ColorFormat.RESET}"
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

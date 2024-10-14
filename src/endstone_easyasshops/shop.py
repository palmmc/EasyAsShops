import typing
from endstone._internal.endstone_python import (
    ActionForm,
    Dropdown,
    ModalForm,
    Player,
    Server,
    Slider,
    TextInput,
)
import json
import os
import re

from .EconomyPilot.database_issuer import (
    server_balance_fetch,
    server_deduct,
    server_pay,
)

from endstone.plugin import Plugin

### CHAT CONFIGURATION ###

prefix = "§l§f[§aEAS§f]§r >> "


def send_custom(player: Player, message: str):
    player.send_message(prefix + message)


def error_custom(player: Player, message: str):
    player.send_message(prefix + "§cError: " + message)


### ECONOMY METHODS ###


def replace_score_placeholders(player: Player, string):
    server = player.server
    placeholders = re.findall(r"\{(.*?)\}", string)
    for placeholder in placeholders:
        if placeholder.startswith("score:"):
            objective = placeholder.split(":", 1)[1]
            value = server.scoreboard.get_objective(objective).get_score(player).value
            string = re.sub(r"\{" + re.escape(placeholder) + r"\}", str(value), string)

    return string


def get_objective_display(player: Player, objective: str):
    name = player.server.scoreboard.get_objective(objective)
    if not hasattr(name, "display_name"):
        name = objective
    else:
        name = name.display_name
    return name


def player_balance(player: Player, currency: str):
    if currency == "default":
        return int(server_balance_fetch(player.name))
    else:
        return player.server.scoreboard.get_objective(currency).get_score(player).value


def player_pay(player: Player, currency: str, amount: int):
    if currency == "default":
        server_pay(player.name, amount)
    else:
        player.server.scoreboard.get_objective(currency).get_score(
            player
        ).value += amount


def player_deduct(player: Player, currency: str, amount: int):
    if currency == "default":
        server_deduct(player.name, -amount)
    else:
        player.server.scoreboard.get_objective(currency).get_score(
            player
        ).value -= amount


### DEFAULT SHOP CONFIGURATION ###

default_data = {
    "title": "Shop",
    "content": "Balance: ${balance}",
    "categories": [
        {
            "title": "Blocks",
            "icon": "textures/blocks/grass_side_carried.png",
            "items": [
                {
                    "item": "minecraft:stone",
                    "title": "Stone",
                    "price": 0,
                    "value": 5,
                    "category": "blocks",
                    "icon": "textures/blocks/stone.png",
                    "currency": "default",
                },
                {
                    "item": "minecraft:oak_log",
                    "title": "Oak Log",
                    "price": 10,
                    "value": 0,
                    "category": "blocks",
                    "icon": "textures/blocks/log_oak.png",
                    "currency": "default",
                },
            ],
        },
    ],
}

### SHOP CONFIGURATION MANAGEMENT ###

# Define the path to the JSON file
json_file_path = os.path.abspath("./config/shop.json")


class logger:
    def info(str: str):
        print(str)

    def error(str: str):
        print(str)


# Function to read from the JSON file
def read_shop_config():
    try:
        with open(json_file_path, "r") as file:
            data = json.load(file)
        logger.info(f"Loaded shop configuration from {json_file_path}.")
        return data
    except FileNotFoundError:
        logger.error(f"Error: Missing shop configuration file, generating a new one.")
        write_shop_config(default_data)
        return default_data
    except json.JSONDecodeError:
        logger.error(f"Error: Failed to decode JSON from {json_file_path}.")
        return {}


# Function to write to the JSON file
def write_shop_config(data):
    try:
        with open(json_file_path, "w") as file:
            json.dump(data, file, indent=4)
        global shopData
        shopData = data
    except IOError as e:
        logger.error(f"Error: Failed to write to {json_file_path}\n{e}")


def edit_shop_config(key, value):
    if not isinstance(key, str):
        logger.error("Error: Invalid key access in shop config.")
        return
    config = read_shop_config()
    config[key] = value
    write_shop_config(config)


def construct_buttons(buttons):
    buttonList = []
    try:
        for button in buttons:
            buttonList.append(ActionForm.Button(button["title"], button["icon"]))
    except Exception as e:
        logger.error(f"Error: Invalid button format in shop config: {e}")
    return buttonList


def construct_categories(player: Player, categories):
    categoryList = []
    try:
        for category in categories:
            categoryList.append(
                ActionForm.Button(
                    category["title"],
                    category["icon"],
                    lambda p=player: enter_category(p, category),
                )
            )
    except Exception as e:
        logger.error(f"Error: Invalid category format in shop config: {e}")
    return categoryList


def construct_category(player: Player, category):
    buttonList = []
    try:
        if "subcategories" in category:
            for subcategory in category["subcategories"]:
                buttonList.append(
                    ActionForm.Button(
                        subcategory["title"],
                        subcategory["icon"],
                        lambda p=player: enter_category(p, subcategory),
                    ),
                )
        if "items" in category:
            for item in category["items"]:
                priceColor = "§2"
                price = item["price"]
                if "value" in item and item["price"] == 0:
                    price = item["value"]
                else:
                    if player_balance(player, item["currency"]) < item["price"]:
                        priceColor = "§4"
                buttonList.append(
                    ActionForm.Button(
                        f'{item["title"]} §8- {priceColor}${price}',
                        item["icon"],
                        lambda p=player, i=item: item_info(p, i, category),
                    )
                )
    except Exception as e:
        logger.error(f"Error: Invalid category format in shop config: {e}")
    return buttonList


### SHOP FUNCTIONALITY ###

shopData = read_shop_config()


def enter_category(player: Player, category) -> None:
    form = ActionForm(
        title=f"{category['title']}",
        content=replace_score_placeholders(player, shopData["content"]).format(
            balance=server_balance_fetch(player.name)
        ),
        buttons=construct_category(player, category),
    )
    form.add_button(
        "Back",
        "textures/ui/cancel.png",
        lambda p=player: open_shop(
            player.server.plugin_manager.get_plugin("EasyAsShops"), player
        ),
    )
    if form:
        player.send_form(form)


def item_info(player: Player, item, category) -> None:
    content = "\n§l§fItem Information§r\n"
    form = ActionForm(
        title=item["title"],
    )
    if item["price"] != 0:
        content += f"§7 - §aPrice: §f${item['price']}\n"
        form.add_button(
            "Buy", "textures/ui/confirm.png", lambda p=player: buy_item(p, item)
        )
    if "value" in item:
        content += f"§7 - §bValue: §f${item['value']}\n"
        form.add_button(
            "Sell",
            "textures/ui/icon_minecoin_9x9",
            lambda p=player: sell_item(p, item),
        )
    content += "\n"
    form.content = content
    form.add_button(
        "Back", "textures/ui/cancel.png", lambda p=player: enter_category(p, category)
    )
    if form:
        player.send_form(form)


def buy_item(player: Player, item) -> None:
    form = ModalForm(
        title=f"Transaction: {item['title']}",
        controls=[
            Slider(
                f"\n§7Use the slider to select an amount, or use the text box below.§f\n§eCurrency: §f{get_objective_display(player, item["currency"])} §7(§b{player_balance(player, item["currency"])}§7)\n\nAmount",
                1,
                64,
                1,
                1,
            ),
            TextInput("Amount", "1"),
        ],
        on_submit=lambda p=player, r=str: confirm_purchase(p, item, json.loads(r)),
    )
    if form:
        player.send_form(form)


def sell_item(player: Player, item) -> None:
    form = ModalForm(
        title=f"Transaction: {item['title']}",
        controls=[
            Slider(
                f"\n§7Use the slider to select an amount, or use the text box below.§f\n§eCurrency: §f{get_objective_display(player, item["currency"])} §7(§b{player_balance(player, item["currency"])}§7)\n\nAmount",
                1,
                64,
                1,
                1,
            ),
            TextInput("Amount", "1"),
        ],
        on_submit=lambda p=player, r=str: confirm_sell(p, item, json.loads(r)),
    )
    if form:
        player.send_form(form)


def confirm_purchase(player: Player, item, result) -> None:
    amount = int(result[0])
    if result[1] != "":
        if int(result[1]) > 1:
            amount = int(result[1])
    server = player.server
    coins = player_balance(player, item["currency"])
    if item["price"] * amount > coins:
        error_custom(player, "§cYou do not have enough money to buy this item.")
        return
    success = server.dispatch_command(
        server.command_sender,
        f'give "{player.name}" {item['item']} {amount}',
    )
    if not success:
        (
            error_custom(
                player,
                "§cInvalid item: §4" + item["item"] + "§c. Please contact an admin.",
            )
        )
        return
    player_deduct(player, item["currency"], (item["price"] * amount))
    send_custom(player, f"§bYou have bought §e{item['title']} §8x§7{amount}.")
    send_custom(
        player,
        f"§6Your balance is now §e${player_balance(player, item["currency"])}§6.",
    )


def confirm_sell(player: Player, item, result) -> None:
    amount = int(result[0])
    if result[1] != "":
        if int(result[1]) > 1:
            amount = int(result[1])
    server = player.server
    it = item["item"]
    am = str(amount)
    success = server.dispatch_command(
        server.command_sender,
        f'clear @a[name="{player.name}",hasitem='
        + "{item="
        + it
        + ",quantity="
        + am
        + "..2304}"
        + f"] {it} -1 {am}",
    )
    if not success:
        error_custom(player, "§cYou do not have enough items to sell.")
        return
    else:
        player_pay(player, item["currency"], item["value"] * amount)
        send_custom(player, f"§aYou have sold §e{item['title']} §8x§7{amount}.")
        send_custom(
            player,
            f"§6Your balance is now §e${player_balance(player, item["currency"])}§6.",
        )


def open_shop(self: Plugin, player: Player):
    try:
        form = ActionForm(
            title=shopData["title"],
            content=replace_score_placeholders(player, shopData["content"]).format(
                balance=server_balance_fetch(player.name)
            ),
            buttons=construct_categories(player, shopData["categories"]),
        )
    except KeyError as e:
        self.logger.error(f"Error: Missing key in content format string: {e}")
        return
    except ValueError as e:
        self.logger.error(f"Error: Invalid format string in content: {e}")
        return
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}")
        return
    if form:
        player.send_form(form)


def reset_shop(self: Plugin):
    write_shop_config(default_data)
    global shopData
    shopData = default_data
    self.logger.info("Shop configuration has been reset to default.")


def edit_shop(self: Plugin, player: Player):
    form = ActionForm(
        title="Edit Shop",
        content="What would you like to edit?",
        buttons=[
            ActionForm.Button(
                "Edit Title",
                "textures/ui/icon_minecoin_9x9",
                lambda p=player: edit_title(p),
            ),
            ActionForm.Button(
                "Edit Content",
                "textures/ui/icon_minecoin_9x9",
                lambda p=player: edit_content(p),
            ),
            ActionForm.Button(
                "Edit Categories",
                "textures/ui/icon_minecoin_9x9",
                lambda p=player: edit_categories(p),
            ),
        ],
    )
    if form:
        player.send_form(form)


def edit_title(player: Player) -> None:
    form = ModalForm(
        title="Edit Title",
        controls=[TextInput("Title", shopData["title"], shopData["title"])],
        on_submit=lambda p=player, r=str: edit_shop_config("title", json.loads(r)[0]),
    )
    if form:
        player.send_form(form)


def edit_content(player: Player) -> None:
    form = ModalForm(
        title="Edit Content",
        controls=[TextInput("Content", shopData["content"], shopData["content"])],
        on_submit=lambda p=player, r=str: edit_shop_config("content", json.loads(r)[0]),
    )
    if form:
        player.send_form(form)


def edit_categories(player: Player) -> None:
    form = ActionForm(
        title="Edit Categories",
        content="What would you like to do?",
        buttons=[
            ActionForm.Button(
                "Add Category",
                "textures/ui/icon_minecoin_9x9",
                lambda p=player: add_category(p),
            ),
            ActionForm.Button(
                "Remove Category",
                "textures/ui/icon_minecoin_9x9",
                lambda p=player: remove_category(p),
            ),
        ],
    )
    try:
        categories = shopData["categories"]
        for category in categories:
            form.add_button(
                category["title"],
                category["icon"],
                lambda p=player, c=category: edit_category(p, c),
            )
    except Exception as e:
        logger.error(f"Error: Invalid category format in shop config: {e}")

    if form:
        player.send_form(form)


def add_category(player: Player) -> None:
    form = ModalForm(
        title="Add Category",
        controls=[
            TextInput("Title", "Category Title"),
            TextInput("Icon", "textures/ui/icon_minecoin_9x9"),
        ],
        on_submit=lambda p=player, r=str: add_category_confirm(p, json.loads(r)),
    )
    if form:
        player.send_form(form)


def add_category_confirm(player: Player, result) -> None:
    category = {
        "title": result[0],
        "icon": result[1],
        "items": [],
    }
    shopData["categories"].append(category)
    write_shop_config(shopData)
    enter_category(player, category)
    send_custom(player, f"§aCategory §e{result[0]} §ahas been added.")


def remove_category(player: Player) -> None:
    form = ActionForm(title="Remove Category", content="Select a category to remove.")
    categories = shopData["categories"]
    for category in categories:
        form.add_button(
            category["title"],
            category["icon"],
            lambda p=player, c=category: remove_category_confirm(p, c),
        )
    if form:
        player.send_form(form)


def remove_category_confirm(player: Player, category) -> None:
    shopData["categories"].remove(category)
    write_shop_config(shopData)
    send_custom(player, f"§aCategory §e{category['title']} §ahas been removed.")


def edit_category(player: Player, category) -> None:
    form = ActionForm(
        title=f"Edit Category: {category['title']}",
        content="What would you like to do?",
        buttons=[
            ActionForm.Button(
                "Add Item",
                "textures/ui/icon_minecoin_9x9",
                lambda p=player: add_item(p, category),
            ),
            ActionForm.Button(
                "Remove Item",
                "textures/ui/icon_minecoin_9x9",
                lambda p=player: remove_item(p, category),
            ),
            ActionForm.Button(
                "Add Subcategory",
                "textures/ui/icon_minecoin_9x9",
                lambda p=player: add_subcategory(p, category),
            ),
            ActionForm.Button(
                "Remove Subcategory",
                "textures/ui/icon_minecoin_9x9",
                lambda p=player: remove_subcategory(p, category),
            ),
        ],
    )
    try:
        if "subcategories" in category:
            subcategories = category["subcategories"]
            for subcategory in subcategories:
                form.add_button(
                    subcategory["title"],
                    subcategory["icon"],
                    lambda p=player, s=subcategory: edit_category(p, s),
                )
        items = category["items"]
        for item in items:
            form.add_button(
                item["title"],
                item["icon"],
                lambda p=player, i=item: edit_item(p, i, category),
            )
    except Exception as e:
        logger.error(f"Error: Invalid item format in shop config: {e}")

    if form:
        player.send_form(form)


def add_item(player: Player, category) -> None:
    form = ModalForm(
        title="Add Item",
        controls=[
            TextInput("Item", "minecraft:stone"),
            TextInput("Title", "Display Title"),
            TextInput("Price\n§7(Use 0 to make it unpurchasable)", "0", "0"),
            TextInput("Value\n§7(Use 0 to make it unsellable)", "0", "0"),
            TextInput("Icon", "textures/.../___.png"),
            TextInput("Currency", "default", "default"),
        ],
        on_submit=lambda p=player, r=str: add_item_submit(p, category, json.loads(r)),
    )
    if form:
        player.send_form(form)


def add_item_submit(player: Player, category, result) -> None:
    try:
        item = {
            "item": result[0],
            "title": result[1],
            "price": int(result[2]),
            "value": int(result[3]),
            "category": category["title"],
            "icon": result[4],
            "currency": result[5],
        }
        if item["value"] == 0:
            item.pop("value")
        category["items"].append(item)
        write_shop_config(shopData)
        enter_category(player, category)
        send_custom(player, f"§aItem §e{result[1]} §ahas been added.")
    except Exception as e:
        logger.error(f"Error: Invalid item format in shop config: {e}")


def remove_item(player: Player, category) -> None:
    form = ActionForm(title="Remove Item", content="Select an item to remove.")
    items = category["items"]
    for item in items:
        form.add_button(
            item["title"],
            item["icon"],
            lambda p=player, i=item: remove_item_confirm(p, i, category),
        )
    if form:
        player.send_form(form)


def remove_item_confirm(player: Player, item, category) -> None:
    category["items"].remove(item)
    write_shop_config(shopData)
    enter_category(player, category)
    send_custom(player, f"§aItem §e{item['title']} §ahas been removed.")


def add_subcategory(player: Player, category) -> None:
    form = ModalForm(
        title="Add Subcategory",
        controls=[
            TextInput("Title", "Subcategory Title"),
            TextInput("Icon", "textures/ui/icon_minecoin_9x9"),
        ],
        on_submit=lambda p=player, r=str: add_subcategory_confirm(
            p, category, json.loads(r)
        ),
    )
    if form:
        player.send_form(form)


def add_subcategory_confirm(player: Player, category, result) -> None:
    subcategory = {
        "title": result[0],
        "icon": result[1],
        "items": [],
    }
    category["subcategories"].append(subcategory)
    write_shop_config(shopData)
    enter_category(player, category)
    send_custom(player, f"§aSubcategory §e{result[0]} §ahas been added.")


def remove_subcategory(player: Player, category) -> None:
    form = ActionForm(
        title="Remove Subcategory", content="Select a subcategory to remove."
    )
    subcategories = category["subcategories"]
    for subcategory in subcategories:
        form.add_button(
            subcategory["title"],
            subcategory["icon"],
            lambda p=player, s=subcategory: remove_subcategory_confirm(p, s, category),
        )
    if form:
        player.send_form(form)


def remove_subcategory_confirm(player: Player, subcategory, category) -> None:
    category["subcategories"].remove(subcategory)
    write_shop_config(shopData)
    send_custom(player, f"§aSubcategory §e{subcategory['title']} §ahas been removed.")


def edit_item(player: Player, item, category) -> None:
    form = ModalForm(
        title="Edit Item",
        controls=[
            TextInput("Item", item["item"], item["item"]),
            TextInput("Title", item["title"], item["title"]),
            TextInput("Price", str(item["price"]), str(item["price"])),
        ],
        on_submit=lambda p=player, r=str: edit_item_submit(
            p, item, category, json.loads(r)
        ),
    )
    if "value" in item:
        form.add_control(TextInput("Value", str(item["value"]), str(item["value"])))
    else:
        form.add_control(TextInput("Value", "0", "0"))
    form.add_control(TextInput("Icon", item["icon"], item["icon"]))
    form.add_control(TextInput("Currency", item["currency"], item["currency"]))
    if form:
        player.send_form(form)


def edit_item_submit(player: Player, item, category, result) -> None:
    try:
        item["item"] = result[0]
        item["title"] = result[1]
        item["price"] = int(result[2])
        item["value"] = int(result[3])
        item["icon"] = result[4]
        item["currency"] = result[5]
        if item["value"] == 0:
            item.pop("value")
        write_shop_config(shopData)
        enter_category(player, category)
        send_custom(player, f"§aItem §e{result[1]} §ahas been edited.")
    except Exception as e:
        logger.error(f"Error: Invalid item format in shop config: {e}")

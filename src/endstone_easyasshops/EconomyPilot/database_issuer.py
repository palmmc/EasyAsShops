import sqlite3
import pymysql

from endstone import ColorFormat
from pathlib import Path
import tomllib
import tomlkit
import os


# config loader
### DO NOT TOUCH :3 ###
def load_config():
    directory = "config"
    filename = "economy-pilot.toml"
    file_path = os.path.join(directory, filename)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    with open(file_path, "rb") as file:
        toml_data = tomllib.load(file)
        u_version = toml_data.get("version")
        u_currency_symbol = toml_data.get("currency_symbol")
        u_database_type = toml_data.get("database_type")

        u_database_host = toml_data.get("database_host")
        u_database_username = toml_data.get("database_username")
        u_database_password = toml_data.get("database_password")
        u_database_name = toml_data.get("database_name")

    return (
        u_version,
        u_currency_symbol,
        u_database_type,
        u_database_host,
        u_database_username,
        u_database_password,
        u_database_name,
    )


database_directory = "endstone"

config_data = load_config()
currency = config_data[1]

database_type = config_data[2]
database_host = config_data[3]
database_username = config_data[4]
database_password = config_data[5]
database_name = config_data[6]

directory_path = Path("databases/economy-pilot/")

### ^^^ DO NOT TOUCH THE STUFF ABOVE ^^^ ###


# this function fetches the amount of money the user has and returns it to the issuer
# INPUT - string
# OUTPUT - string (parse it yourself :P)
def fetch_balance(username):
    match database_type:
        case "sqlite":
            connection = sqlite3.connect(f"{directory_path}/database.db")
            cursor = connection.cursor()
            cursor.execute(
                "SELECT money FROM database WHERE username = ?;", (str(username),)
            )

            balance = (
                str(cursor.fetchone())
                .replace("(", "")
                .replace(")", "")
                .replace(",", "")
            )
            connection.commit()
            connection.close()

            return balance
        case "mysql":
            connection = pymysql.connect(
                host=database_host,
                user=database_username,
                password=database_password,
                database=database_name,
            )

            cursor = connection.cursor()
            cursor.execute(
                "SELECT money FROM database WHERE username = %s;", (str(username),)
            )

            balance = (
                str(cursor.fetchone())
                .replace("(", "")
                .replace(")", "")
                .replace(",", "")
            )
            connection.commit()
            connection.close()

            return balance


# this function sets the players balance
# INPUT - string, int
# OUTPUT - string (INFO MESSAGE)
def set_balance(username, balance) -> str:
    match database_type:
        case "sqlite":
            connection = sqlite3.connect(f"{directory_path}/database.db")
            cursor = connection.cursor()

            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM database WHERE username = ?)",
                (str(username),),
            )
            reciever_exists = int(cursor.fetchone()[0])
            if reciever_exists == 0:
                return_string = f"{ColorFormat.RED}This user isnt logged in the database{ColorFormat.RESET}"
                connection.close()
                return return_string

            return_message = f"{ColorFormat.GOLD}Player's {ColorFormat.GREEN}{username}{ColorFormat.RESET} {ColorFormat.GOLD}balance was set to {ColorFormat.AQUA}{balance}{currency}{ColorFormat.RESET}"

            cursor.execute(
                "UPDATE database SET money = ? WHERE username = ?;",
                (abs(int(balance)), str(username)),
            )

            connection.commit()
            connection.close()
            return return_message
        case "mysql":
            connection = pymysql.connect(
                host=database_host,
                user=database_username,
                password=database_password,
                database=database_name,
            )

            cursor = connection.cursor()

            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM database WHERE username = %s)",
                (str(username),),
            )
            reciever_exists = int(cursor.fetchone()[0])
            if reciever_exists == 0:
                return_string = f"{ColorFormat.RED}This user isnt logged in the database{ColorFormat.RESET}"
                connection.close()
                return return_string

            return_message = f"{ColorFormat.GOLD}Player's {ColorFormat.GREEN}{username}{ColorFormat.RESET} {ColorFormat.GOLD}balance was set to {ColorFormat.AQUA}{balance}{currency}{ColorFormat.RESET}"

            cursor.execute(
                "UPDATE database SET money = %s WHERE username = %s;",
                (abs(int(balance)), str(username)),
            )

            connection.commit()
            connection.close()
            return return_message


# it's like the /pay command but it can be sent from a non player, must be op though
# INPUT - string, int
# OUTPUT - string (INFO MESSAGE)
def server_pay(username, amount) -> str:
    match database_type:
        case "sqlite":
            connection = sqlite3.connect(f"{directory_path}/database.db")
            cursor = connection.cursor()

            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM database WHERE username = ?)",
                (str(username),),
            )
            reciever_exists = int(cursor.fetchone()[0])
            if reciever_exists == 0:
                return_string = f"{ColorFormat.RED}This user isnt logged in the database{ColorFormat.RESET}"
                connection.close()
                return return_string

            cursor.execute(
                "UPDATE database SET money = money + ? WHERE username = ?;",
                (abs(int(amount)), str(username)),
            )
            return_string = f"{ColorFormat.GOLD}The Server has sent {ColorFormat.AQUA}{abs(int(amount))}{currency}{ColorFormat.RESET}{ColorFormat.GOLD} to {ColorFormat.GREEN}{username}{ColorFormat.RESET}"

            connection.commit()
            connection.close()
            return return_string
        case "mysql":
            connection = pymysql.connect(
                host=database_host,
                user=database_username,
                password=database_password,
                database=database_name,
            )

            cursor = connection.cursor()

            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM database WHERE username = %s)",
                (str(username),),
            )
            reciever_exists = int(cursor.fetchone()[0])
            if reciever_exists == 0:
                return_string = f"{ColorFormat.RED}This user isnt logged in the database{ColorFormat.RESET}"
                connection.close()
                return return_string

            cursor.execute(
                "UPDATE database SET money = money + %s WHERE username = %s;",
                (abs(int(amount)), str(username)),
            )
            return_string = f"{ColorFormat.GOLD}The Server has sent {ColorFormat.AQUA}{abs(int(amount))}{currency}{ColorFormat.RESET}{ColorFormat.GOLD} to {ColorFormat.GREEN}{username}{ColorFormat.RESET}"

            connection.commit()
            connection.close()
            return return_string


# this command lets the server deduct from the player's balance
# INPUT - string, int
# OUTPUT - string (INFO MESSAGE)
def server_deduct(username, amount) -> str:
    match database_type:
        case "sqlite":
            connection = sqlite3.connect(f"{directory_path}/database.db")
            cursor = connection.cursor()

            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM database WHERE username = ?)",
                (str(username),),
            )
            reciever_exists = int(cursor.fetchone()[0])
            if reciever_exists == 0:
                return_string = f"{ColorFormat.RED}This user isnt logged in the database{ColorFormat.RESET}"
                connection.close()
                return return_string

            cursor.execute(
                "UPDATE database SET money = money - ? WHERE username = ?;",
                (abs(int(amount)), str(username)),
            )
            return_string = f"{ColorFormat.GOLD}The Server has deducted {ColorFormat.AQUA}{abs(int(amount))}{currency}{ColorFormat.RESET}{ColorFormat.GOLD} from {ColorFormat.GREEN}{username}{ColorFormat.RESET}"

            connection.commit()
            connection.close()
            return return_string
        case "mysql":
            connection = pymysql.connect(
                host=database_host,
                user=database_username,
                password=database_password,
                database=database_name,
            )

            cursor = connection.cursor()

            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM database WHERE username = %s)",
                (str(username),),
            )
            reciever_exists = int(cursor.fetchone()[0])
            if reciever_exists == 0:
                return_string = f"{ColorFormat.RED}This user isnt logged in the database{ColorFormat.RESET}"
                connection.close()
                return return_string

            cursor.execute(
                "UPDATE database SET money = money - %s WHERE username = %s;",
                (abs(int(amount)), str(username)),
            )
            return_string = f"{ColorFormat.GOLD}The Server has deducted {ColorFormat.AQUA}{abs(int(amount))}{currency}{ColorFormat.RESET}{ColorFormat.GOLD} from {ColorFormat.GREEN}{username}{ColorFormat.RESET}"

            connection.commit()
            connection.close()
            return return_string


# lets the server fetch the player's balance
# INPUT - string
# OUTPUT - string (has to be parsed to int)
def server_balance_fetch(username) -> str:
    match database_type:
        case "sqlite":
            connection = sqlite3.connect(f"{directory_path}/database.db")
            cursor = connection.cursor()

            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM database WHERE username = ?)",
                (str(username),),
            )
            reciever_exists = int(cursor.fetchone()[0])
            if reciever_exists == 0:
                return_string = f"{ColorFormat.RED}This user isnt logged in the database{ColorFormat.RESET}"
                connection.close()
                return return_string

            cursor.execute(
                "SELECT money FROM database WHERE username = ?;", (str(username),)
            )
            return_string = (
                str(cursor.fetchone())
                .replace("(", "")
                .replace(")", "")
                .replace(",", "")
            )
            connection.commit()
            connection.close()

            return return_string
        case "mysql":
            connection = sqlite3.connect(f"{directory_path}/database.db")
            cursor = connection.cursor()

            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM database WHERE username = ?)",
                (str(username),),
            )
            reciever_exists = int(cursor.fetchone()[0])
            if reciever_exists == 0:
                return_string = f"{ColorFormat.RED}This user isnt logged in the database{ColorFormat.RESET}"
                connection.close()
                return return_string

            cursor.execute(
                "SELECT money FROM database WHERE username = ?;", (str(username),)
            )
            return_string = (
                str(cursor.fetchone())
                .replace("(", "")
                .replace(")", "")
                .replace(",", "")
            )
            connection.commit()
            connection.close()

            return return_string

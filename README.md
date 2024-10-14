<a href="../../"><img src="./images/badge.png?raw=true" width="128"></a><br>
<a href="https://github.com/legitbox/Economy-Pilot"><img src="./images/badge2.png?raw=true" width="256"></a>
<br>
<div align="left">
  
[![view - Documentation](https://img.shields.io/badge/view-Documentation-blue?style=for-the-badge)](../../wiki/ "Go to project documentation")

</div>

# EasyAsShops
A plugin for [Endstone](https://github.com/EndstoneMC/endstone) that allows you to setup a simple server shop without any programming!

# Installation
1) Download [**EconomyPilot**](https://github.com/legitbox/Economy-Pilot) (without it, this plugin will not work).
2) Download the latest [release](../../releases).
3) Drag and drop both files ending with `.whl` into your Endstone plugin folder.
4) Restart or reload your server. Enjoy!

### Demo
<img src="./images/shopdemo.gif?raw=true">

# Features
- ## Shop UI
  - Category support.
  - Buy/sell items.
- ## Editor UI (Admin-Only)
  - Title & content configuration.
  - Categories
    - Add/remove/edit.
  - Items
    - Add/remove/edit.

# Commands
- `/editshop` - `easyas.command.editshop`
- `/resetshop` - `easyas.command.resetshop`
- `/shop` - `easyas.command.shop`

# Tutorial
### *Using In-Game UI*
1) With **operator** or the `easyas.command.editshop` permission, run the `/editshop` command.
2) This is the first layer of configuration, where you can edit things like the title and content of the UI.
   - Next click "Edit Categories"
3) Here you can add or remove a cateegory, or edit existing categories by clicking them.
   - Click the 'Blocks' category to edit it.
4) Now, inside this category, you can add or remove items and subcategories, as well as edit existing ones.
   - Try adding a new entry for diamonds; use the ID '`minecraft:diamond`', and the path "`textures/items/diamond.png`".
   - The rest you can choose!
5) Once you've done that, you will be taken to your new entry in the shop.
   - If you want, try buying one!
### *Using JSON Editor*
1) For more advanced users, a more efficient approach is to edit the JSON directly.
To start, navigate to your `/bedrock_server/config/` folder; the `/config/` folder should be in the same directory as your `/plugins/` folder.
2) Open `shop.json` in your choice of text editor. You don't need anything fancy; Notepad will do.
3) Begin editing. Refer to the [Wiki](../../wiki/Editing-with-JSON) for available arguments.
Once done, save the file and reload/restart your server for the changes to take effect.

### 🥳 Congratulations!
You've added your first item to the shop!
What will you add next? It's up to you! Have fun with it!

# Feature Roadmap
**Feature**|**Status**
:-----:|:-----:
Shop UI|✅
Category Support|✅
Buy/Sell Support|✅
Editor UI|✅
Reset command|✅
EconomyPilot Integration|✅
Scoreboard Currency Support|✅
Multi-Currency Support|✅
Documentation|🔷
Placeholder Support|🔷

✅ - Complete
🔷 - Work in Progress
🔶 - Planned

# Feedback
It's always possible that you will experience issues with this plugin, or have suggestions on how it can be improved.
When that happens, please create an [Issue](../../issues), so I can get to it when I have the chance!
I hope you enjoy using this plugin!

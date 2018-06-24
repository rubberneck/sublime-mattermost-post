# Sublime Mattermost Post
Posts selected text from [Sublime Text 3](https://www.sublimetext.com/) to [Mattermost](https://mattermost.com/)


## Install
Use [Package Control](https://packagecontrol.io/)


## Usage
Select some text (multi select works as well) then right click "Mattermost Post", ctrl+shift+p "Mattermost Post" or
[setup a keybinding](#keybindings) and use that.


## Settings
All settings execpt for [syntax_map](#settings-syntax_map) are required.

You can use ctrl+shift+p then "Preferences: Mattermost Post"

Example
```json
{
    "url": "mm.example.com",
    "team": "example",
    "channel": "mmpost",
    "pat": "",
    "post_fileinfo": true,
    "max_lines": 25,
    "syntax_map": {
        "Packages/C#/C#.sublime-syntax": "cs",
        "Packages/C++/C++.sublime-syntax": "cpp",
        "Packages/Objective-C/Objective-C.sublime-syntax": "objectivec",
    }
}
```

### Settings - pat
This is a [Personal Access Token](https://docs.mattermost.com/developer/personal-access-tokens.html)

### Settings - post_fileinfo
This will send the relative_path+filename and the line numbers.
```
Filename: test-data/test.py
Linenumbers: 12 - 13
```

### Settings - syntax_map
Since sublime returns a file for view.settings().get('syntax') the syntax is based on that file name.
```python
self.view.settings().get('syntax').split("/")[-1].rsplit(".")[0].split(" ")[0].lower()
```
However this is not always correct for example.
`Packages/PackageDev/Package/Sublime Text Settings/Sublime Text Settings.sublime-syntax` returns `sublime` since it is
the first word of the filename part.

To create your own syntax_map

Get current sublime text syntax of view bring up the console "ctrl-\`"
```
view.settings().get('syntax')
```
Then use one of the "Supported languages" from the
[Mattermost Code Block](https://docs.mattermost.com/help/messaging/formatting-text.html#code-block)
for syntax highliting.


## Keybindings
I don't set a default key binding.

You can use ctrl+shift+p then "Preferences: Mattermost Post Key Bindings"

Example
```json
[
    { "keys": [""], "command": "mattermost_post",
        "context": [
            { "key": "selection_empty", "operator": "equal", "operand": false }
        ],
    },
]
```

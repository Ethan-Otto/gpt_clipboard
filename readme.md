# GPT Clipboard

GPT Clipboard is a Python application that allows users to merge multiple Python files into a single file or copy the merged content to the clipboard. This tool is particularly useful for preparing code to be pasted into large language models like GPT for analysis or modification.

## Features

- Drag and drop Python files or folders containing Python files into the application
- Merge selected Python files into a single file
- Copy merged content to the clipboard
- Remove selected files from the list
- Clear the entire list of files

## Requirements

- Python 3.6+
- PyQt5

## Installation

1. Clone this repository or download the source code.
2. Install the required dependencies:

```
pip install PyQt5
```

## Usage

1. Run the application:

```
python gpt_clipboard.py
```

2. Drag and drop Python files or folders containing Python files into the application window.
3. Use the buttons at the bottom of the window to perform actions:
   - "Merge and Save": Merge the selected files and save the result to a new file.
   - "Merge and Copy to Clipboard": Merge the selected files and copy the result to the clipboard.
   - "Remove Selected": Remove the selected files from the list.
   - "Clear List": Remove all files from the list.

## How it works

1. The application uses PyQt5 to create a graphical user interface.
2. Users can drag and drop Python files or folders into the application window.
3. The application recursively searches for Python files in dropped folders.
4. When merging, the application combines the content of all selected files, adding separators with relative file paths between each file's content.
5. Users can choose to save the merged content to a file or copy it to the clipboard.

## Example: Folder Handling

Let's say you have a project structure like this:

```
my_project/
├── main.py
├── utils/
│   ├── helper.py
│   └── config.py
└── modules/
    ├── module1.py
    └── module2.py
```

When you drag and drop the `my_project` folder into GPT Clipboard, the application will:

1. Recursively search for all `.py` files in the folder and its subfolders.
2. Add all found Python files to the list:
   - `my_project/main.py`
   - `my_project/utils/helper.py`
   - `my_project/utils/config.py`
   - `my_project/modules/module1.py`
   - `my_project/modules/module2.py`

3. When you merge the files, the content will be combined with separators showing the relative paths:

```python
----main.py----

[Content of main.py]

----utils/helper.py----

[Content of helper.py]

----utils/config.py----

[Content of config.py]

----modules/module1.py----

[Content of module1.py]

----modules/module2.py----

[Content of module2.py]
```

This approach preserves the folder structure information, making it easier to understand the project layout when the merged content is used in a language model or saved as a single file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

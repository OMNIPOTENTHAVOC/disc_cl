```markdown
# Disk Cleaner

A lightweight and user-friendly disk cleaning tool built with Python and Tkinter.  
Designed for safe and efficient removal of duplicate and junk files across multiple directories. Includes powerful filtering and sorting capabilities inspired by classic Windows aesthetics.

---

## Features

- **Scan multiple folders** including custom selections and common Windows folders like Recent Items.
- **Duplicate detection** by computing SHA-256 hash of files.
- **Junk file identification** using configurable file extension lists.
- **Safe deletion** via moving files to the Recycle Bin (using [`send2trash`](https://pypi.org/project/Send2Trash/)).
- **Filtering options** by file type, minimum file size (in MB), and age (files older than X months).
- **Sorting results** by file name, file size, or last modified date.
- **Pause and resume** scan functionality.
- **Real-time progress display** showing total files scanned, scan rate (files/sec), and elapsed time.
- **File info preview** for selected files, including name, path, size, and modification date.
- **Log of deleted files** maintained in `deleted_files_log.txt` with timestamps.
- **Disk usage info** for selected drives.
- **GUI with classic Windows-inspired color scheme and layout.**
- **Help and About dialogs** available via menu.
- **Multi-selection for filtering file types.**

---

## Installation

1. **Clone the repository:**
   ```
   git clone https://github.com/yourusername/disk-cleaner.git
   cd disk-cleaner
   ```

2. **Install required dependencies:**
   ```
   pip install send2trash
   ```

3. **Run the application:**
   ```
   python disk_cleaner.py
   ```

---

## Usage

1. **Add folders to scan:** Use "Add Folder" or "Add Recent" buttons to select scan targets.

2. **Configure filters:**
   - Click "Scan Folder" to start scanning.
   - Use the "File Types" dropdown to select which file extensions to include.
   - Use the "Older Than" dropdown to limit files to those older than specified months.
   - Set minimum file size in MB to ignore small files.

3. **Manage scan:**
   - Pause or resume scanning at any time.
   - Monitor progress and stats in the progress bar and status label.

4. **Review scan results:**
   - Browse detected duplicates and junk files.
   - Sort results by name, size, or modification date.
   - View detailed information for selected files.

5. **Delete files:**
   - Select files to delete.
   - Confirm deletion; files are safely moved to the Recycle Bin.
   - Deletion logged in `deleted_files_log.txt`.

6. **Additional options:**
   - Configure junk file extensions to customize what counts as junk.
   - View disk usage statistics for any selected folder.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Author

Siddhansh Srivasta  
Contact: siddhansh@example.com

---

## Contributions

Feel free to fork, improve, and submit pull requests!  
Issues and feature requests are welcome.

---

## Acknowledgements

- Uses [`send2trash`](https://pypi.org/project/Send2Trash/) for safe deletion.  
- Inspired by classic Windows UI and user-friendly design principles.
```

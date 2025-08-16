# Disk Cleaner

A lightweight and user-friendly disk cleaning tool built with Python and Tkinter.  
Designed for safe and efficient removal of duplicate and junk files across multiple directories. Includes powerful filtering and sorting capabilities inspired by classic Windows aesthetics.

---

## Features

- **Scan multiple folders** including custom selections and common Windows folders like Recent Items.
- **Duplicate detection** using SHA-256 hash of files.
- **Junk file identification** with customizable extension lists.
- **Safe deletion** of files by sending them to the Recycle Bin using [`send2trash`](https://pypi.org/project/SendTrash/).
- **Filtering options** for file types, minimum file size (MB), and file age (months).
- **Sorting** scan results by file name, size, or last modified date.
- **Pause and resume** scanning to manage long operations.
- Real-time **scan progress** display including files per second and elapsed time.
- **File info preview** showing size, path, and modification date for selected files.
- Logging of deleted files with timestamps in `deleted_files_log.txt`.
- **Disk usage** overview for selected drives or folders.
- GUI styled with a **steel gray** color scheme and Windows-like design.
- **Multi-selection dropdowns** for flexible filtering.
- Help and about dialogs for guidance.

---

## Installation

1. Clone the repository:  
   ```
   git clone https://github.com/yourusername/disk-cleaner.git
   cd disk-cleaner
   ```

2. Install dependencies:  
   ```
   pip install send2trash
   ```

3. Run the application:  
   ```
   python disk_cleaner.py
   ```

---

## Usage

1. Add folders to scan using the "Add Folder" or "Add Recent" buttons.
2. Select desired file types and minimum age of files to include in deletion.
3. Set minimum file size (in MB) to focus on larger files.
4. Start the scan. Use pause and resume as needed.
5. Review detected duplicate and junk files in the list with options to sort by name, size, or date.
6. Select files to delete and confirm deletion. Files are safely sent to the Recycle Bin.
7. View system disk usage information anytime.
8. Configure junk file extensions to customize criteria for cleanup.

---

## Author

Siddhansh Srivastava
- sri.siddhansh@gmail.com
- github.com/OMNIPOTENTHAVOC

---

## Contributions

Contributions are welcome! Feel free to fork, open issues, and submit pull requests to improve the project.

---

## Acknowledgments

- Built using the [`send2trash`](https://pypi.org/project/SendTrash/) package for safe file deletion.
- Interface inspired by classic Windows styling and usability principles.

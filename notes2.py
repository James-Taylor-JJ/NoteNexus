
import sys
from pathlib import Path


def setup():
    # Initialize the notes application.
    # Define the notes directory in HOME
    notes_dir = Path.home() / ".notes"

    # Check if notes directory exists
    if not notes_dir.exists():
        # For CLI version, we don't automatically create it
        pass

    return notes_dir

# Make sure a filename/id was supplied
# Look for that note in the notes directory
# Open the file
# Show Its Metadata and Content
# Print a Useful Error If the File Is Missing

#Read and Display a Specific Note
def read_note(notes_dir, note_id=None):
    
    # Check if notes directory exists
    if not notes_dir.exists():
        print(f"Error: Notes directory does not exist: {notes_dir}", file=sys.stderr)
        print("Create it with: mkdir -p ~/.notes/notes", file=sys.stderr)
        print("Then copy test notes: cp test-notes/*.md ~/.notes/notes/", file=sys.stderr)
        return False

    # Look for notes in the notes directory (or directly in .notes)
    notes_subdir = notes_dir / "notes"
    search_dirs = [notes_subdir] if notes_subdir.exists() else [notes_dir]

    # Find all note files (*.md, *.note, *.txt)
    note_files = []
    for search_dir in search_dirs:
        note_files.extend(search_dir.glob("*.md"))
        note_files.extend(search_dir.glob("*.note"))
        note_files.extend(search_dir.glob("*.txt"))

    if not note_files:
        print(f"No notes found in {notes_dir}")
        print("Copy test notes with: cp test-notes/*.md ~/.notes/notes/", file=sys.stderr)
        return False

    # If no note was specified, ask for one after showing the list
    if not note_id:
        print("Please specify a note.\n")
        print("Available notes:")
        print("=" * 60)
        for note_file in sorted(note_files):
            metadata = parse_yaml_header(note_file)
            title = metadata.get("title", note_file.name)
            print(f"{note_file.name}  -  {title}")

        note_id = input("\nEnter file name: ").strip()

        if not note_id:
            print("Error: No note selected.", file=sys.stderr)
            return False

    # Find the requested note
    note_file = None
    for candidate in note_files:
        if candidate.name == note_id:
            note_file = candidate
            break

    if note_file is None:
        print(f"Error: Note not found: {note_id}", file=sys.stderr)
        print("\nAvailable notes:")
        print("=" * 60)
        for candidate in sorted(note_files):
            metadata = parse_yaml_header(candidate)
            title = metadata.get("title", candidate.name)
            print(f"{candidate.name}  -  {title}")
        return False

    try:
        metadata = parse_yaml_header(note_file)

        with open(note_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        content_start = 0
        if lines and lines[0].strip() == "---":
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    content_start = i + 1
                    break

        content = "".join(lines[content_start:]).strip()

        print("=" * 60)
        print(f"File: {note_file.name}")
        print(f"Title: {metadata.get('title', note_file.name)}")
        print(f"Author: {metadata.get('author', 'N/A')}")
        print(f"Created: {metadata.get('created', 'N/A')}")
        print(f"Modified: {metadata.get('modified', 'N/A')}")
        print(f"Tags: {metadata.get('tags', '')}")
        print("=" * 60)
        print(content)

        return True

    except Exception as e:
        print(f"Error reading note '{note_id}': {e}", file=sys.stderr)
        return False

#Parse YAML front matter from a note file. Returns a dictionary with metadata and the content.
def parse_yaml_header(file_path):
   
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Check if file starts with YAML front matter
        if not lines or lines[0].strip() != '---':
            return {'title': file_path.name, 'file': file_path.name}

        # Find the closing ---
        yaml_end = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                yaml_end = i
                break

        if yaml_end == -1:
            return {'title': file_path.name, 'file': file_path.name}

        # Parse YAML lines (simple parsing for basic key: value pairs)
        metadata = {'file': file_path.name}
        for line in lines[1:yaml_end]:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                metadata[key] = value

        return metadata

    except Exception as e:
        return {'title': file_path.name, 'file': file_path.name, 'error': str(e)}

#List all notes in the notes directory.
def list_notes(notes_dir):
    # Check if notes directory exists
    if not notes_dir.exists():
        print(f"Error: Notes directory does not exist: {notes_dir}", file=sys.stderr)
        print("Create it with: mkdir -p ~/.notes/notes", file=sys.stderr)
        print("Then copy test notes: cp test-notes/*.md ~/.notes/notes/", file=sys.stderr)
        return False

    # Look for notes in the notes directory (or directly in .notes)
    notes_subdir = notes_dir / "notes"
    search_dirs = [notes_subdir] if notes_subdir.exists() else [notes_dir]

    # Find all note files (*.md, *.note, *.txt)
    note_files = []
    for search_dir in search_dirs:
        note_files.extend(search_dir.glob("*.md"))
        note_files.extend(search_dir.glob("*.note"))
        note_files.extend(search_dir.glob("*.txt"))

    if not note_files:
        print(f"No notes found in {notes_dir}")
        print("Copy test notes with: cp test-notes/*.md ~/.notes/", file=sys.stderr)
        return True

    # Parse and display notes
    print(f"Notes in {notes_dir}:")
    print("=" * 60)

    for note_file in sorted(note_files):
        metadata = parse_yaml_header(note_file)
        title = metadata.get('title', note_file.name)
        created = metadata.get('created', 'N/A')
        tags = metadata.get('tags', '')

        print(f"\n{note_file.name}")
        print(f"  Title: {title}")
        if created != 'N/A':
            print(f"  Created: {created}")
        if tags:
            print(f"  Tags: {tags}")

    print(f"\n{len(note_files)} note(s) found.")
    return True

#Display help information.
def show_help():
   
    help_text = """
Future Proof Notes Manager v0.1

Usage: notes1.py [command]

Available commands:
  help         - Display this help information
  list         - List all notes in the notes directory
  read <id>    - Display a specific note

Notes directory: {}

Setup:
  To test the 'list' command, copy sample notes:
    mkdir -p ~/.notes/notes
    cp test-notes/*.md ~/.notes/notes/
    """.format(Path.home() / ".notes")
    print(help_text.strip())

#Clean up and exit the application.
def finish(exit_code=0):
    sys.exit(exit_code)

#Main entry point for the notes CLI application.
def main():
    # Setup
    notes_dir = setup()

    # Parse command-line arguments
    if len(sys.argv) < 2:
        # No command provided
        print("Error: No command provided.", file=sys.stderr)
        print("Usage: notes1.py [command]", file=sys.stderr)
        print("Try 'notes1.py help' for more information.", file=sys.stderr)
        finish(1)

    command = sys.argv[1].lower()

    # Process command
    if command == "help":
        show_help()
        finish(0)
    elif command == "list":
        success = list_notes(notes_dir)
        finish(0 if success else 1)
    elif command == "read":
        if len(sys.argv) < 3:
            print("Error: No note ID provided.", file=sys.stderr)
            print("Usage: notes2.py read <note-id>", file=sys.stderr)
            finish(1)

        note_id = sys.argv[2]
        success = read_note(notes_dir, note_id)
        finish(0 if success else 1)
    else:
        print(f"Error: Unknown command '{command}'", file=sys.stderr)
        print("Try 'notes2.py help' for more information.", file=sys.stderr)
        finish(1)


if __name__ == "__main__":
    main()

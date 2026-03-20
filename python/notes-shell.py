#!/usr/bin/env python3
"""
Future Proof Notes Manager - Version Zero
A personal notes manager using text files with YAML headers.
"""

import os
import sys
from pathlib import Path

"""Initialize the notes application."""
def setup():
    print("Future Proof Notes Manager v0.0")
    print("=" * 40)

    # Define the notes directory in HOME
    notes_dir = Path.home() / ".notes"

    # Check if notes directory exists
    if not notes_dir.exists():
        print(f"Notes directory not found at {notes_dir}")
        print("Run 'notes init' to create it.")
    else:
        print(f"Notes directory: {notes_dir}")

    print()
    return notes_dir

"""Extract YAML metadata from a note file."""
def parse_yaml_header(file_path):
    metadata = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if lines and lines[0].strip() == "---":
            for line in lines[1:]:
                line = line.strip()
                if line == "---":
                    break
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()
    except Exception as e:
        metadata["error"] = str(e)
    return metadata


def get_note_files(notes_dir):
    if not notes_dir.exists():
        return []

    notes_subdir = notes_dir / "notes"
    search_dirs = [notes_subdir] if notes_subdir.exists() else [notes_dir]

    note_files = []
    for search_dir in search_dirs:
        note_files.extend(search_dir.glob("*.md"))
        note_files.extend(search_dir.glob("*.note"))
        note_files.extend(search_dir.glob("*.txt"))

    return sorted(note_files)

"""List all notes."""
def list_notes(notes_dir):
    note_files = get_note_files(notes_dir)
    if not note_files:
        print("No notes found.")
        return False
    print("Available notes:")
    print("=" * 60)
    for note_file in note_files:
        metadata = parse_yaml_header(note_file)
        title = metadata.get("title", note_file.name)
        print(f"{note_file.name}  -  {title}")
    return True

"""Read and display a note."""
def read_note(notes_dir, note_id=None):
    note_files = get_note_files(notes_dir)
    if not note_files:
        print("No notes found.")
        return False
    if not note_id:
        print("Please specify a note.\n")
        list_notes(notes_dir)
        note_id = input("\nEnter file name: ").strip()
    if not note_id:
        print("Error: No note selected.")
        return False
    note_file = None
    for candidate in note_files:
        if candidate.name == note_id:
            note_file = candidate
            break
    if note_file is None:
        print(f"Error: Note not found: {note_id}")
        print()
        list_notes(notes_dir)
        return False

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

"""Delete a note."""
def delete_note(notes_dir, note_id=None):
    note_files = get_note_files(notes_dir)
    if not note_files:
        print("No notes found.")
        return False
    
    if not note_id:
        print("Please specify a note.\n")
        list_notes(notes_dir)
        note_id = input("\nEnter a file name: ").strip()

    if not note_id:
        print("Error: No note selected.")
        return False

    note_file = None
    for candidate in note_files:
        if candidate.name == note_id:
            note_file = candidate
            break

    if note_file is None:
        print(f"Error: Note not found: {note_id}")
        print()
        list_notes(notes_dir)
        note_id = input("\nEnter a file name: ").strip()

        if not note_id:
            print("Error: No note selected.")
            return False

        for candidate in note_files:
            if candidate.name == note_id:
                note_file = candidate
                break

        if note_file is None:
            print(f"Error: Note not found: {note_id}")
            return False

    confirmation = input(f"Are you sure you'd like to delete {note_file.name}? (Y/N) ").strip().upper()
    if confirmation == "Y":
        note_file.unlink()
        print(f"{note_file.name} has been deleted.")
        return True
    else:
        print("Operation cancelled.")
        return False

"""Display help information."""
def show_help():
    help_text = """
Available commands:
  help          - Display this help information
  list          - List all notes
  read <id>     - Read a note
  delete <id>   - Delete a note
  create        - Create a new note
  edit <id>     - Edit a note
  quit          - Exit the application
    """
    print(help_text)

"""Main command loop for processing user input."""
def command_loop(notes_dir):
    while True:
        try:
            command_line = input("notes> ").strip()

            if not command_line:
                continue

            parts = command_line.split(maxsplit=1)
            command = parts[0].lower()
            note_id = parts[1] if len(parts) > 1 else None

            if command == "quit":
                break
            elif command == "help":
                show_help()
            elif command == "list":
                list_notes(notes_dir)
            elif command == "read":
                read_note(notes_dir, note_id)
            elif command == "delete":
                delete_note(notes_dir, note_id)
            else:
                print(f"Unknown command: '{command}'")
                print("Type 'help' for available commands.")

        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print("\nUse 'quit' to exit.")

"""Clean up and exit the application."""
def finish():
    print("\nGoodbye!")
    sys.exit(0)

"""Main entry point for the notes application."""
def main():
    notes_dir = setup()
    command_loop(notes_dir)
    finish()


if __name__ == "__main__":
    main()
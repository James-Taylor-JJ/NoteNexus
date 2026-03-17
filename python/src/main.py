import sys
from pathlib import Path

"""Initialize the notes application."""
def setup():
    # Define the notes directory in HOME
    notes_dir = Path.home() / ".notes"
    # Check if notes directory exists (silent check for CLI version)
    if not notes_dir.exists():
        # For CLI version, we don't automatically display this
        # It will be shown if needed by specific commands
        pass
    return notes_dir

"""Display help information."""
def show_help():
    help_text = """""
Future Proof Notes Manager v0.0

Usage: notes0.py [command]

Available commands:
  help          - Display this help information
  list          - List all notes 
  read <id>     - Read a Note
  delete <id>   - Delete a Note
  create        - Create a new note
  edit <id>     - Edit a note

Notes directory: {~/.notes/notes}
    """.format(Path.home() / ".notes")
    print(help_text.strip())

"""Clean up and exit the application."""
def finish(exit_code=0):
    sys.exit(exit_code)

"""Main entry point for the notes CLI application."""
def main():
    # Setup
    notes_dir = setup()
    # Parse command-line arguments
    if len(sys.argv) < 2:
        # No command provided
        print("Error: No command provided.", file=sys.stderr)
        print("Usage: notes0.py [command]", file=sys.stderr)
        print("Try 'notes0.py help' for more information.", file=sys.stderr)
        finish(1)

    command = sys.argv[1].lower()

    # Process command
    if command == "help":
        show_help()
        finish(0)
    else:
        print(f"Error: Unknown command '{command}'", file=sys.stderr)
        print("Try 'notes0.py help' for more information.", file=sys.stderr)
        finish(1)


if __name__ == "__main__":
    main()
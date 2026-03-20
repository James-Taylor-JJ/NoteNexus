from repositories.note_repo_class import NoteRepository
from services.note_service_class import NoteService


class ShellApp:
    def __init__(self, service: NoteService, repository: NoteRepository):
        self.service = service
        self.repository = repository

    def show_help(self):
        print("""
Available commands:
  help          - Display this help information
  list          - List all notes
  read <id>     - Read a note
  delete <id>   - Delete a note
  create [id]   - Create a new note
  edit <id>     - Edit a note
  quit          - Exit the application
""")

    def display_note(self, note):
        print("=" * 60)
        print(f"File: {note.filename}")
        print(f"Title: {note.title}")
        print(f"Author: {note.author}")
        print(f"Created: {note.created}")
        print(f"Modified: {note.modified}")
        print(f"Tags: {', '.join(note.tags)}")
        print("=" * 60)
        print(note.content)

    def handle_list(self):
        notes = self.service.list_notes()
        if not notes:
            print("No notes found.")
            return
        print("Available notes:")
        print("=" * 60)
        for note in notes:
            print(f"{note.filename}  -  {note.title}")

    def handle_read(self, filename=None):
        if not filename:
            print("Please specify a note.\n")
            self.handle_list()
            filename = input("\nEnter file name: ").strip()

        if not filename:
            print("Error: No note selected.")
            return

        note = self.service.read_note(filename)
        if not note:
            print(f"Error: Note not found: {filename}")
            return

        self.display_note(note)

    def handle_create(self, filename=None):
        if not filename:
            filename = input("Enter file name (example: my-note.md): ").strip()

        if not filename:
            print("Error: No file name provided.")
            return

        title = input("Title: ").strip()
        author = input("Author: ").strip()

        print("Enter note content. Type 'END' on its own line to finish.")
        lines = []
        while True:
            line = input()
            if line == "END":
                break
            lines.append(line)

        content = "\n".join(lines)

        try:
            note = self.service.create_note(filename, title, author, content)
            print(f"Note created: {note.filename}")
        except ValueError as e:
            print(f"Error: {e}")

    def handle_edit(self, filename=None):
        if not filename:
            print("Please specify a note.\n")
            self.handle_list()
            filename = input("\nEnter file name: ").strip()

        if not filename:
            print("Error: No note selected.")
            return

        note = self.service.read_note(filename)
        if not note:
            print(f"Error: Note not found: {filename}")
            return

        print("Enter new content. Type 'END' on its own line to finish.")
        print("Leave blank and type END to keep current content.")
        lines = []
        while True:
            line = input()
            if line == "END":
                break
            lines.append(line)

        new_content = "\n".join(lines).strip() or note.content
        updated = self.service.edit_note(filename, new_content)
        if updated:
            print(f"Note updated: {updated.filename}")

    def handle_delete(self, filename=None):
        if not filename:
            print("Please specify a note.\n")
            self.handle_list()
            filename = input("\nEnter file name: ").strip()

        if not filename:
            print("Error: No note selected.")
            return

        note = self.service.read_note(filename)
        if not note:
            print(f"Error: Note not found: {filename}")
            return

        confirmation = input(f"Are you sure you'd like to delete {note.filename}? (Y/N) ").strip().upper()
        if confirmation == "Y":
            deleted = self.service.delete_note(filename)
            if deleted:
                print(f"{filename} has been deleted.")
        else:
            print("Operation cancelled.")

    def run(self):
        print("Future Proof Notes Manager")
        print("=" * 40)
        print(f"Notes directory: {self.repository.notes_home}")
        print()

        while True:
            try:
                command_line = input("notes> ").strip()
                if not command_line:
                    continue

                parts = command_line.split(maxsplit=1)
                command = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else None

                if command == "quit":
                    print("\nGoodbye!")
                    break
                elif command == "help":
                    self.show_help()
                elif command == "list":
                    self.handle_list()
                elif command == "read":
                    self.handle_read(arg)
                elif command == "create":
                    self.handle_create(arg)
                elif command == "edit":
                    self.handle_edit(arg)
                elif command == "delete":
                    self.handle_delete(arg)
                else:
                    print(f"Unknown command: '{command}'")
                    print("Type 'help' for available commands.")
            except EOFError:
                print("\nGoodbye!")
                break
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit.")
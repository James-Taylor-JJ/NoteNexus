from repositories.note_repo_class import NoteRepository
from services.note_service_class import NoteService
from ui.shell_app import ShellApp


def main():
    repository = NoteRepository()
    service = NoteService(repository)
    app = ShellApp(service, repository)
    app.run()


if __name__ == "__main__":
    main()
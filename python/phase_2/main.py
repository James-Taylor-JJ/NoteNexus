from phase_2.repositories.note_repo_class import NoteRepository
from phase_2.services.note_service_class import NoteService
from phase_2.ui.shell_app import ShellApp


def main():
    repository = NoteRepository()
    service = NoteService(repository)
    app = ShellApp(service, repository)
    app.run()


if __name__ == "__main__":
    main()
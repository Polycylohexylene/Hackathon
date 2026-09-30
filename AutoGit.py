import difflib
import getpass
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

from git import Actor, InvalidGitRepositoryError, NoSuchPathError, Repo


# The directory containing this Python script
APP_DIR = Path(__file__).resolve().parent

# The Git repository is the same directory as the script
REPOSITORY_DIR = APP_DIR

# The document managed by this demo
DOCUMENT_PATH = APP_DIR / "document.txt"


class GitDocumentEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Local Git Document Editor")
        self.root.geometry("1000x700")

        self.repository = None
        self.create_or_open_repository()
        self.create_user_interface()
        self.load_current_document()

    def create_or_open_repository(self):
        """
        Open the Git repository in the same directory as this script.

        If no repository exists, create one automatically.
        """

        try:
            self.repository = Repo(REPOSITORY_DIR)

            if self.repository.bare:
                raise InvalidGitRepositoryError(
                    "Bare repositories are not supported."
                )

        except (InvalidGitRepositoryError, NoSuchPathError):
            self.repository = Repo.init(REPOSITORY_DIR)

        # Create the document if it does not exist yet
        if not DOCUMENT_PATH.exists():
            DOCUMENT_PATH.write_text(
                "This is the first version of the document.\n",
                encoding="utf-8",
            )

        # Add and commit the initial document if the repository has no commits
        if not self.has_commits():
            self.repository.index.add(["document.txt"])

            actor = self.get_local_actor()

            self.repository.index.commit(
                "Created document",
                author=actor,
                committer=actor,
            )

    def has_commits(self):
        try:
            self.repository.head.commit
            return True
        except ValueError:
            return False

    def get_local_actor(self):
        """
        Try to obtain the local operating-system username.

        The email is intentionally empty if it cannot be determined.
        Git may still require an email depending on the local Git setup,
        so a local.invalid fallback is used only when necessary.
        """

        try:
            username = getpass.getuser()
        except Exception:
            username = ""

        if not username:
            username = "Unknown user"

        email = f"{username}@local.invalid"

        return Actor(username, email)

    def create_user_interface(self):
        controls = ttk.Frame(self.root, padding=10)
        controls.pack(fill="x")

        self.save_button = ttk.Button(
            controls,
            text="Commit Changes",
            command=self.commit_changes,
        )
        self.save_button.pack(side="left", padx=(0, 10))

        self.history_button = ttk.Button(
            controls,
            text="View History",
            command=self.show_history,
        )
        self.history_button.pack(side="left", padx=(0, 10))

        self.reload_button = ttk.Button(
            controls,
            text="Reload Current Version",
            command=self.load_current_document,
        )
        self.reload_button.pack(side="left")

        self.status_label = ttk.Label(
            self.root,
            text=f"Repository: {REPOSITORY_DIR}",
            padding=(10, 0),
        )
        self.status_label.pack(anchor="w")

        self.document_label = ttk.Label(
            self.root,
            text=f"Editing: {DOCUMENT_PATH.name}",
            padding=(10, 5),
        )
        self.document_label.pack(anchor="w")

        editor_frame = ttk.Frame(self.root, padding=10)
        editor_frame.pack(fill="both", expand=True)

        self.text_editor = tk.Text(
            editor_frame,
            wrap="word",
            undo=True,
            font=("Consolas", 12),
        )
        self.text_editor.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            editor_frame,
            orient="vertical",
            command=self.text_editor.yview,
        )
        scrollbar.pack(side="right", fill="y")

        self.text_editor.configure(
            yscrollcommand=scrollbar.set
        )

    def load_current_document(self):
        try:
            content = DOCUMENT_PATH.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            messagebox.showerror(
                "Unsupported document",
                "document.txt must be a UTF-8 text file.",
            )
            return

        self.replace_editor_content(content)

        self.status_label.config(
            text=f"Repository: {REPOSITORY_DIR} | Current document loaded"
        )

    def replace_editor_content(self, content):
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", content)

    def commit_changes(self):
        new_content = self.text_editor.get("1.0", tk.END)

        try:
            DOCUMENT_PATH.write_text(
                new_content,
                encoding="utf-8",
            )

            self.repository.index.add(["document.txt"])

            if not self.repository.is_dirty(
                index=True,
                working_tree=True,
                untracked_files=True,
            ):
                messagebox.showinfo(
                    "No changes",
                    "There are no changes to commit.",
                )
                return

            commit_message = simpledialog.askstring(
                "Describe the change",
                "What changed in this version?",
                initialvalue="Updated document",
                parent=self.root,
            )

            if not commit_message:
                commit_message = "Updated document"

            actor = self.get_local_actor()

            commit = self.repository.index.commit(
                commit_message,
                author=actor,
                committer=actor,
            )

            self.status_label.config(
                text=(
                    f"Repository: {REPOSITORY_DIR} | "
                    f"Saved version {commit.hexsha[:8]}"
                )
            )

            messagebox.showinfo(
                "Version saved",
                (
                    "The document was committed successfully.\n\n"
                    f"Description: {commit_message}\n"
                    f"User: {actor.name}"
                ),
            )

        except Exception as error:
            messagebox.showerror(
                "Could not save version",
                str(error),
            )

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Document History")
        history_window.geometry("1100x700")

        history_window.columnconfigure(0, weight=1)
        history_window.columnconfigure(1, weight=3)
        history_window.rowconfigure(1, weight=1)

        ttk.Label(
            history_window,
            text="Previous versions",
            padding=10,
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            history_window,
            text="Changes compared with the current document",
            padding=10,
        ).grid(row=0, column=1, sticky="w")

        # Version list
        versions_frame = ttk.Frame(history_window, padding=10)
        versions_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
        )

        versions_frame.rowconfigure(0, weight=1)
        versions_frame.columnconfigure(0, weight=1)

        version_list = tk.Listbox(
            versions_frame,
            width=40,
            exportselection=False,
        )
        version_list.grid(row=0, column=0, sticky="nsew")

        version_scrollbar = ttk.Scrollbar(
            versions_frame,
            orient="vertical",
            command=version_list.yview,
        )
        version_scrollbar.grid(row=0, column=1, sticky="ns")

        version_list.configure(
            yscrollcommand=version_scrollbar.set
        )

        # Preview area
        preview_frame = ttk.Frame(history_window, padding=10)
        preview_frame.grid(
            row=1,
            column=1,
            sticky="nsew",
        )

        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)

        preview = tk.Text(
            preview_frame,
            wrap="none",
            font=("Consolas", 11),
        )
        preview.grid(row=0, column=0, sticky="nsew")

        preview_scrollbar = ttk.Scrollbar(
            preview_frame,
            orient="vertical",
            command=preview.yview,
        )
        preview_scrollbar.grid(row=0, column=1, sticky="ns")

        preview.configure(
            yscrollcommand=preview_scrollbar.set,
            state="disabled",
        )

        # Colors for the change preview
        preview.tag_configure(
            "added",
            foreground="#087f23",
            background="#d9fdd3",
        )

        preview.tag_configure(
            "removed",
            foreground="#a40000",
            background="#ffd6d6",
        )

        preview.tag_configure(
            "unchanged",
            foreground="#333333",
        )

        preview.tag_configure(
            "heading",
            foreground="#555555",
            font=("Consolas", 11, "bold"),
        )

        commits = list(self.repository.iter_commits())

        if not commits:
            version_list.insert(tk.END, "No versions found")
            return

        # Read the current working document
        current_content = DOCUMENT_PATH.read_text(
            encoding="utf-8"
        )

        current_lines = current_content.splitlines(
            keepends=True
        )

        # Store commit objects in the same order as the list
        selected_commits = []

        for index, commit in enumerate(commits):
            selected_commits.append(commit)

            date = commit.committed_datetime.strftime(
                "%Y-%m-%d %H:%M"
            )

            author = commit.author.name or "Unknown user"
            message = commit.message.strip()

            list_entry = (
                f"{index + 1}. {date} | "
                f"{author} | {message}"
            )

            version_list.insert(tk.END, list_entry)

        def get_version_content(commit):
            try:
                return (
                    commit.tree / "document.txt"
                ).data_stream.read().decode("utf-8")
            except Exception:
                return ""

        def show_selected_preview(event=None):
            selection = version_list.curselection()

            if not selection:
                return

            selected_commit = selected_commits[selection[0]]
            old_content = get_version_content(selected_commit)

            old_lines = old_content.splitlines(
                keepends=True
            )

            differences = difflib.ndiff(
                old_lines,
                current_lines,
            )

            preview.config(state="normal")
            preview.delete("1.0", tk.END)

            preview.insert(
                tk.END,
                f"Selected version: "
                f"{selected_commit.hexsha[:10]}\n",
                "heading",
            )
            preview.insert(
                tk.END,
                "Green lines were added in the current version.\n"
                "Red lines existed in the selected older version.\n\n",
                "heading",
            )

            for line in differences:
                marker = line[:2]
                text = line[2:]

                if marker == "+ ":
                    preview.insert(
                        tk.END,
                        f"+ {text}",
                        "added",
                    )
                elif marker == "- ":
                    preview.insert(
                        tk.END,
                        f"- {text}",
                        "removed",
                    )
                elif marker == "  ":
                    preview.insert(
                        tk.END,
                        f"  {text}",
                        "unchanged",
                    )

            preview.config(state="disabled")

        def load_selected_version():
            selection = version_list.curselection()

            if not selection:
                messagebox.showinfo(
                    "Select a version",
                    "Select a version first.",
                    parent=history_window,
                )
                return

            selected_commit = selected_commits[selection[0]]
            old_content = get_version_content(selected_commit)

            confirmation = messagebox.askyesno(
                "Load older version",
                (
                    "Load this older version into the editor?\n\n"
                    "Your current unsaved editor contents will be replaced."
                ),
                parent=history_window,
            )

            if not confirmation:
                return

            self.replace_editor_content(old_content)

            self.status_label.config(
                text=(
                    f"Loaded historical version "
                    f"{selected_commit.hexsha[:8]} "
                    f"into the editor"
                )
            )

            history_window.destroy()

        version_list.bind(
            "<<ListboxSelect>>",
            show_selected_preview,
        )

        buttons = ttk.Frame(history_window, padding=10)
        buttons.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="e",
        )

        ttk.Button(
            buttons,
            text="Load Selected Version",
            command=load_selected_version,
        ).pack(side="right", padx=(10, 0))

        ttk.Button(
            buttons,
            text="Close",
            command=history_window.destroy,
        ).pack(side="right")

        version_list.selection_set(0)
        version_list.event_generate("<<ListboxSelect>>")


def main():
    root = tk.Tk()
    GitDocumentEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()

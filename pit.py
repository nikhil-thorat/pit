from os import path
import json
from datetime import datetime
from rich import print as rich_print

from filesystem import FileSystem
from utils import generate_hash, format_date


class Pit:

    def __init__(self, pit_path="."):
        self.pit_path = path.join(pit_path, ".pit")
        self.objects_path = path.join(self.pit_path, "objects")
        self.head_path = path.join(self.pit_path, "HEAD")
        self.index_path = path.join(self.pit_path, "index")

    def initialize(self):
        try:
            FileSystem.create_directory(self.pit_path)
            FileSystem.create_directory(self.objects_path)
            FileSystem.write_file(self.head_path, "")
            FileSystem.write_file(self.index_path, "[]")
            rich_print(f"[green]Success : Initialized pit {self.pit_path}.[/green]")
            print("\n")

        except PermissionError:
            rich_print(
                f"[red]Error : Permission denied. Unable to create or access pit {self.pit_path}.[/red]"
            )
        except OSError:
            rich_print(
                "[yellow]Warning : Unable to initialize pit or pit already exists.[/yellow]"
            )

    def add_file(self, file_path):
        try:
            file_content = FileSystem.read_file(file_path, mode="r")
            file_hash = generate_hash(file_content)

            object_path = path.join(self.objects_path, file_hash)
            FileSystem.write_file(object_path, file_content, mode="w")

            self.update_index(file_path, file_hash)
            rich_print(f"[green]Success : Added file {file_path} to Pit.[/green]")
            print("\n")

        except PermissionError:
            rich_print(
                f"[red]Error : Permission denied. Unable to access {file_path}.[/red]"
            )
        except OSError:
            rich_print(f"[red]Error : Unable to add file {file_path} to Pit.[/red]")

    def update_index(self, file_path, file_hash):
        index = json.loads(FileSystem.read_file(self.index_path))
        index.append({"path": file_path, "hash": file_hash})
        FileSystem.write_file(self.index_path, json.dumps(index))

    def get_head(self):
        try:
            return FileSystem.read_file(self.head_path)
        except (PermissionError, OSError) as e:
            rich_print(
                f"[red]Error : Permission denied. Unable to access {self.head_path}.[/red]"
            )
            print(e)

        return None

    def create_commit(self, commit_message):
        index = json.loads(FileSystem.read_file(self.index_path))
        parent_commit = self.get_head()

        commit_data = {
            "timestamp": format_date(datetime.now()),
            "message": commit_message,
            "files": index,
            "parent": parent_commit,
        }

        commit_hash = generate_hash(json.dumps(commit_data))
        commit_path = path.join(self.objects_path, commit_hash)

        FileSystem.write_file(commit_path, json.dumps(commit_data))
        FileSystem.write_file(self.head_path, commit_hash)
        FileSystem.write_file(self.index_path, "[]")

        rich_print(f"[green]Success : Created commit {commit_hash}.[/green]")
        print("\n")

    def log(self):

        current_commit_hash = self.get_head()

        while current_commit_hash:

            commit_data = self.get_commit_data(current_commit_hash)

            if commit_data:
                rich_print(f"Commit : {current_commit_hash}")
                rich_print(f"Date : {commit_data['timestamp']}")
                rich_print(f"Message : {commit_data['message']}")

                current_commit_hash = commit_data["parent"]
            else:
                break

    def diff(self, commit_hash):
        commit_data = self.get_commit_data(commit_hash)

        if not commit_data:
            rich_print(f"[red]Error : Commit {commit_hash} not found.[/red]")
            print("\n")
            return

        rich_print("[green]Changes in last commit[/green]")

        for file in commit_data["files"]:

            rich_print(f"[blue]{file['path']}[/blue]")
            current_content = self.get_file_content(file["hash"])
            rich_print(f"[green]{current_content}[/green]")
            print("\n")

            if commit_data.get("parent"):
                parent_commit_data = self.get_commit_data(commit_data["parent"])
                parent_file = next(
                    (
                        f
                        for f in parent_commit_data["files"]
                        if f["path"] == file["path"]
                    ),
                    None,
                )

                if parent_file:
                    parent_content = self.get_file_content(parent_file["hash"])
                    rich_print(f"Changes in {file['path']}")
                    rich_print(f"[yellow]Old content : \n{parent_content}[/yellow]")
                    rich_print(f"[green]New content : \n{current_content}[/green]")
                    print("\n")
                else:
                    rich_print("[green]New file added in this commit.[/green]")
                    print("\n")

    def get_commit_data(self, commit_hash):

        commit_path = path.join(self.objects_path, commit_hash)
        try:
            return json.loads(FileSystem.read_file(commit_path))
        except (PermissionError, OSError) as e:
            rich_print(
                f"[red]Error : Permission denied. Unable to access {commit_path}.[/red]"
            )
            print(e)

        return None

    def get_file_content(self, file_hash):
        file_path = path.join(self.objects_path, file_hash)
        return FileSystem.read_file(file_path)

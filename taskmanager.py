import datetime
import json
import os
import flet as ft
from flet import *

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.data_file = "tasks.json"
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.tasks = json.load(f)
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = []

    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def add_task(self, title, description="", priority="Medium"):
        """Add a new task"""
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "description": description,
            "priority": priority,
            "completed": False,
            "created_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "completed_date": None
        }
        self.tasks.append(task)
        self.save_tasks()
        return task

    def toggle_task(self, task_id):
        """Toggle task completion status"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = not task["completed"]
                if task["completed"]:
                    task["completed_date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                else:
                    task["completed_date"] = None
                self.save_tasks()
                break

    def delete_task(self, task_id):
        """Delete a task"""
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        self.save_tasks()

    def get_tasks(self, filter_type="all"):
        """Get tasks based on filter"""
        if filter_type == "completed":
            return [task for task in self.tasks if task["completed"]]
        elif filter_type == "pending":
            return [task for task in self.tasks if not task["completed"]]
        return self.tasks


def main(page: ft.Page):
    page.title = "Personal Task Manager"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.window.width = 800
    page.window.height = 600
    page.window.icon="icon.ico"
    page.scroll=ft.ScrollMode.HIDDEN
    page.window.center()
    # Initialize task manager
    task_manager = TaskManager()

    # UI Components
    task_title = ft.TextField(
        label="Task Title",
        hint_text="Enter task title...",
        expand=True
    )

    task_description = ft.TextField(
        label="Description (Optional)",
        hint_text="Enter task description...",
        multiline=True,
        min_lines=2,
        max_lines=4
    )

    priority_dropdown = ft.Dropdown(
        label="Priority",
        value="Medium",
        options=[
            ft.dropdown.Option("High"),
            ft.dropdown.Option("Medium"),
            ft.dropdown.Option("Low"),
        ],
        width=150
    )

    # Filter buttons
    filter_all = ft.TextButton(
        "All Tasks",
        on_click=lambda _: update_task_list("all")
    )
    filter_pending = ft.TextButton(
        "Pending",
        on_click=lambda _: update_task_list("pending")
    )
    filter_completed = ft.TextButton(
        "Completed",
        on_click=lambda _: update_task_list("completed")
    )

    # Task list container
    task_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    # Stats container
    stats_text = ft.Text("", size=14, color=ft.Colors.GREY_600)

    def get_priority_color(priority):
        """Get color for priority"""
        colors = {
            "High": ft.Colors.RED_400,
            "Medium": ft.Colors.ORANGE_400,
            "Low": ft.Colors.GREEN_400
        }
        return colors.get(priority, ft.Colors.GREY_400)

    def create_task_card(task):
        """Create a task card widget"""
        def toggle_task(e):
            task_manager.toggle_task(task["id"])
            update_task_list()
        
        def delete_task(e):
            task_manager.delete_task(task["id"])
            update_task_list()
        
        # Task title with strikethrough if completed
        title_style = ft.TextStyle(
            decoration=ft.TextDecoration.LINE_THROUGH if task["completed"] else None,
            color=ft.Colors.GREY_500 if task["completed"] else None
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Checkbox(
                        value=task["completed"],
                        on_change=toggle_task
                    ),
                    ft.Column([
                        ft.Text(
                            task["title"],
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            style=title_style
                        ),
                        ft.Text(
                            task["description"] if task["description"] else "No description",
                            size=12,
                            color=ft.Colors.GREY_600,
                            style=title_style
                        ),
                        ft.Row([
                            ft.Container(
                                content=ft.Text(
                                    task["priority"],
                                    size=10,
                                    color=ft.Colors.WHITE
                                ),
                                bgcolor=get_priority_color(task["priority"]),
                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                border_radius=10
                            ),
                            ft.Text(
                                f"Created: {task['created_date']}",
                                size=10,
                                color=ft.Colors.GREY_500
                            ),
                        ]),
                        ft.Text(
                            f"Completed: {task['completed_date']}" if task["completed_date"] else "",
                            size=10,
                            color=ft.Colors.GREEN_600
                        ) if task["completed"] else ft.Container(),
                    ], expand=True),
                    ft.IconButton(
                        ft.Icons.DELETE,
                        icon_color=ft.Colors.RED_400,
                        on_click=delete_task,
                        tooltip="Delete task"
                    )
                ])
            ]),
            padding=15,
            margin=ft.margin.only(bottom=10),
            bgcolor=ft.Colors.GREY_50 if task["completed"] else ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
        )

    def add_task(e):
        """Add new task"""
        if task_title.value and task_title.value.strip():
            task_manager.add_task(
                task_title.value.strip(),
                task_description.value.strip() if task_description.value else "",
                priority_dropdown.value
            )
            # Clear form
            task_title.value = ""
            task_description.value = ""
            priority_dropdown.value = "Medium"
            page.update()
            update_task_list()
        else:
            # Show error using snack bar
            page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Please enter a task title"),
                    bgcolor=ft.Colors.RED_400
                )
            )

    def update_task_list(filter_type="all"):
        """Update task list display"""
        tasks = task_manager.get_tasks(filter_type)
        task_list.controls.clear()
        
        if tasks:
            for task in sorted(tasks, key=lambda x: x["created_date"], reverse=True):
                task_list.controls.append(create_task_card(task))
        else:
            task_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No tasks found",
                        size=16,
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER
                    ),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
        
        # Update stats
        all_tasks = task_manager.get_tasks()
        completed_tasks = task_manager.get_tasks("completed")
        pending_tasks = task_manager.get_tasks("pending")
        
        stats_text.value = f"Total: {len(all_tasks)} | Completed: {len(completed_tasks)} | Pending: {len(pending_tasks)}"
        
        page.update()

    # Add task button
    add_button = ft.ElevatedButton(
        "Add Task",
        icon=ft.Icons.ADD,
        on_click=add_task,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_400,
            color=ft.Colors.WHITE
        )
    )

    # Layout
    page.add(
        ft.Column([
            # Header
            ft.Container(
                content=ft.Text(
                    "Personal Task Manager",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                padding=ft.padding.only(bottom=20)
            ),
            
            # Add task form
            ft.Container(
                content=ft.Column([
                    ft.Text("Add New Task", size=18, weight=ft.FontWeight.BOLD),
                    task_title,
                    task_description,
                    ft.Row([
                        priority_dropdown,
                        add_button
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ]),
                padding=20,
                bgcolor=ft.Colors.BLUE_50,
                border_radius=10,
                margin=ft.margin.only(bottom=20)
            ),
            
            # Filters and stats
            ft.Row([
                ft.Text("Filter:", size=14, weight=ft.FontWeight.BOLD),
                filter_all,
                filter_pending,
                filter_completed,
            ], alignment=ft.MainAxisAlignment.START),
            
            ft.Container(
                content=stats_text,
                padding=ft.padding.only(top=10, bottom=10)
            ),
            
            # Task list
            ft.Container(
                content=task_list,
                expand=True,
                padding=10,
                bgcolor=ft.Colors.GREY_100,
                border_radius=10
            )
        ], expand=True)
    )

    # Initial load
    update_task_list()


if __name__ == "__main__":
    ft.app(target=main,assets_dir="assets")

    #Check the codes with my Github links below i will put to the comment Please dont forget to subscribe our youtube channel
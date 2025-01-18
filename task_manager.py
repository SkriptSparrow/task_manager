import json
import os
import flet as ft


TASKS_FILE = "tasks.json"


def save_to_file(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)


def load_from_file():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)  # Загружаем задачи
            except json.JSONDecodeError:
                return []  # Возвращаем пустой список, если файл поврежден
    return []  # Возвращаем пустой список, если файл не существует


def main(page: ft.Page):
    page.title = "Task Manager"
    screen_width = page.window.width
    screen_height = page.window.height
    page.window.width = screen_width * 0.4
    page.window.height = screen_height * 1.3
    page.window.resizable = False
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.GREEN,
            primary_container=ft.Colors.GREEN_200
        ),
    )
    service_task = []  # Список для хранения карточек
    service_task_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)  # Контейнер для карточек
    loaded_cards = load_from_file()  # Загрузка сохранённых карточек при запуске приложения
    service_task.extend(loaded_cards)  # Загружаем сохранённые карточки

    # Отображение загруженных карточек
    for card_data in loaded_cards:
        service_task_container.controls.append(
            ft.Card(
                content=ft.ListTile(
                    title=ft.Text(card_data['name']),
                    on_click=lambda e, c=card_data.copy(): open_card(c),
                )
            )
        )

    def on_theme_toggle(e):
        """Функция смены темы"""
        if theme_switch.value:
            theme_switch.label = "Темная тема"
            page.theme_mode = ft.ThemeMode.DARK
        else:
            theme_switch.label = "Светлая тема"
            page.theme_mode = ft.ThemeMode.LIGHT
        page.update()

    def add_new_card(e):
        """Функция создания новой задачи"""
        task_name_input = ft.TextField(label="Название задачи", expand=True)
        subtasks_container = ft.Column(spacing=5)

        def add_subtask(e):
            """ Функция создания подзадач"""
            subtask_text = ft.TextField(
                label="Описание",
                height=80,
                width=250,
                expand=True,
                multiline=True,
                hint_text="Enter text here",
                text_align=ft.TextAlign.LEFT
            )

            subtask_checkbox = ft.Checkbox(
                label=" ",
                value=False
            )

            row = ft.Row(
                [subtask_checkbox, subtask_text],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START
            )

            # Добавляем кнопку удаления
            delete_button = ft.IconButton(
                icon=ft.Icons.DELETE_FOREVER,
                on_click=lambda e, r=row: delete_subtask(r, e)  # Захватываем значение row в r
            )

            # Добавляем кнопку в строку
            row.controls.append(delete_button)

            # Добавляем контейнер в subtasks_container
            subtasks_container.controls.append(row)
            page.update()

        def delete_subtask(row, e):
            """Функция для удаления подзадач"""
            subtasks_container.controls.remove(row)  # Удаляем контейнер с подзадачей из списка controls
            page.update()

            task_data = service_task[-1]  # или используйте правильный индекс задачи
            subtask_index = subtasks_container.controls.index(row)

            if subtask_index < len(task_data.get('subtasks', [])):
                task_data['subtasks'].pop(subtask_index)  # Удаляем из данных
            else:
                print("Ошибка: подзадача не найдена в данных")

            save_to_file(service_task)  # Обновляем сохраненные данные

        add_subtask_button = ft.ElevatedButton(
            text="+ Добавить подзадачу",
            on_click=add_subtask
        )

        def save_card(e):
            """Функция сохранения задачи"""
            if not task_name_input.value.strip():
                # Отображение SnackBar с сообщением об ошибке
                if not task_name_input.value.strip():
                    # Создание SnackBar с сообщением об ошибке
                    snack_bar = ft.SnackBar(
                        content=ft.Text(
                            "Название задачи не может быть пустым!",
                            color="black"
                        ),
                        bgcolor="red",
                        duration=1500,
                    )
                    page.overlay.append(snack_bar)  # Добавление SnackBar в overlay страницы
                    snack_bar.open = True  # Открыть SnackBar
                    page.update()
                    return

            subtasks = []
            for row in subtasks_container.controls:
                checkbox = row.controls[0]
                textfield = row.controls[1]
                subtasks.append({"name": textfield.value, "completed": checkbox.value})

            card_data = {
                "name": task_name_input.value,
                "subtasks": subtasks
            }
            service_task.append(card_data)
            service_task_container.controls.append(
                ft.Card(
                    content=ft.ListTile(
                        title=ft.Text(task_name_input.value),
                        on_click=lambda e: open_card(card_data),
                    )
                )
            )
            save_to_file(service_task)
            dialog.open = False
            page.update()

        def cancel_dialog(e):
            dialog.open = False
            page.update()

        dialog_content = ft.Column(
            controls=[
                ft.Row(
                    controls=[task_name_input],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Row(
                    controls=[subtasks_container],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Row(
                    controls=[add_subtask_button],
                    alignment=ft.MainAxisAlignment.START
                )
            ],
            spacing=10,
            height=500,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        dialog = ft.AlertDialog(
            title=ft.Text("Новая карточка", text_align=ft.TextAlign.CENTER),
            content=dialog_content,
            actions=[
                ft.TextButton("Сохранить", on_click=save_card),
                ft.TextButton("Отмена", on_click=cancel_dialog),
            ],
            open=True
        )
        page.overlay.append(dialog)  # Используем overlay для добавления диалога
        page.update()

    def open_card(card):
        """Функция для открытия карточки"""

        def update_progress():
            """Обновление прогресса выполнения подзадач"""
            total_subtasks = len(card.get("subtasks", []))  # Общее количество подзадач
            if total_subtasks == 0:  # Если подзадач нет
                progress_bar.value = 0
                progress_bar.label = "0%"
            else:
                # Подсчитываем количество выполненных подзадач
                completed_count = sum(1 for subtask in card["subtasks"] if subtask["completed"])
                progress_bar.value = completed_count
                progress_bar.label = f"{(completed_count / total_subtasks) * 100:.0f}%"

            # Обновляем страницу
            page.update()

        task_name_field = ft.TextField(
            label="Название сервиса",
            value=card['name'],
            expand=True
        )
        subtasks_container = ft.Column(spacing=5)

        progress_bar = ft.Slider(
            min=0,
            max=len(card.get("subtasks", [])),
            divisions=len(card.get("subtasks", [])),  # Количество подзадач
            value=0,
            label="{value}%",
            autofocus=False,
            on_change=lambda e: update_progress()  # Обновляем прогресс при изменении слайдера
        )

        # Отобразить существующие подзадачи
        for subtask in card.get("subtasks", []):
            update_progress()
            # Создаем текстовое поле для подзадачи
            subtask_text = ft.TextField(
                value=subtask.get("name", ""),
                width=250,
                height=80,
                multiline=True,
                expand=True,
            )
            # Создаем чекбокс для подзадачи
            subtask_checkbox: ft.Checkbox = ft.Checkbox(
                value=subtask.get("completed", False)
            )
            if subtask_checkbox.value:
                subtask_text.text_style = ft.TextStyle(
                    decoration=ft.TextDecoration.LINE_THROUGH,
                    color=ft.Colors.GREY
                )

            def toggle_text_style(e, checkbox=subtask_checkbox, text=subtask_text):
                """Обработчик изменения состояния чекбокса"""
                # Обновляем стиль текста в зависимости от состояния чекбокса
                if checkbox.value:  # Если чекбокс установлен
                    text.text_style = ft.TextStyle(
                        decoration=ft.TextDecoration.LINE_THROUGH,
                        color=ft.Colors.GREY,
                    )
                else:  # Если чекбокс снят
                    text.text_style = None

                # Обновляем данные карточки
                for subtask in card["subtasks"]:
                    if subtask["name"] == text.value:  # Находим соответствующую подзадачу
                        subtask["completed"] = checkbox.value  # Обновляем состояние
                        break

                # Сохраняем изменения в файл
                save_to_file(service_task)

                # Обновляем прогресс
                update_progress()

            # Привязываем обработчик к чек-боксу
            subtask_checkbox.on_change = toggle_text_style
            # Создаем строку с подзадачей
            row = ft.Row(
                [subtask_checkbox, subtask_text],
                vertical_alignment=ft.CrossAxisAlignment.START
            )
            # Добавляем кнопку удаления
            delete_button = ft.IconButton(
                icon=ft.Icons.DELETE_FOREVER,
                on_click=lambda e, r=row: delete_subtask(r, e)  # Захватываем значение row
            )
            # Добавляем кнопку в строку
            row.controls.append(delete_button)
            # Добавляем строку в контейнер подзадач
            subtasks_container.controls.append(row)

        def add_subtask(e):
            subtask_checkbox = ft.Checkbox(
                label=" ",
                value=False
            )
            subtask_text = ft.TextField(
                label="Описание",
                height=80,
                width=250,
                expand=True,
                multiline=True,
                hint_text="Enter text here",
                text_align=ft.TextAlign.LEFT
            )

            # Создаем иконку удаления
            row = ft.Row(
                [subtask_checkbox, subtask_text],
                vertical_alignment=ft.CrossAxisAlignment.START,
                height=100)

            delete_button = ft.IconButton(
                icon=ft.Icons.DELETE_FOREVER,
                on_click=lambda e, r=row: delete_subtask(r, e)  # Захватываем значение row
            )

            row.controls.append(delete_button)


            def update_text_style(e):
                if subtask_checkbox.value:  # Если чекбокс установлен
                    subtask_text.text_style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)  # Зачеркиваем
                else:  # Если чекбокс не установлен
                    subtask_text.text_style = None  # Убираем зачеркивание
                update_progress()

            subtask_checkbox.on_change = update_text_style

            # Добавляем контейнер в subtasks_container
            subtasks_container.controls.append(row)
            page.update()

        def delete_subtask(row, e):
            # Удаляем контейнер с подзадачей из списка controls
            subtasks_container.controls.remove(row)
            page.update()

            # Удаляем подзадачу из данных
            subtask_index = subtasks_container.controls.index(row)
            task_data = service_task[-1]  # или используйте правильный индекс задачи

            if subtask_index < len(task_data.get('subtasks', [])):
                task_data['subtasks'].pop(subtask_index)  # Удаляем из данных
            else:
                print("Ошибка: подзадача не найдена в данных")

            save_to_file(service_task)

        add_subtask_button = ft.ElevatedButton(text="+ Добавить подзадачу", on_click=add_subtask)

        def save_changes(e):
            card['name'] = task_name_field.value
            card['subtasks'] = [
                {"name": row.controls[1].value, "completed": row.controls[0].value}
                for row in subtasks_container.controls
            ]
            save_to_file(service_task)
            dialog.open = False
            update_progress()
            page.update()

        def delete_card(e):
            service_task.remove(card)
            save_to_file(service_task)
            service_task_container.controls.clear()
            for card_data in service_task:
                service_task_container.controls.append(
                    ft.Card(
                        content=ft.ListTile(
                            title=ft.Text(card_data['name']),
                            on_click=lambda e, c=card_data.copy(): open_card(c),
                        )
                    )
                )
            dialog.open = False
            page.update()

        def close_card(e):
            dialog.open = False
            page.update()

        dialog_content = ft.Column(
            controls=[
                ft.Row(controls=[task_name_field], alignment=ft.MainAxisAlignment.CENTER),
                progress_bar,  # Прогресс-бар между названием и подзадачами
                ft.Row(controls=[subtasks_container], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row(controls=[add_subtask_button], alignment=ft.MainAxisAlignment.CENTER)
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        dialog = ft.AlertDialog(
            title=ft.Text(card['name'], text_align=ft.TextAlign.CENTER),
            content=dialog_content,
            actions=[
                ft.TextButton("Удалить", on_click=delete_card),
                ft.TextButton("Сохранить", on_click=save_changes),
                ft.TextButton("Закрыть", on_click=close_card),
            ],
            open=True
        )
        page.overlay.append(dialog)
        page.update()

    theme_switch = ft.Switch(
        label="Темная тема",
        value=True,
        on_change=on_theme_toggle)

    header = ft.Row([
        ft.Text(
            "Менеджер задач",
            size=30,
            color="green",
            selectable=True,
            expand=True),
        theme_switch],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    add_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        on_click=add_new_card,
        bgcolor=ft.Colors.GREEN)

    page.add(
        ft.Column([
            header,
            service_task_container,
        ],
            expand=True), add_button
    )
    page.update()


ft.app(target=main)

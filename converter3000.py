# Copyright (c) 2025 Roman Boyarintsev
# All rights reserved.
#
# This software is licensed under the Python Software Foundation License (PSF License) and GNU General Public License (GPL v3).
# See LICENSE_PSF.txt and LICENSE_GPLv3.txt for details.

import sys
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QClipboard, QRegularExpressionValidator,QIcon
from PyQt6.QtWidgets import QApplication,QWidget,QVBoxLayout,QHBoxLayout,QPlainTextEdit,QPushButton,QLineEdit,QLabel,QCheckBox


class NoSpaceValidator(QRegularExpressionValidator):
    """
    Валидатор, запрещающий ввод пробелов.
    """
    def __init__(self):
        super().__init__(QRegularExpression(r'\S*'))  # Регулярное выражение, разрешающее любые непустые символы, кроме пробела


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Настройки главного окна
        self.setWindowTitle("Преобразователь 3000")
        self.resize(600, 350)  # Увеличим размер окна для удобного размещения всех элементов

        # Создание виджетов
        self.input_plain_text_edit = QPlainTextEdit()  # Поле для ввода
        self.input_plain_text_edit.setPlaceholderText('Введите или вставьте текст. Программа разделит его на элементы по пробелам. Затем они объединятся в строку с заданными начальными, конечными и разделительными символами.')
        self.start_characters_line_edit = QLineEdit()  # Поле для ввода начальных символов
        self.start_characters_line_edit.setPlaceholderText('Начальные символы (по умолчанию ")')
        self.start_characters_line_edit.setToolTip('Начальные символы (по умолчанию ")')
        self.separator_line_edit = QLineEdit()  # Поле для ввода разделителя
        self.separator_line_edit.setPlaceholderText('Разделитель (по умолчанию ",")')
        self.separator_line_edit.setToolTip('Разделитель (по умолчанию ",")')
        self.end_characters_line_edit = QLineEdit()  # Поле для ввода конечных символов
        self.end_characters_line_edit.setPlaceholderText('Конечные символы (по умолчанию ")')
        self.end_characters_line_edit.setToolTip('Конечные символы (по умолчанию ")')
        self.output_plain_text_edit = QPlainTextEdit(readOnly=True)  # Поле для вывода результата
        self.output_plain_text_edit.setMaximumHeight(100)
        self.output_plain_text_edit.setPlaceholderText('Здесь выведется результат')
        self.status_label = QLabel()

        convert_button = QPushButton("Преобразовать")
        convert_button.setToolTip("Нажмите, чтобы преобразовать данные.")
        clear_button = QPushButton("Очистить")
        clear_button.setToolTip("Нажмите, чтобы очистить все поля.")
        copy_to_clipboard_button = QPushButton("Скопировать в буфер")  # Новая кнопка для копирования в буфер обмена
        copy_to_clipboard_button.setToolTip("Нажмите, чтобы скопировать результат в буфер обмена.")  # Тултип для кнопки

        # Создаем чекбокс
        self.process_as_single_element_checkbox = QCheckBox("Обрабатывать строки, как единый элемент")
        self.process_as_single_element_checkbox.setChecked(False)  # По умолчанию не отмечен
        self.process_as_single_element_checkbox.setToolTip("При установке этой галочки программа обработает строки как единый элемент без удаления пробелов.")

        # Применение валидаторов для запрета ввода пробелов
        no_space_validator = NoSpaceValidator()
        self.start_characters_line_edit.setValidator(no_space_validator)
        self.separator_line_edit.setValidator(no_space_validator)
        self.end_characters_line_edit.setValidator(no_space_validator)

        # Обработка сигналов кнопок
        convert_button.clicked.connect(self.convert_input)
        clear_button.clicked.connect(self.clear_fields)
        copy_to_clipboard_button.clicked.connect(self.copy_to_clipboard)  # Событие для копирования в буфер

        # Размещение виджетов
        hbox_layout = QHBoxLayout()
        hbox_layout.addStretch(1)
        hbox_layout.addWidget(convert_button)
        hbox_layout.addWidget(copy_to_clipboard_button)  # Добавляем новую кнопку в макет
        hbox_layout.addWidget(clear_button)
        hbox_layout.addStretch(1)

        # Горизонтальное размещение полей для ввода начальных/конечных символов и разделителя
        characters_hbox_layout = QHBoxLayout()
        characters_hbox_layout.addWidget(self.start_characters_line_edit)
        characters_hbox_layout.addWidget(self.separator_line_edit)
        characters_hbox_layout.addWidget(self.end_characters_line_edit)

        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(self.process_as_single_element_checkbox)
        vbox_layout.addWidget(self.input_plain_text_edit)
        vbox_layout.addLayout(characters_hbox_layout)
        vbox_layout.addLayout(hbox_layout)
        vbox_layout.addWidget(self.output_plain_text_edit)
        vbox_layout.addWidget(self.status_label)

        self.setLayout(vbox_layout)

        self.show()

    def convert_input(self):
        """Функция преобразования данных"""
        input_data = self.input_plain_text_edit.toPlainText().strip()  # Получаем текст из QPlainTextEdit
        start_chars = self.start_characters_line_edit.text().strip() or '"'  # Получаем начальные символы, если они введены, иначе используем '"'
        separator = self.separator_line_edit.text().strip() or '","'  # Получаем разделитель, если он введен, иначе используем '","'
        end_chars = self.end_characters_line_edit.text().strip() or '"'  # Получаем конечные символы, если они введены, иначе используем '"'

        # Проверяем состояние чекбокса
        if self.process_as_single_element_checkbox.isChecked():
            # Если чекбокс установлен, обрабатываем каждую строку как единое целое
            lines = input_data.split('\n')  # Разделение на строки
            all_elements = [line for line in lines if line.strip()]  # Сохраняем строки без удаления пробелов
            result = f'{start_chars}{separator.join(all_elements)}{end_chars}'  # Объединяем строки с разделителем
        else:
            # Иначе разбиваем текст на строки и далее каждую строку на элементы по пробелам
            lines = input_data.split('\n')
            all_elements = []
            for line in lines:
                elements_in_line = line.split()
                all_elements.extend(elements_in_line)

            # Формируем результат, очищая от лишних пробелов и пустых элементов
            filtered_elements = [element.strip() for element in all_elements if element.strip()]
            result = f'{start_chars}{separator.join(filtered_elements)}{end_chars}'

        # Подсчитываем количество слов и символов
        if self.process_as_single_element_checkbox.isChecked():
            word_count = sum(len(line.split()) for line in lines)  # Количество слов во всех строках
        else:
            word_count = len(filtered_elements)
        total_characters = len(result)
    
        # Строка статуса
        status_string = f"Исходное количество слов: {word_count} | Итоговое количество символов: {total_characters}."
        self.status_label.setText(status_string)
        
        # Выводим результат
        self.output_plain_text_edit.setPlainText(result)

    def clear_fields(self):
        """Функция очистки полей"""
        self.input_plain_text_edit.clear()
        self.start_characters_line_edit.clear()
        self.separator_line_edit.clear()
        self.end_characters_line_edit.clear()
        self.output_plain_text_edit.clear()

    def copy_to_clipboard(self):
        """Функция копирования содержимого output_plain_text_edit в буфер обмена."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_plain_text_edit.toPlainText(), mode=QClipboard.Mode.Clipboard)
        self.output_plain_text_edit.setFocus(Qt.FocusReason.MouseFocusReason)  # Перемещаем фокус обратно на output_plain_text_edit


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowIcon(QIcon("splitmerge.ico"))
    window.show()
    sys.exit(app.exec())
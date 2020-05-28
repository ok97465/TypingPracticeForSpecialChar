"""숫자 및 특수기호 타자 연습 프로그램."""
# Standard library imports
import sys
import time
from datetime import timedelta
from random import choice

# Third party imports
from qtpy.QtCore import Signal, Slot
from qtpy.QtGui import QFont, QPixmap, QIcon
from qtpy.QtWidgets import (QMainWindow, QApplication, QLineEdit, QVBoxLayout,
                            QWidget, QFrame, QLabel)
import qdarkstyle


VER = "0.0.01"


class VLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(self.VLine|self.Sunken)


class ManageTyping:
    """Typing 정보를 저장한다."""

    def __init__(self):
        self.start_time = None  # 이전 게임을 시작한 시간
        self.elapsed_time_total = 0  # 전체 Typing 시간
        self.elapsed_time_prev = 0  # 직전 게임의 Typing 시간
        self.n_repeat = 0  # 게임 횟수
        self.n_space_between_chars = 2  # 글자간 여백
        self.n_char_in_game = 25  # 한번 연습에 사용할 문자수
        self.chars_answer = ''  # 현재 문제
        # 연습에 사용하 문자들
        self.char_candidate = list("0123456789;:\"'[]/?<>|.,\\!@#$%^&*()_-+=")

        self.new_game()
    
    def new_game(self):
        """새로운 연습 문장을 만든다."""
        self.start_time = None
        chars_for_practice = [choice(self.char_candidate)
                              for _ in range(self.n_char_in_game)]
        self.chars_answer = ''.join(chars_for_practice)

    def typing_per_sec_prev(self):
        """이전 연습의 타수를 반환한다."""
        if self.n_repeat == 0:
            return 0
        else:
            return self.n_char_in_game / self.elapsed_time_prev

    def typing_per_sec_avg(self):
        """평균 타수를 반환한다."""
        if self.n_repeat == 0:
            return 0
        else:
            elapsed = (self.n_repeat 
                       * self.n_char_in_game 
                       / self.elapsed_time_total)
            return elapsed

    def check_result(self, input_str):
        """결과를 비교한다."""
        is_correct = False
        err_str = ""

        input_str = input_str.replace(" ", "")

        if input_str == self.chars_answer:
            self.elapsed_time_prev = time.time() - self.start_time
            self.elapsed_time_total += self.elapsed_time_prev
            self.n_repeat += 1
            is_correct = True

        err = []

        for s1, s2 in zip(input_str, self.chars_answer):
            if s1 == s2:
                err.append(" " * (self.n_space_between_chars + 1))
            else:
                err.append("▲")
        
        if err:
            err_str = "".join(err)

        return is_correct, err_str

    def update_time(self):
        if self.start_time is None:
            self.start_time = time.time()

    def str_of_total_time(self):  
        """총 연습 시간을 시분초로 반환한다."""
        diff_time = timedelta(seconds=self.elapsed_time_total)
        mm, ss = divmod(diff_time.seconds, 60)
        hh, mm = divmod(mm, 60)
        return f'{hh:02d}:{mm:02d}:{ss:02d}'


class MainWindowTyping(QMainWindow):
    """Main Window."""

    def __init__(self):
        """Main Window UI를 설정한다."""
        super().__init__()
        self.setWindowTitle(f"Typing Number - {VER}")

        icon = QIcon()
        icon.addPixmap(QPixmap(r'ok_64x64.ico'), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setMinimumSize(800, 100)

        # Typing Info
        self.typing = ManageTyping()

        # Setup StatusBar
        self.statusBar().showMessage("")
        self.statusBar().addPermanentWidget(VLine())
        self.label_typing_avg = QLabel("평균타수 : 0.0타/초", self)
        self.statusBar().addPermanentWidget(self.label_typing_avg)

        self.statusBar().addPermanentWidget(VLine())
        self.label_total_time = QLabel("총 연습시간", self)
        self.statusBar().addPermanentWidget(self.label_total_time)

        # Setup LineEdit
        self.line_for_number = QLineEdit(self)
        self.line_for_typing = QLineEdit(self)
        self.line_for_error = QLineEdit(self)
        self.setup_lineedit()
        vbox = QVBoxLayout()
        vbox.addWidget(self.line_for_number)
        vbox.addWidget(self.line_for_typing)
        vbox.addWidget(self.line_for_error)

        central_widget = QWidget(self)
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)

        self.new_game()

    def setup_lineedit(self):
        """LineEdit를 설정한다."""
        mask = (("X" + " " * self.typing.n_space_between_chars) 
                * self.typing.n_char_in_game)
        self.line_for_number.setInputMask(mask)
        self.line_for_typing.setInputMask(mask)
        self.line_for_error.setInputMask(mask)

        self.line_for_number.setReadOnly(True)
        self.line_for_error.setReadOnly(True)

        self.line_for_error.setStyleSheet(
            "QLineEdit { border:none; color: red; }")

        self.line_for_typing.textChanged.connect(self.update_typing)
    
    def display_result(self):
        """연습결과를 보여준다."""
        typing_per_sec = self.typing.typing_per_sec_prev()
        typing_per_sec_avg = self.typing.typing_per_sec_avg()

        self.statusBar().showMessage(
            f'현재타수 : {typing_per_sec:.1f}타/초')
        
        self.label_typing_avg.setText(
            f'평균타수 : {typing_per_sec_avg:.1f}타/초')

        self.label_total_time.setText(
            "총 연습시간 : " + self.typing.str_of_total_time())

    def new_game(self):
        """연습에 필요한 문자열 만든다."""
        self.line_for_typing.setText("")
        self.line_for_typing.setCursorPosition(0)

        self.typing.new_game()
        self.line_for_number.setText(self.typing.chars_answer)

        self.line_for_typing.setFocus()
        self.display_result()
    
    def update_typing(self):
        """Typing 정보를 갱신한다."""
        typing = self.typing
        typing.update_time()
        is_correct, err_str = typing.check_result(self.line_for_typing.text())

        if is_correct:
            self.new_game()
            self.line_for_error.setText("")

        self.line_for_error.setText(err_str)


if __name__ == "__main__":
    APP = QApplication(sys.argv)
    style_sheet = qdarkstyle.load_stylesheet_pyqt5()
    APP.setStyleSheet(style_sheet)

    FONT = QFont("D2Coding ligature", 15)
    FONT.setStyleHint(QFont.Monospace)
    APP.setFont(FONT)

    MAIN_WINDOW = MainWindowTyping()

    MAIN_WINDOW.show()

    sys.exit(APP.exec_())

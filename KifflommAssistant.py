import sys
import threading
import time
import keyboard
import pydirectinput
import winsound
import win32api, win32con
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QSpinBox, QRadioButton, QFrame, QPushButton)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl
from PyQt6.QtGui import QDesktopServices

pydirectinput.PAUSE = 0

class RunnerLogic(threading.Thread):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.running = False
        self.daemon = True

    def force_release(self):
        for key in ['w', 'shift', 'ctrl', 'alt']:
            pydirectinput.keyUp(key)

    def run(self):
        while True:
            if self.running:
                pydirectinput.keyDown('w')
                pydirectinput.keyDown('shift')
                
                speed = self.settings['mouse_speed']
                move_x = speed if self.settings['mouse_dir'] == 'right' else -speed
                
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(move_x), 0, 0, 0)
                time.sleep(0.01)
            else:
                time.sleep(0.1)

class KifflomApp(QWidget):
    hotkey_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.active = False
        self.start_time = 0
        self.total_target_ms = 27 * 60 * 1000
        self.settings = {'mouse_speed': 7.0, 'mouse_dir': 'right'} 
        
        self.init_ui()
        self.logic = RunnerLogic(self.settings)
        self.logic.start()
        
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update_stats)
        
        self.hotkey_signal.connect(self.toggle)
        keyboard.add_hotkey('ctrl+shift+enter', lambda: self.hotkey_signal.emit())

    def init_ui(self):
        self.setWindowTitle('Epsilon Program: Truth Exercise Assistant')
        self.setFixedSize(460, 640)
        self.setStyleSheet("background-color: #001a2c; color: #5086C1;")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()

        # Header
        self.status_box = QLabel('KIFFLOM, BROTHER-BROTHER!')
        self.status_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_box.setStyleSheet("""
            background: #5086C1; color: white; font-weight: bold; 
            font-size: 22px; border: 2px solid white; padding: 15px;
        """)
        layout.addWidget(self.status_box)

        # Timers
        timer_frame = QFrame()
        timer_frame.setStyleSheet("background: #000; border: 2px solid #5086C1; border-radius: 5px;")
        t_layout = QVBoxLayout(timer_frame)
        self.lbl_elapsed = QLabel('ELAPSED: 00:00:00.000')
        self.lbl_left = QLabel('LEFT:    27:00:00.000')
        self.lbl_dist = QLabel('MILES:   0.000 / 5.000')
        for lbl in [self.lbl_elapsed, self.lbl_left, self.lbl_dist]:
            lbl.setStyleSheet("color: #00d4ff; font-family: 'Consolas'; font-size: 20px; border: none;")
            t_layout.addWidget(lbl)
        layout.addWidget(timer_frame)

        # Settings
        layout.addWidget(QLabel("ORBIT SETTINGS:"))
        h_dir = QHBoxLayout()
        self.rb_m_left = QRadioButton("Orbit Left")
        self.rb_m_right = QRadioButton("Orbit Right")
        self.rb_m_right.setChecked(True)
        h_dir.addWidget(self.rb_m_left); h_dir.addWidget(self.rb_m_right)
        layout.addLayout(h_dir)

        h_speed = QHBoxLayout()
        h_speed.addWidget(QLabel("Rotation Speed (1-100):"))
        self.spin_speed = QSpinBox()
        self.spin_speed.setRange(1, 100); self.spin_speed.setValue(70)
        h_speed.addWidget(self.spin_speed)
        layout.addLayout(h_speed)

        # Instructions
        help_box = QLabel(
            "COMMANDS:\n"
            "• CTRL + SHIFT + ENTER: Toggle Auto-Run\n"
            "• ESC (In App Window): Emergency Stop & Close\n\n"
            "INSTRUCTIONS:\n"
            "1. Go to the desert and activate script.\n"
            "2. Switch to 1st Person view (Default 'V') for better orbit.\n"
            "3. Alt-Tab to the app and press ESC to stop."
        )
        help_box.setStyleSheet("color: #aaa; font-size: 11px; background: #00253d; padding: 10px; border-radius: 5px;")
        layout.addWidget(help_box)

        # Warning Block
        warning_box = QLabel(
            "<b>WARNING:</b> This tool is for <b>SINGLE PLAYER</b> use only. "
            "It was not designed or tested for GTA Online. "
            "Use at your own risk. The author is not responsible for any bans or account actions."
        )
        warning_box.setStyleSheet("color: #d44; font-size: 10px; background: #1a0000; padding: 10px; border: 1px solid #d44; border-radius: 5px;")
        warning_box.setWordWrap(True)
        layout.addWidget(warning_box)

        # Links
        self.quote = QLabel('<a href="https://github.com/kickmesc-dotcom/GTA-V-Kifflom-Assistant" style="color: #5086C1; text-decoration: none;">The Tract says: "Everything is simple."</a>')
        self.quote.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quote.setOpenExternalLinks(True)
        layout.addWidget(self.quote)

        self.btn_support = QPushButton("Make a Tithe to the Cult (Support)")
        self.btn_support.setStyleSheet("""
            QPushButton { background-color: transparent; color: #5086C1; border: 1px solid #5086C1; 
                          font-weight: bold; padding: 8px; margin-top: 5px; }
            QPushButton:hover { background-color: #5086C1; color: #001a2c; }
        """)
        self.btn_support.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://boosty.to/icreatethings")))
        layout.addWidget(self.btn_support)

        self.setLayout(layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.stop_and_release()
            self.close()

    def sync_settings(self):
        self.settings['mouse_speed'] = self.spin_speed.value() / 10.0
        self.settings['mouse_dir'] = 'right' if self.rb_m_right.isChecked() else 'left'

    def toggle(self):
        self.active = not self.active
        self.sync_settings()
        self.logic.running = self.active
        if self.active:
            self.start_time = time.time() * 1000
            self.ui_timer.start(33)
            self.status_box.setText('SEEKING THE TRUTH...')
            self.status_box.setStyleSheet("background: #00d4ff; color: #000; font-weight: bold; font-size: 22px;")
            winsound.Beep(1000, 300)
        else:
            self.stop_and_release()

    def stop_and_release(self):
        self.active = False
        self.logic.running = False
        self.ui_timer.stop()
        self.logic.force_release()
        self.status_box.setText('KIFFLOM, BROTHER!')
        self.status_box.setStyleSheet("background: #5086C1; color: white; font-weight: bold; font-size: 22px;")
        winsound.Beep(500, 300)

    def update_stats(self):
        current_ms = time.time() * 1000
        elapsed_ms = current_ms - self.start_time
        remaining_ms = max(0, self.total_target_ms - elapsed_ms)
        def format_ms(ms):
            m, s = divmod(int(ms / 1000), 60)
            h, m = divmod(m, 60)
            return f"{h:02d}:{m:02d}:{s:02d}.{int(ms % 1000):03d}"
        self.lbl_elapsed.setText(f"ELAPSED: {format_ms(elapsed_ms)}")
        self.lbl_left.setText(f"LEFT:    {format_ms(remaining_ms)}")
        dist = (elapsed_ms / self.total_target_ms) * 5.0
        self.lbl_dist.setText(f"MILES:   {min(5.0, dist):.3f} / 5.000")
        if remaining_ms <= 0: self.finish()

    def finish(self):
        self.stop_and_release()
        self.status_box.setText('TRUTH DELIVERED!')
        self.status_box.setStyleSheet("background: #fff; color: #5086C1; font-weight: bold; font-size: 22px;")
        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

    def closeEvent(self, event):
        self.logic.force_release()
        keyboard.unhook_all()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = KifflomApp()
    window.show()
    sys.exit(app.exec())

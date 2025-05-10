#!/usr/bin/env python3

import gi
import subprocess
import socket

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Doesn't need to succeed
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Unavailable"

def get_proftpd_port(config_paths=["/etc/proftpd.conf", "/etc/proftpd/proftpd.conf"]):
    for path in config_paths:
        try:
            with open(path, "r") as f:
                for line in f:
                    if line.strip().lower().startswith("port"):
                        parts = line.strip().split()
                        if len(parts) >= 2 and parts[1].isdigit():
                            return parts[1]
        except FileNotFoundError:
            continue
    return "21"  # Default port

class ProFTPDFrontend(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="ProFTPD Frontend (Arch Linux)")
        self.set_border_width(10)
        self.set_default_size(400, 400)

        # Layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # Labels
        self.status_label = Gtk.Label(label="Status: Unknown")
        vbox.pack_start(self.status_label, False, False, 0)

        self.ip_label = Gtk.Label(label=f"IP Address: {get_ip_address()}")
        vbox.pack_start(self.ip_label, False, False, 0)

        self.port_label = Gtk.Label(label=f"FTP Port: {get_proftpd_port()}")
        vbox.pack_start(self.port_label, False, False, 0)

        # Buttons
        button_box = Gtk.Box(spacing=10)
        vbox.pack_start(button_box, False, False, 0)

        start_button = Gtk.Button(label="Start")
        start_button.connect("clicked", self.start_proftpd)
        button_box.pack_start(start_button, True, True, 0)

        stop_button = Gtk.Button(label="Stop")
        stop_button.connect("clicked", self.stop_proftpd)
        button_box.pack_start(stop_button, True, True, 0)

        restart_button = Gtk.Button(label="Restart")
        restart_button.connect("clicked", self.restart_proftpd)
        button_box.pack_start(restart_button, True, True, 0)

        refresh_button = Gtk.Button(label="Refresh Status")
        refresh_button.connect("clicked", self.refresh_status)
        vbox.pack_start(refresh_button, False, False, 0)

        # Edit Config Button
        edit_config_button = Gtk.Button(label="Edit Config")
        edit_config_button.connect("clicked", self.edit_config)
        vbox.pack_start(edit_config_button, False, False, 0)

        # Log Viewer
        log_label = Gtk.Label(label="ProFTPD Logs:")
        log_label.set_xalign(0)
        vbox.pack_start(log_label, False, False, 0)

        self.log_buffer = Gtk.TextBuffer()
        self.log_view = Gtk.TextView(buffer=self.log_buffer)
        self.log_view.set_editable(False)
        self.log_view.set_wrap_mode(Gtk.WrapMode.WORD)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.log_view)
        vbox.pack_start(scrolled_window, True, True, 0)

        self.refresh_status(None)

    def run_command(self, command):
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return output.decode("utf-8")
        except subprocess.CalledProcessError as e:
            return e.output.decode("utf-8")

    def load_logs(self):
        logs = self.run_command("journalctl -u proftpd --no-pager -n 100")
        self.log_buffer.set_text(logs)

    def refresh_status(self, widget):
        output = self.run_command("systemctl is-active proftpd")
        status = output.strip()
        self.status_label.set_text(f"proFTP Status: {status}")
        self.ip_label.set_text(f"IP Address: {get_ip_address()}")
        self.port_label.set_text(f"FTP Port: {get_proftpd_port()}")
        self.load_logs()

    def start_proftpd(self, widget):
        self.run_command("pkexec systemctl start proftpd")
        self.refresh_status(widget)

    def stop_proftpd(self, widget):
        self.run_command("pkexec systemctl stop proftpd")
        self.refresh_status(widget)

    def restart_proftpd(self, widget):
        self.run_command("pkexec systemctl restart proftpd")
        self.refresh_status(widget)

    def edit_config(self, widget):
        command = "kate /etc/proftpd.conf"  # You can change 'nano' to another editor like 'vim' or 'gedit'
        self.run_command(command)

win = ProFTPDFrontend()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

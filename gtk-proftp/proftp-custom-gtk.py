#!/usr/bin/env python3

import gi
import subprocess
import socket
import os
import pwd

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
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
    return "21"

class ProFTPDFrontend(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="ProFTPD Frontend (Arch Linux)")
        self.set_border_width(10)
        self.set_default_size(500, 600)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        self.status_label = Gtk.Label(label="Status: Unknown")
        vbox.pack_start(self.status_label, False, False, 0)

        self.ip_label = Gtk.Label(label=f"IP Address: {get_ip_address()}")
        vbox.pack_start(self.ip_label, False, False, 0)

        self.port_label = Gtk.Label(label=f"FTP Port: {get_proftpd_port()}")
        vbox.pack_start(self.port_label, False, False, 0)

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

        edit_config_button = Gtk.Button(label="Edit Config")
        edit_config_button.connect("clicked", self.edit_config)
        vbox.pack_start(edit_config_button, False, False, 0)

        user_label = Gtk.Label(label="Create FTP User")
        user_label.set_xalign(0)
        vbox.pack_start(user_label, False, False, 0)

        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        vbox.pack_start(grid, False, False, 0)

        self.username_entry = Gtk.Entry()
        self.username_entry.set_placeholder_text("Username")
        grid.attach(Gtk.Label(label="Username:"), 0, 0, 1, 1)
        grid.attach(self.username_entry, 1, 0, 1, 1)

        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)
        self.password_entry.set_placeholder_text("Password")
        grid.attach(Gtk.Label(label="Password:"), 0, 1, 1, 1)
        grid.attach(self.password_entry, 1, 1, 1, 1)

        self.folder_entry = Gtk.Entry()
        self.folder_entry.set_placeholder_text("/path/to/share")
        grid.attach(Gtk.Label(label="Shared Folder:"), 0, 2, 1, 1)
        grid.attach(self.folder_entry, 1, 2, 1, 1)

        create_user_button = Gtk.Button(label="Create FTP User")
        create_user_button.connect("clicked", self.create_ftp_user)
        grid.attach(create_user_button, 1, 3, 1, 1)

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

    def show_message(self, message, title="Info"):
        dialog = Gtk.MessageDialog(transient_for=self, flags=0,
                                   message_type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK,
                                   text=title)
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def load_logs(self):
        logs = self.run_command("journalctl -u proftpd --no-pager -n 100")
        self.log_buffer.set_text(logs)

    def refresh_status(self, widget):
        status = self.run_command("systemctl is-active proftpd").strip()
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
        self.run_command("kate /etc/proftpd.conf")

    def create_ftp_user(self, widget):
        username = self.username_entry.get_text().strip()
        password = self.password_entry.get_text().strip()
        folder = self.folder_entry.get_text().strip()

        if not username or not password or not folder:
            self.show_message("Please fill in all fields.", "Missing input")
            return

        try:
            pwd.getpwnam(username)
            self.show_message(f"User '{username}' already exists.")
            return
        except KeyError:
            pass  # User does not exist; proceed.

        try:
            if not os.path.exists(folder):
                os.makedirs(folder)
            self.run_command(f"pkexec useradd -d {folder} -s /bin/false {username}")
            self.run_command(f"pkexec bash -c \"echo '{username}:{password}' | chpasswd\"")
            self.run_command(f"pkexec chown -R {username}:{username} {folder}")
            self.show_message(f"User '{username}' created and assigned to folder '{folder}'.")
        except Exception as e:
            self.show_message(f"Failed to create user: {e}", "Error")

if __name__ == "__main__":
    win = ProFTPDFrontend()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

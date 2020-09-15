"""
    TranSPHIRE is supposed to help with the cryo-EM data collection
    Copyright (C) 2017 Markus Stabrin

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import urllib3
import socket
import smtplib
from email.mime.text import MIMEText
import telepot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from . import transphire_utils as tu

class NotificationContainer(QWidget):
    """
    Container for notification widgets

    Inherits:
    QWidget

    Signals:
    sig_stop - Signal is emitted, if the user is sending /stop via telegram
    """
    sig_stop = pyqtSignal()

    def __init__(
            self, content, mount_worker, process_worker,
            settings_folder, parent=None, **kwargs
            ):
        """
        Initialise layout

        Arguments:
        content - TranSPHIRE content
        mount_worker - Mount worker object
        process_worker - Process worker object
        settings_folder - Folder to load/save settings from/to
        parent - Parent widget (default None)

        Returns:
        None
        """
        super(NotificationContainer, self).__init__(parent)

        noti_content = {}
        for entry in content:
            for widget in entry:
                for key in widget:
                    noti_content[key] = widget[key][0]
        bot_token = noti_content['Bot token'].strip()
        self.smtp_server = noti_content['SMTP server']
        self.sending_email = noti_content['E-Mail adress']

        # Global content
        self.content = {}
        self.users_telegram = {}
        self.users_email = {}
        self.block_list = []
        self.bot = telepot.Bot(bot_token)
        self.parent = parent
        self.settings_folder = settings_folder
        self.update_id = 0
        self.enable_telegram = None
        exception_list = []

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        max_per_col = 3

        default_programs_dict = {
            'telegram': 'T',
            'email': '@'
            }

        # Add to layout
        for key, value  in default_programs_dict.items():
            layout_default = QHBoxLayout()
            layout.addLayout(layout_default)
            if noti_content['Default names {0}'.format(key)]:
                offset = 0
                for idx, entry in enumerate(noti_content['Default names {0}'.format(key)].split(';')):
                    try:
                        name, default = entry.split(':')
                    except ValueError:
                        print('Default {0} entry does not follow - Name:{0} Name - {1}'.format(key, entry))
                        offset += 1
                        continue
                    if idx-offset % max_per_col == 0 and idx != 0:
                        layout_default.addStretch(1)
                        layout_default = QHBoxLayout()
                        layout.addLayout(layout_default)
                    name = '{0} {1}'.format(value, name)
                    default = '{0} {1}'.format(value, default)
                    exception_list.append(default)
                    widget = NotificationWidget(name=name, default=default, parent=self, default_programs_dict=default_programs_dict)
                    layout_default.addWidget(widget)
                    self.content[name] = widget
                if noti_content['Default names {0}'.format(key)].split(';'):
                    layout_default.addStretch(1)
            else:
                pass

        # Chooseable users
        layout_default_user = QHBoxLayout()
        layout.addLayout(layout_default_user)
        for idx in range(int(noti_content['Number of users'])):
            if idx % max_per_col == 0 and idx != 0:
                layout_default_user.addStretch(1)
                layout_default_user = QHBoxLayout()
                layout.addLayout(layout_default_user)
            name = 'User {0}'.format(idx)
            default = 'choose'
            widget = NotificationWidget(name=name, default=default, parent=self, default_programs_dict=default_programs_dict)
            for entry in exception_list:
                widget.add_exceptions(name=entry)
            layout_default_user.addWidget(widget)
            self.content[name] = widget
        if int(noti_content['Number of users']) != 0:
            layout_default_user.addStretch(1)

        # Test button
        layout_button = QHBoxLayout()
        layout.addLayout(layout_button)
        self.button_telegram = QPushButton('Update Telegram', self)
        self.button_telegram.setToolTip('Update Telegram')
        self.button_email = QPushButton('Add E-Mail', self)
        self.button_email.setToolTip('Add E-Mail')
        self.button_test = QPushButton('Test', self)
        self.button_test.setToolTip('Test')
        self.button_telegram.setObjectName('notification')
        self.button_test.setObjectName('notification')
        self.button_email.setObjectName('notification')
        layout_button.addWidget(self.button_telegram)
        layout_button.addWidget(self.button_email)
        layout_button.addWidget(self.button_test)
        layout_button.addStretch(1)

        layout.addStretch(1)

        # Events
        self.button_email.clicked.connect(self.add_email)
        self.button_telegram.clicked.connect(self.update)
        self.button_test.clicked.connect(lambda: self.send_notification('Test successful'))
        mount_worker.sig_notification.connect(self.send_notification)
        process_worker.sig_notification.connect(self.send_notification)

        self.enable_telegram = True
        self.enable_email = True
        self.first = True

    def get_settings(self):
        """
        Get settings as dict

        Arguments:
        None

        Returns:
        Settings dictionary as list
        """
        settings = {}
        for key in self.content:
            settings.update(self.content[key].get_settings())
        return [settings]

    def set_settings(self, settings):
        """
        Set settings.

        Arguments:
        settings - Settings as dictionary to set.

        Returns:
        None
        """
        for key in settings:
            try:
                self.content[key].set_settings(*settings[key])
            except KeyError:
                #print('Key', key, 'no longer exists')
                continue

    @pyqtSlot()
    def update(self):
        """
        Update the combo boxes.

        Arguments:
        None

        Returns:
        None
        """
        for key in self.content:
            self.content[key].clear_combo()
        if self.enable_telegram:
            self.update_telegram()
        else:
            pass
        if self.enable_email:
            self.update_email()
        else:
            pass
        if self.first:
            self.first = False
        else:
            pass

    @pyqtSlot()
    def add_email(self):
        """
        Add a new e-mail adress

        Arguments:
        None

        Returns:
        None
        """
        email_dialog = EmailDialog(self)
        result = email_dialog.exec_()
        if result:
            save_file = os.path.join(
                self.settings_folder,
                '.users_email'
                )
            user = email_dialog.get_name()
            email = email_dialog.get_email()
            self.users_email[user] = email
            with open(save_file, 'w') as write:
                for key in self.users_email:
                    write.write('{0}\t{1}\n'.format(key, self.users_email[key]))
        else:
            pass
        self.update()

    def update_email(self):
        """
        Update E-Mail file.

        Arguments:
        None

        Returns:
        None
        """
        save_file = os.path.join(
            self.settings_folder,
            '.users_email'
            )

        # Check if a save file exists
        if os.path.exists(save_file):
            with open(save_file) as read:
                for line in read:
                    name, email = line.replace('\n', '').split('\t')
                    self.users_email[name] = email
        for key in self.content:
            self.content[key].update_combo('email', self.users_email)

        try:
            server = smtplib.SMTP(self.smtp_server, timeout=10)
        except socket.timeout:
            self.enable_email = False
            print('EMail SMTP server adress not acessable!')
            return None
        except socket.gaierror:
            self.enable_email = False
            print('EMail SMTP server adress wrong or empty')
            return None
        except smtplib.SMTPServerDisconnected:
            self.enable_email = False
            print('EMail SMTP server adress wrong or empty')
            return None
        else:
            try:
                server.quit()
            except smtplib.SMTPServerDisconnected:
                self.enable_email = False
                print('EMail SMTP server adress wrong or empty')
                return None

    def update_telegram(self):
        """
        Update telegram settings file

        Arguments:
        None

        Returns:
        None
        """
        save_file = os.path.join(
            self.settings_folder,
            '.users_telegram'
            )

        # Check if a save file exists
        if os.path.exists(save_file):
            with open(save_file) as read:
                for line in read:
                    name, user_id = line.replace('\n', '').split('\t')
                    self.users_telegram[name] = user_id

        try:
            response = self.bot.getUpdates()
        except telepot.exception.TelegramError:
            self.enable_telegram = False
            print('Telegram bot token wrong or empty!')
            return None
        except urllib3.exceptions.MaxRetryError:
            self.enable_telegram = False
            print('Telegram bot not acessable!')
            return None
        except telepot.exception.BadHTTPResponse:
            self.enable_telegram = False
            print('Telegram bot not acessable!')
            return None
        self.users_telegram.update(self.get_telegram_user(response))

        with open(save_file, 'w') as write:
            for key in list(self.users_telegram.keys()):
                try:
                    write.write('{0}\t{1}\n'.format(key, self.users_telegram[key]))
                except UnicodeEncodeError:
                    print('Found a non-unicode character, that cannot be decoded.')
                    del self.users_telegram[key]

        for key in self.content:
            self.content[key].update_combo('telegram', self.users_telegram)

    @pyqtSlot(str)
    def send_notification(self, text):
        """
        Send a notification to specified users.

        Arguments:
        text - Text to send

        Returns:
        None
        """

        text = '{0}:\n{1}'.format(os.uname()[1], text)
        print(text)
        chosen_users = self.get_settings()
        for entry in chosen_users:
            for key in entry:
                name, state = entry[key].split('\t')

                if self.enable_telegram:
                    telegram_name = name[2:]

                    if telegram_name in self.users_telegram and \
                            state == 'True' and \
                            name.startswith('T '):
                        user_id = self.users_telegram[telegram_name]
                        try:
                            self.bot.sendMessage(user_id, text)
                        except telepot.exception.BotWasBlockedError as err:
                            if user_id in self.block_list:
                                pass
                            else:
                                self.block_list.append(user_id)
                                tu.message('{0}\n{1}\t{2}'.format(
                                    os.uname()[1],
                                    name,
                                    err
                                    ))
                        except telepot.exception.TooManyRequestsError:
                            print('Could not send: {}'.format(text))
                        except telepot.exception.TelegramError as err:
                            if user_id in self.block_list:
                                pass
                            else:
                                self.block_list.append(user_id)
                                tu.message('{0}\n{1}\t{2}'.format(
                                    os.uname()[1],
                                    name,
                                    err
                                    ))
                        else:
                            if user_id in self.block_list:
                                self.block_list.remove(user_id)
                            else:
                                pass

                    else:
                        pass

                else:
                    pass

                if self.enable_email:
                    email_name = name[2:]

                    if email_name in self.users_email and \
                            state == 'True' and \
                            name.startswith('@ '):
                        email = self.users_email[email_name]
                        msg = MIMEText(text)
                        msg['Subject'] = 'Transphire message {0}'.format(
                            os.uname()[1]
                            )
                        msg['From'] = self.sending_email
                        msg['To'] = email
                        try:
                            server = smtplib.SMTP(self.smtp_server, timeout=10)
                        except smtplib.SMTPServerDisconnected:
                            print('Could not send to:', name)
                            continue
                        except Exception:
                            print('Unknown exception! Could not send to:', name)
                            continue

                        try:
                            server.sendmail(self.sending_email, [email], msg.as_string())
                        except smtplib.SMTPServerDisconnected:
                            print('Could not send to:', name)
                            continue
                        except smtplib.SMTPRecipientsRefused:
                            print('Could not send to:', name)
                            continue
                        except Exception:
                            print('Unknown exception! Could not send to:', name)
                            continue

                        try:
                            server.quit()
                        except smtplib.SMTPServerDisconnected:
                            print('Could not send to:', name)
                            continue
                        except Exception:
                            print('Unknown exception! Could not send to:', name)
                            continue
                    else:
                        pass

                else:
                    pass

        else:
            pass

    def get_telegram_user(self, page):
        """
        Get the users and the user id

        Arguments:
        page - Webpage of the telegram bot

        Returns:
        Dictionary of users
        """
        user_dict = {}
        for entry in page:
            msg = entry['message']
            try:
                msg['text']
            except KeyError:
                continue
            if msg['text'] == '/start' or msg['text'] == '/refresh':
                user_id = None
                first_name = None
                last_name = None
                for key in msg['chat']:
                    if key == 'id':
                        user_id = msg['chat']['id']
                    elif key == 'first_name':
                        first_name = msg['chat']['first_name']
                    elif key == 'last_name':
                        last_name = msg['chat']['last_name']
                if last_name is None:
                    key = '{0}'.format(first_name)
                else:
                    key = '{0} {1}'.format(first_name, last_name)
                user_dict[key] = user_id
            else:
                pass
            if self.first:
                self.update_id = entry['update_id'] + 1
            else:
                pass
        return user_dict

    def enable(self, var, use_all):
        """
        Enable or disable the widgets of the widget.

        Arguments:
        var - True(Enable) or False(Disable)
        use_all - Disable or enable all

        Returns:
        None
        """
        for key in self.content:
            if use_all:
                self.content[key].setEnabled(var)
                self.button_email.setEnabled(var)
                self.button_telegram.setEnabled(var)
                self.button_test.setEnabled(var)
            else:
                pass

    def get_telegram_messages(self):
        """
        Check the messages in telegram for commands.

        Arguments:
        None

        Returns:
        None
        """
        if not self.enable_telegram:
            return None
        else:
            pass

        try:
            page_dict = self.bot.getUpdates(offset=self.update_id)
        except telepot.exception.TelegramError:
            print('Telegram bot token wrong or empty!')
            return None
        except telepot.exception.BadHTTPResponse:
            print('Telegram bot not acessable!')
            return None
        except urllib3.exceptions.MaxRetryError:
            print('Telegram bot not acessable!')
            return None
        except urllib3.exceptions.ReadTimeoutError:
            print('Telegram bot not acessable!')
            return None
        except Exception as e:
            print(e)
            return None

        for line in page_dict:
            try:
                msg = line['message']
                self.update_id = line['update_id'] + 1
                try:
                    first_name = msg['from']['first_name']
                except KeyError:
                    first_name = None
                try:
                    last_name = msg['from']['last_name']
                except KeyError:
                    last_name = None
                if first_name is None and last_name is None:
                    user = 'Anonymus User'
                elif first_name is None:
                    user = last_name
                elif last_name is None:
                    user = first_name
                else:
                    user = '{0} {1}'.format(first_name, last_name)

                if msg['text'].startswith('/send'):
                    text = msg['text'][len('/send'):]
                    self.send_notification('{0}: {1}'.format(user, text))
                elif msg['text'].startswith('/stop'):
                    self.send_notification('Stopping {0}'.format(os.uname()[1]))
                    self.sig_stop.emit()
                else:
                    pass
            except Exception:
                continue

    def send_to_user(self, user_id, text, name):
        """
        Send a message to all users.

        Arguments:
        user_id - User id of the receiving person
        text - Text of the message
        name - Name of the sender

        Returns:
        None
        """
        try:
            self.bot.sendMessage(
                user_id,
                '{0}\n{1}: {2}'.format(os.uname()[1], name, text)
                )
        except telepot.exception.BotWasBlockedError as err:
            tu.message('{0}\n{1}\t{2}'.format(
                os.uname()[1],
                name,
                err
                ))

from .notificationwidget import NotificationWidget
from .emaildialog import EmailDialog

import smtplib
import sys
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename
from pathlib import Path
from tkinter import Tk, Label, mainloop, Entry, Text, Button, filedialog, END, INSERT, Frame
from typing import List, Tuple, Union, Dict

from config import EMAIL_FILE, EMAIL_TEXT_FILE, EMAIL_LOGIN, EMAIL_PASSWORD
from models import Address, Email


def get_emails() -> List[str]:
    with open(EMAIL_FILE) as file:
        return file.readlines()


def get_email_text() -> Tuple[str, str]:
    """First line in EMAIL_TEXT_FILE is subject, second line is empty, email text are further"""
    with open(EMAIL_TEXT_FILE) as file:
        subject = file.readline()
        file.readline()

        return subject, file.read()


def send_email(email: str, subject: str = '', text: str = '', attachments: List[str] = ()) -> None:
    msg = MIMEMultipart()
    msg['From'] = EMAIL_LOGIN
    msg['To'] = email
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in attachments:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)

    server = smtplib.SMTP('smtp.mail.ru', 587)
    server.starttls()
    server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
    text = msg.as_string()
    try:
        server.sendmail(EMAIL_LOGIN, email, text)
        server.quit()
    except:
        print("Mail send error")
        server.quit()


def run_mailing():
    emails = get_emails()
    subject, text = get_email_text()

    addresses = Address.select()
    for address in addresses:
        send_email(email=address.email,
                   subject=subject,
                   text=text)


def init_db():
    Address.create_table(fail_silently=True)
    Email.create_table(fail_silently=True)


def prepare_email_addresses() -> List[Dict[str, str]]:
    with filedialog.askopenfile() as file:
        addresses = file.readlines()

    return [{'email': address.strip()}
            for address in addresses]


def load_addresses_to_field(field: Text):
    field.delete(1.0, END)

    field_text = '\n'.join([f"{address.email}" for address in Address.select()])
    field.insert(INSERT, field_text)


def load_email_addresses_from_file(field: Text):
    field.delete(1.0, END)
    address_records = prepare_email_addresses()
    Address.delete().where(True).execute()

    Address.insert_many(address_records).execute()

    load_addresses_to_field(field)


def save_email_addresses(addresses_field: Text):
    '''Save email addresses from Text widget'''
    text = addresses_field.get(1.0, END)

    addresses = [{'email': address.strip()} for address in text.split('\n')]

    Address.delete().where(True).execute()
    Address.insert_many(addresses).execute()


def main():
    init_db()

    percent_width = '30'
    percent_height = '20'

    root = Tk()
    root.title = 'Email sender'
    root.geometry('30x30')
    print(root.winfo_screenheight())
    width_pixels_to_percent = round(root.winfo_screenwidth() / 100)
    height_pixels_to_percent = round(root.winfo_screenheight() / 100)
    root.geometry(f"{width_pixels_to_percent * percent_width}x{height_pixels_to_percent*percent_height}")

    Label(root, text='Letter subject', font=('Helvetica', 14)).grid(row=0)
    Label(root, text='Letter text', font=('Helvetica', 14)).grid(row=1)
    Label(root, text='Emails', font=('Helvetica', 14)).grid(row=2)

    subject_field = Entry(root, width=60)
    subject_field.grid(row=0, column=1)
    subject_field.config(font=('Helvetica', 11))

    text_field = Text(root, width=60, height=10)
    text_field.grid(row=1, column=1)
    text_field.config(font=('Helvetica', 11))

    addresses_field = Text(root, width=60, height=20)
    addresses_field.grid(row=2, column=1)
    addresses_field.config(font=('Helvetica', 11))
    load_addresses_to_field(addresses_field)

    buttons_frame = Frame(root)
    buttons_frame.grid(row=2, column=2, sticky="nsew")

    save_addresses_button = Button(buttons_frame, text='Save email addresses',
                                   command=lambda: save_email_addresses(addresses_field))
    save_addresses_button.grid(row=0, column=0, sticky="nsew")
    save_addresses_button.config(font=('Helvetica', 10), width=30, height=3)

    load_addresses_from_file_button = Button(buttons_frame, text='Load email addresses from file',
                                             command=lambda: load_email_addresses_from_file(addresses_field))
    load_addresses_from_file_button.grid(row=1, column=0, sticky="nsew")
    load_addresses_from_file_button.config(font=('Helvetica', 10), width=30, height=3)

    run_mailing_button = Button(root, text='Run mailing', command=lambda: run_mailing())
    run_mailing_button.grid(row=3, column=1)
    run_mailing_button.config(font=('Helvetica', 10), width=60, height=3)

    mainloop()


if __name__ == "__main__":
    main()

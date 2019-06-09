import logging
import smtplib
import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename
from tkinter import Tk, Label, mainloop, Entry, Text, Button, filedialog, END, INSERT, Frame
from typing import List, Dict

from peewee import DoesNotExist

# from config import EMAIL_LOGIN, EMAIL_PASSWORD
from models import Address, Email, Launch


def get_credentials():
    try:
        with open('config.txt') as file:
            login, password = file.read().split(':')

        return login, password
    except FileNotFoundError:
        logger.debug('Файл с логином и паролем не найден')
        logger.info('test')
        exit()


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
        response = server.sendmail(EMAIL_LOGIN, email, text)
        if len(response) > 0:
            logger.info(response.__dict__)
    except smtplib.SMTPRecipientsRefused as e:
        logger.debug(e)
    finally:
        server.quit()


def save_email(subject, text):
    email = Email.create(subject=subject, text=text)
    # launch = Launch.create(email=email)


def run_mailing(subject_field: Entry, text_field: Text, addresses_field: Text):
    save_email_addresses(addresses_field)
    subject = subject_field.get()
    text = text_field.get(1.0, END)
    save_email(subject_field.get(), text_field.get(1.0, END))

    addresses = Address.select()
    for address in addresses:
        logger.info(f'Sending: {address.email}')
        send_email(email=address.email,
                   subject=subject,
                   text=text)

        time.sleep(1)


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
    address_records = prepare_email_addresses()
    Address.delete().where(True).execute()
    field.delete(1.0, END)

    Address.insert_many(address_records).execute()

    load_addresses_to_field(field)
    save_email_addresses(field)


def save_email_addresses(addresses_field: Text):
    '''Save email addresses from Text widget'''
    text = addresses_field.get(1.0, END)

    addresses = [{'email': address.strip()} for address in text.split('\n')]

    Address.delete().where(True).execute()
    Address.insert_many(addresses).execute()


def init_email_text(subject_field: Entry, text_field: Text):
    try:
        email = Email.select().order_by(Email._datetime.desc()).get()

        subject_field.insert(0, email.subject)
        text_field.insert(1.0, email.text)
    except DoesNotExist:
        pass


def main():
    init_db()

    percent_width = 70
    percent_height = 60

    root = Tk()
    root.title = 'Email sender'
    width_pixels_to_percent = round(root.winfo_screenwidth() / 100)
    height_pixels_to_percent = round(root.winfo_screenheight() / 100)
    screen_size = f"{width_pixels_to_percent * percent_width}x{height_pixels_to_percent*percent_height}"
    # root.geometry(screen_size)

    Label(root, text='Letter subject', font=('Helvetica', 14)).grid(row=0)
    Label(root, text='Letter text', font=('Helvetica', 14)).grid(row=1)
    Label(root, text='Emails', font=('Helvetica', 14)).grid(row=2)

    subject_field = Entry(root, width=60)
    subject_field.grid(row=0, column=1)
    subject_field.config(font=('Helvetica', 11))

    text_field = Text(root, width=60, height=10)
    text_field.grid(row=1, column=1)
    text_field.config(font=('Helvetica', 11))

    init_email_text(subject_field, text_field)

    addresses_field = Text(root, width=60, height=20)
    addresses_field.grid(row=2, column=1)
    addresses_field.config(font=('Helvetica', 11))
    load_addresses_to_field(addresses_field)

    # log_field = Text(root, width=60, height=3)
    # log_field.grid(row=3, column=1)
    # log_field.config(font=('Helvetica', 11))

    buttons_frame = Frame(root)
    buttons_frame.grid(row=2, column=2, sticky="nsew")

    # save_addresses_button = Button(buttons_frame, text='Save email addresses',
    #                                command=lambda: save_email_addresses(addresses_field))
    # save_addresses_button.grid(row=0, column=0, sticky="nsew")
    # save_addresses_button.config(font=('Helvetica', 10), width=30, height=3)

    load_addresses_from_file_button = Button(buttons_frame, text="Добавить email'ы из файла",
                                             command=lambda: load_email_addresses_from_file(addresses_field))
    load_addresses_from_file_button.grid(row=1, column=0, sticky="nsew")
    load_addresses_from_file_button.config(font=('Helvetica', 10), width=30, height=3)

    # status_field = Text(root, width=60)
    # status_field.grid(row=3, column=1)
    # status_field.config(font=('Helvetica', 11), width=60, height=3)

    run_mailing_button = Button(root, text='Run mailing', command=lambda: run_mailing(subject_field,
                                                                                      text_field,
                                                                                      addresses_field))
    run_mailing_button.grid(row=3, column=1)
    run_mailing_button.config(font=('Helvetica', 10), width=60, height=3)

    mainloop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='info.log')
    logger = logging.getLogger()
    EMAIL_LOGIN, EMAIL_PASSWORD = get_credentials()
    main()

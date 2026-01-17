from datetime import date

# Нормализация email адресов - приводит адреса к нижнему регистру и убирает пробелы
def normalize_addresses(value: str) -> str:
    return value.strip().lower()

# Сокращенная версия тела письма - создает короткую версию тела
def add_short_body(email: dict) -> dict:
    email["short_body"] = email.get("body")[:10] + "..." if len(email.get("body")) > 10 else email.get("body")
    return email

# Очистка текста письма - заменяет табы и переводы строк на пробелы
def clean_body_text(body: str) -> str:
    return body.replace("\n", " ").replace("\t", " ")

# Формирование итогового текста письма - создает форматированный текст письма
def build_sent_text(email: dict) -> str:
    return (
        f"Кому: {email['recipient']}\n"
        f"От: {email['sender']}\n"
        f"Тема: {email['subject']}\n"
        f"Дата: {email['date']}\n\n"
        f"{clean_body_text(email['body'])}"
    )

# Проверка пустоты темы и тела - проверяет, заполнены ли обязательные поля
def check_empty_fields(subject: str, body: str) -> tuple[bool, bool]:
    return not bool(subject.strip()), not bool(body.strip())

# Маска email отправителя - создает маскированную версию email (первые 2 символа + "***@" + домен)
def mask_sender_email(login: str, domain: str) -> str:
    return login[:2] + "***@" + domain

# Проверка корректности email - проверяет наличие @ и допустимые домены (.com, .ru, .net)
def get_correct_email(email_list: list[str]) -> list[str]:
    valid_emails = []
    domains = ['.com', '.ru', '.net']
    for email in email_list:
        if '@' in email and any(domain in email.lower() for domain in domains):
            valid_emails.append(email.strip())
    return valid_emails

# Создание словаря письма - создает базовую структуру письма
def create_email(sender: str, recipient: str, subject: str, body: str) -> dict:
    return {
        "sender": sender,
        "recipient": recipient,
        "subject": subject,
        "body": body
    }

# Добавление даты отправки - добавляет текущую дату
def add_send_date(email: dict) -> dict:
    email["date"] = date.today().isoformat()
    return email

# Получение логина и домена - разделяет email на логин и домен
def extract_login_domain(address: str) -> tuple[str, str]:
    parts = address.split("@")
    return parts[0].strip(), parts[1].strip()

# Функция отправки письма
def sender_email(recipient_list: list[str], subject: str, message: str, *, sender="default@study.com") -> list[dict]:
    # Проверить, что recipient_list не пустой
    if not recipient_list:
        return []

    # Проверить корректность email отправителя и получателей
    valid_recipients = get_correct_email(recipient_list)
    if not valid_recipients:
        return []

    # Проверить пустоту темы и тела письма
    is_subject_empty, is_body_empty = check_empty_fields(subject, message)
    if is_subject_empty or is_body_empty:
        return []

    # Исключить отправку самому себе
    valid_recipients = [recipient for recipient in valid_recipients if recipient != sender]

    # Нормализовать subject и body
    subject = clean_body_text(subject)
    message = clean_body_text(message)

    # Нормализовать sender и recipient_list
    sender = normalize_addresses(sender)
    valid_recipients = [normalize_addresses(recipient) for recipient in valid_recipients]

    # Создать письмо для каждого получателя
    emails = []
    for recipient in valid_recipients:
        email = create_email(sender, recipient, subject, message)
        email = add_send_date(email)

        # Замаскировать email отправителя
        login, domain = extract_login_domain(sender)
        masked_sender = mask_sender_email(login, domain)
        email["masked_sender"] = masked_sender

        # Сохранить короткую версию в email["short_body"]
        email = add_short_body(email)

        # Сформировать итоговый текст письма
        email["sent_text"] = build_sent_text(email)

        emails.append(email)

    return emails

# Пример использования
test_emails = [
    "user@gmail.com",
    "admin@company.ru",
    "test_123@service.net",
    "Example.User@domain.com",
    "default@study.com",
    " hello@corp.ru  ",
    "user@site.NET",
    "user@domain.coM",
    "user.name@domain.ru",
    "usergmail.com",       # Нет знака @
    "user@domain",         # Недостаточно доменного расширения
    "user@domain.org",     # Домен ".org" недопустимый
    "@mail.ru",            # Отсутствует логин
    "name@.com",           # Неправильный синтаксис домена
    "name@domain.comm",    # Неверный домен
    "",
    "   ",
]

result = sender_email(test_emails, "Hello!", "Привет, коллега!")
for email in result:
    print(email)


MailRedirector
[![License](https://img.shields.io/github/license/VadVergasov/MailRedirector)](https://github.com/VadVergasov/MailRedirector/blob/master/LICENSE)
[![Stars](https://img.shields.io/github/stars/VadVergasov/MailRedirector)](https://github.com/VadVergasov/MailRedirector/stargazers)
![Codestyle](https://img.shields.io/badge/code%20style-black-000000.svg)
===========

Simple to use Telegram bot, that can resend emails from the configured account.

Setup
-----------

```bash
git clone https://github.com/VadVergasov/MailRedirector.git
cd MailRedirector
python3 -m venv env
env\Scripts\activate.bat # For Windows.
source env/bin/activate # For Linux and MacOS
pip install -r requirements.txt
```

Copy config.py.template to config.py insert all required values, do the same with .service.templates, then run

```bash
sudo ln mailredirector_mail.service /etc/systemd/system/mailredirector_mail.service
sudo ln mailredirector_mail.timer /etc/systemd/system/mailredirector_mail.timer
sudo ln mailredirector.service /etc/systemd/system/mailredirector.service
sudo ln mailredirector_telegram.service /etc/systemd/system/mailredirector_telegram.service
sudo systemctl daemon-reload
sudo systemctl enable mailredirector mailredirector_mail.service mailredirector_mail.timer mailredirector_telegram
sudo systemctl start mailredirector
```

Basic usage
-----------
    
`/start` and `/help` commands adds your chat to sending list.
`/stop` removes your chat from sending list.

License
-----------

Licensed under GPLv3. See LICENSE file.

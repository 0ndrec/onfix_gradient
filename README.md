# Gradient Bot 🤖

![Console Screenshot](./images/console.png)
![Logs Screenshot](./images/logs.png)

Gradient Bot is an advanced automation tool designed to streamline the process of account registration and farming on Gradient Network. With its powerful features and user-friendly interface, it offers a seamless experience for users looking to maximize their efficiency on the platform.

For purchase: https://t.me/gradient_network_bot

Price: 120$

## ✨ Features

- 🔐 Automatic account registration
- 🧩 Integrated captcha solving
- ✉️ Email verification
- 🔗 Invite code binding
- 🌾 Automated farming
- 📊 Export statistics to CSV
- 🚀 Multi-threaded registration and export support

## 🖥️ System Requirements

- Windows operating system
- Stable internet connection
- Valid email accounts for registration
- Reliable proxies (optional but recommended)

## 🛠️ Setup Guide

1. Download the EXE file from the official source.
2. Run the EXE file and complete the login process.
3. Prepare the necessary configuration files as outlined in the next section.

## ⚙️ Configuration

### settings.yaml

This file contains the general settings for the bot. Here's an example configuration:

```yaml
threads: 3
invite_code: "DOIFI8"
capsolver_api_key: "YOUR_CAPSOLVER_API_KEY"

delay_before_start:
  min: 5
  max: 10

imap_settings:
  rambler.ru: imap.rambler.ru
  hotmail.com: imap-mail.outlook.com
  outlook.com: imap-mail.outlook.com
  mail.ru: imap.mail.ru
  gmail.com: imap.gmail.com
  gmx.com: imap.gmx.com
  yahoo.com: imap.mail.yahoo.com
  gmx.net: imap.gmx.net
  gmx.de: imap.gmx.net
```

### farm.txt

List the accounts for farming, one per line:

```
email1@example.com:password1
email2@example.com:password2
```

### register.txt

List the accounts for registration, one per line:

```
newemail1@example.com:newpassword1
newemail2@example.com:newpassword2
```

### proxies.txt

List them in this format:

```
http://user:pass@ip:port
http://ip:port:user:pass
http://ip:port@user:pass
http://user:pass:ip:port
```

## 🚀 Usage Instructions

1. **Clone the repository**:
    ```sh
    git clone https://github.com/0ndrec/onfix_gradient.git
    cd onfix_gradient
    ```
2. **Install the required dependencies**:
    ```sh
    pip install -r requirements.txt
    ```


## ⚠️ Important Notes

!! To successfully close a session you need to use the exit button or press ctrl + c, otherwise the session will remain active

- 🖥️ The Gradient Bot has support for 2 active sessions. You can run 2 versions on one PC, or 1 version on 2 PCs.
- 📧 Verify that your email providers are correctly configured in the `imap_settings` section of `settings.yaml`.
- 🧩 Maintain sufficient balance in your CapSolver account for uninterrupted captcha solving.

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Email verification failures | Check IMAP settings in `settings.yaml` and ensure they match your email provider's requirements. |
| Captcha-related problems | Verify your CapSolver API key and account balance. |
| Unexpected farming interruptions | Review console output for error messages and confirm account credentials. |

---

🌟 Thank you for choosing Gradient Bot! We're committed to enhancing your Gradient Network experience. 🌟

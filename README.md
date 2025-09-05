# 🚀 Flask Portfolio App

This is a Flask-based portfolio application.  
This README explains how to run the app **locally for development** and how to **deploy it in production** using **uWSGI + Nginx**. It also covers integration with **Cloudflare Tunnels** if you don’t want to expose ports directly or set up DNS/SSL manually.

---

## 📦 Requirements

- Python 3.8+
- `pip` & `venv`
- (Production) `nginx` and `uwsgi`

---

## 🔧 Local Development

Clone and install dependencies:

```bash
git clone https://github.com/Linux-bootloader/Portfolio.git
cd Portfolio
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Run the app locally:

```bash
flask run --debug
```

By default this starts the app at:

```
http://127.0.0.1:5000
```

---

## ⚡ Production Deployment (uWSGI + Nginx)

### 1. uWSGI Configuration

Create a file (e.g. `myproject.ini`) inside your project:

```ini
[uwsgi]
chdir = /path/to/your/project
module = app:app

master = true
processes = 2
threads = 2

socket = 127.0.0.1:8000

vacuum = true
die-on-term = true
virtualenv = /path/to/your/project/env
```

Test:

```bash
uwsgi --ini myproject.ini
```

---

### 2. Nginx Configuration

Create `/etc/nginx/sites-available/myproject`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        include uwsgi_params;
        uwsgi_pass 127.0.0.1:8000;
    }

    location /static/ {
        alias /path/to/your/project/static/;
    }

    location = /favicon.ico {
        alias /path/to/your/project/static/favicon.ico;
        access_log off;
        log_not_found off;
    }
}
```

Enable and reload nginx:

```bash
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Now requests to `yourdomain.com` will be proxied to your uWSGI app.

---

## 🌐 Using Cloudflare Tunnel

If you do **not** want to open ports or manage your own SSL certificates, you can use [Cloudflared Tunnels](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/):

1. Install the client:

   ```bash
   sudo apt install cloudflared
   ```

2. Authenticate with your Cloudflare account:

   ```bash
   cloudflared tunnel login
   ```

3. Create a tunnel:

   ```bash
   cloudflared tunnel create myproject
   ```

4. Map your local service to the tunnel (assuming nginx listens on port `80`):

   ```bash
   cloudflared tunnel route dns myproject yourdomain.com
   ```

   Or run locally without DNS:

   ```bash
   cloudflared tunnel --url http://localhost:80
   ```

Now your app is available on a public URL via Cloudflare Tunnel, without exposing open ports.

---

## ⚙️ Service Management (Production)

### systemd Service

Create `/etc/systemd/system/myproject.service`:

```ini
[Unit]
Description=uWSGI instance to serve Flask app
After=network.target

[Service]
User=youruser
Group=www-data
WorkingDirectory=/path/to/your/project
Environment="PATH=/path/to/your/project/env/bin"
ExecStart=/path/to/your/project/env/bin/uwsgi --ini /path/to/your/project/myproject.ini

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable myproject
sudo systemctl restart myproject
```

Check logs:

```bash
sudo journalctl -u myproject -f
```

---

## 🧰 Troubleshooting

- **404 (Not Found) for static files**  
  - Make sure nginx block uses `alias /path/to/.../static/;` (with trailing `/`).  
  - Ensure your HTML references `/static/...`.

- **403 (Forbidden) for static files**  
  - Ensure permissions allow nginx to read the folder:  
    ```bash
    sudo chmod -R o+r /path/to/project/static
    sudo chmod o+x /path /path/to /path/to/project
    ```

- **502 Bad Gateway**  
  - uWSGI isn’t running or crashed. Check with:  
    ```bash
    sudo systemctl status myproject
    ```

---

## ✅ Summary

- Use `flask run` during local development.  
- Use **uWSGI + Nginx** (or a container setup) in production.  
- Use **Cloudflare Tunnel** to securely expose your app without public port-forwarding.  
- Link static files consistently via `/static/...`.  

---

## 📝 License
Include your project license here.
```
Copyright © 2025 Jacob Jones. All rights reserved.

Default Licence (Restrictive Use)
--------------------------------
Unless a commercial licence is obtained as set out below, all rights in
and to this software and associated materials (the "Software") are
strictly reserved by the copyright holder, Jacob Jones (the "Licensor").

By default, permission is granted only to view, download, and run the
Software locally for private, personal, and non-commercial purposes.

The Licensee must not, without prior written consent from the Licensor:
  • Copy, reproduce, or redistribute the Software, in whole or part;
  • Deploy, publish, or host the Software on a public-facing platform;
  • Use the Software for any commercial purpose, direct or indirect;
  • Modify and redistribute the Software or create derivative works;
  • Remove or obscure copyright/proprietary notices.

Commercial Licence Option
-------------------------
Notwithstanding the restrictions above, a separate commercial
licence is available for purchase through the Licensor’s authorised
Gumroad page:

    https://jacobjones.gumroad.com/l/Coffee

Upon confirmed purchase, the Licensee is granted a limited,
non-exclusive, non-transferable licence to:

  • Deploy, publicly host, and use the Software for personal,
    professional, or commercial purposes (e.g. for a portfolio
    or business website);

Subject to the following restrictions:
  • The Software may not be resold, sublicensed, or redistributed
    in its original or modified form;
  • The Software may not be rebraned, repackaged, or marketed
    as a template or product for sale;
  • Authorship must not be misrepresented;
  • Derivative works for third-party resale or distribution require
    separate written agreement with the Licensor.

All rights not expressly granted under the commercial licence remain
reserved by the Licensor.

Intellectual Property
---------------------
All copyright and intellectual property rights in and to the Software
remain vested solely in Jacob Jones. The commercial licence confers a
usage right only and does not transfer ownership.

Termination
-----------
Any breach of the above terms automatically terminates the licence
(granted or purchased). On termination, the Licensee must immediately
cease all use of the Software and remove all deployed or hosted copies.

Warranty Disclaimer
-------------------
The Software is provided “as is” without warranty of any kind, express
or implied, including but not limited to warranties of merchantability,
fitness for a particular purpose, or non-infringement.

Limitation of Liability
-----------------------
To the maximum extent permitted by law, the Licensor shall not be liable
for any damages (whether direct, indirect, incidental, or consequential)
arising out of or related to the use of, or inability to use, the Software.

Governing Law
-------------
This Licence shall be governed by and construed in accordance with the
laws of Western Australia, Australia. The parties submit to the exclusive
jurisdiction of the courts of Western Australia and the Commonwealth of
Australia.

---

© 2025 Jacob Jones

---


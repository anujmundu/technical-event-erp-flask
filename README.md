# Technical Event Management ERP System

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black)
![ERP](https://img.shields.io/badge/Project-ERP%20System-green)

A simple Flask-based event management ERP with user, vendor, and admin portals. Uses SQLite and SQLAlchemy for persistence. The frontend is styled with the CoreUI theme (Bootstrap-based) and provides a clean, responsive UI for all pages.

## Overview

This project is a role-based **Event Management ERP System** developed using Flask.  
It simulates an enterprise workflow involving Admin, Vendor, and User roles, covering the full lifecycle from master data management to order processing and status tracking.

The system follows ERP principles such as role isolation, controlled data maintenance, and transaction lifecycle management.


## Features

### Authentication & Authorization
- Role-based login system (Admin, Vendor, User)
- Secure session handling
- Restricted route access
- Unauthorized access protection

---

### Admin Module (Master Data Management)
- Manage Memberships (Add / Delete / Expiry tracking)
- Maintain Users (Add / Edit / Delete / Change Membership)
- Maintain Vendors (Add / Edit / Delete)
- Category-based vendor management

---

### Vendor Module
- Vendor dashboard
- Add and manage products
- View vendor-specific items only
- View assigned orders
- Update order status:
  - Received
  - Ready for Shipping
  - Out for Delivery

---

### User Module
- Browse vendors by category
- View products
- Add items to cart
- Quantity management
- Checkout system
- Order tracking

---

### Cart & Checkout
- Persistent cart storage
- Quantity controls
- Order creation
- Automatic cart clearing after checkout
- Payment method selection

---

### Order Lifecycle
The system follows a clear, role-driven ERP workflow:

1. **Admin** creates vendors and users (master data management).
2. **Vendor** adds products, which become available to users.
3. **User** browses vendors by category, adds products to the cart, and checks out.
4. After checkout, an **Order** record is created for processing.
5. **Vendor** updates the order status step‑by‑step:
   - Received → Ready for Shipping → Out for Delivery.
6. **User** monitors and tracks the delivery progress from their dashboard.

This sequence ensures accountability, transparency, and a smooth order lifecycle.

---

### UI Improvements
- CoreUI dashboard theme
- Shared `base.html` layout
- Responsive navigation
- Styled system messages
- Consistent design across all modules

---

## Tech Stack

| Layer | Technology |
|------|------------|
| Backend | Flask |
| Database | SQLite + SQLAlchemy |
| Frontend | CoreUI (Bootstrap-based) |
| Authentication | Flask Sessions |
| Template Engine | Jinja2 |

---

## Project Structure

```
├── app.py              # main Flask application
├── auth_utils.py       # decorators for auth and roles
├── extensions.py       # database initialization
├── models.py           # SQLAlchemy models
├── requirements.txt    # Python dependencies
├── templates/          # Jinja2 HTML templates
│   ├── base.html       # shared layout with CoreUI
│   ├── home.html
│   ├── auth/...
│   ├── admin/...
│   ├── user/...
│   └── vendor/...
└── static/             # static assets (css, images, etc.)
```


## Prerequisites

- Python 3.8+ (tested on Windows)
- `pip` for installing dependencies

## Styling

All templates extend `base.html` which pulls in CoreUI (v4) from CDN. Custom page-specific CSS/JS can be injected with block placeholders.

## Notes

- Sample categories are seeded at application start if not already present.
- Error messages and special responses use `message.html` which is also styled.

## Extending

- Add more categories in `app.py` or manage via admin.
- Replace SQLite with another database by changing `SQLALCHEMY_DATABASE_URI`.
- Enhance forms with validation or file uploads as needed.

## Setup Instructions

### 1. Clone Repository

```bash
git clone <repository-url>
cd event_erp
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Application

```bash
python app.py
```

Open browser:

```
http://127.0.0.1:5000
```

## Demo Credentials

- **Admin**  
  Email: admin@erp.com  
  Password: admin123

- **Vendor**  
  Email: vendorwave@erp.com  
  Password: 123

- **User**  
  Email: user@erp.com  
  Password: 123

## ERP Workflow Demonstration

1. Admin creates vendor and user accounts.
2. Vendor adds products.
3. User browses vendors and places order.
4. Vendor updates order status.
5. User tracks delivery progress.

## Future Improvements

- Password hashing
- Membership expiry enforcement
- Product image uploads
- Audit logging
- Category management UI

## Author

Anuj Mundu  
MCA Student | Full Stack Developer | ERP Workflow Implementation Project
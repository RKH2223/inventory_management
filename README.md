# 📦 Inventory Management System

## 📌 Overview
The **Inventory Management System** is a **Django-based application** designed for managing paper reel stock efficiently. Users can add reels, log daily usage, and monitor inventory levels in real time.

## 🚀 Features
✅ User Authentication (Login/Logout)  
✅ Dashboard for inventory tracking  
✅ Add new reels (Natural & Golden paper types)  
✅ Log daily usage of reels  
✅ Delete reels when no longer needed  
✅ Admin panel for complete control  

---

## 🛠️ Installation & Setup

### 📋 Prerequisites
Ensure you have the following installed:
- **Python 3.x**
- **Django**
- **Virtual Environment** (optional but recommended)

### 📥 Clone the Repository
```sh
git clone https://github.com/RKH2223/inventory_management.git
cd inventory_management
```

### 🏗️ Create a Virtual Environment (Optional)
```sh
python -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate  # For Windows
```

### 📦 Install Dependencies
```sh
pip install -r requirements.txt
```

### 🔄 Run Migrations
```sh
python manage.py migrate
```

### 🔑 Create Superuser (For Admin Access)
```sh
python manage.py createsuperuser
```
Follow the prompts to set up an admin user.

### ▶️ Run the Development Server
```sh
python manage.py runserver
```
Now, open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

---

## 📊 Usage Guide
1. **Login** to access the dashboard.
2. **Add Reels** from the inventory section.
3. **Track Usage** by adding daily consumption.
4. **Monitor Inventory** through the dashboard.
5. **Manage Users & Data** via Django's Admin Panel at **[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).**

---

## 🏗️ Technologies Used
| Technology  | Purpose |
|-------------|---------|
| **Django**  | Backend framework |
| **SQLite**  | Default database (can be changed) |
| **HTML/CSS** | Frontend UI |
| **JavaScript** | Enhancing user experience |
| **Django User Model** | Authentication |

---

## 🤝 Contributing
Want to contribute? Follow these steps:  
1️⃣ **Fork the repository**  
2️⃣ **Create a new branch:** `git checkout -b feature-branch`  
3️⃣ **Make your changes and commit:** `git commit -m "Add new feature"`  
4️⃣ **Push to your branch:** `git push origin feature-branch`  
5️⃣ **Submit a Pull Request** 🚀  

---

## 📜 License
This project is licensed under the **MIT License**.

---

## 📧 Contact
For any inquiries, open an **issue** or contact the repository owner.

🌟 *If you find this project helpful, consider giving it a ⭐ on GitHub!*  

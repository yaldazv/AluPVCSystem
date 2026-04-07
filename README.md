# 🏭 AluPVC System - Управление на цех за дограма

![Django](https://img.shields.io/badge/Django-6.0.2-green.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-blue.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)
![AWS](https://img.shields.io/badge/AWS-EC2-orange.svg)

## 📋 Описание на прoекта

**AluPVC System** е уеб-базирана система за управление на цех за производство и монтаж на алуминиева и PVC дограма. Системата покрива пълния бизнес процес - от управление на материали и доставки, през поръчки и производство, до планиране на монтажи.

### 🎯 Основни функционалности:

- **📦 Управление на материали** - Профили, обков, аксесоари, стъклопакети
- **🚚 Доставки** - Регистриране на доставки и автоматично актуализиране на наличности
- **📋 Поръчки** - Създаване на поръчки с прозорци, врати, щори и гаражни врати
- **🔧 Производство** - Изчисляване на размери на стъклопакети, конфигурация на крила
- **📅 Монтажи** - Планиране и проследяване на монтажи

---

## 🏗️ Архитектура на проекта

### Django Apps:

| App | Отговорност |
|-----|-------------|
| **inventory** | Материали, доставчици, доставки, категории |
| **production** | Поръчки, прозорци, врати, готови продукти |
| **scheduling** | Планиране и управление на монтажи |

### Database Models:

**Inventory:**
- `Material` - Материали за производство
- `Category` - Категории (PVC, Алуминий)
- `Supplier` - Доставчици
- `Delivery` - Доставки на материали

**Production:**
- `Order` - Поръчки от клиенти
- `CustomProduct` - Прозорци и врати
- `ReadyProduct` - Щори и гаражни врати

**Scheduling:**
- `Installation` - Монтажи

### Relationships:

- **Many-to-One**: Order → CustomProduct, Order → ReadyProduct, Material → Delivery, Supplier → Delivery
- **Many-to-Many**: Material ↔ Category, CustomProduct ↔ Material, Installation ↔ Order

---

## 🚀 Инсталация и стартиране

### Предварителни изисквания:

- Python 3.12+
- PostgreSQL 14+ (или SQLite за тестване)
- Git

### Стъпка 1: Клониране на репозитория

```bash
git clone https://github.com/yaldazv/AluPVCSystem.git
cd AluPVCSystem
```

### Стъпка 2: Създаване на виртуална среда

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Стъпка 3: Инсталиране на зависимости

```bash
pip install -r requirements.txt
```

### Стъпка 4: Environment Variables (Опционално)

Проектът може да работи с `.env` файл за съхранение на чувствителни данни.

**Създайте `.env` файл в root папката:**

```bash
# Windows
New-Item -ItemType File -Name .env

# Linux/Mac
touch .env
```

**Примерно съдържание на `.env` файл:**

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*

# Database Configuration (PostgreSQL)
DB_NAME=alu_pvc_db
DB_USER=alupvc_user
DB_PASSWORD=your_database_password_here
DB_HOST=localhost
DB_PORT=5432
```

**Или копирайте template файла:**

```bash
# Windows
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

**⚠️ ВАЖНО:** 
- `.env` файлът е добавен в `.gitignore` и **НЕ се качва** в GitHub!
- За production използвайте силна SECRET_KEY и DEBUG=False
- Променете паролите преди production deployment

**Ако НЕ използвате `.env` файл:**
- Проектът работи с настройките по подразбиране в `settings.py`
- Използва SQLite база данни автоматично

---

### Стъпка 5: Конфигурация на базата данни

#### Вариант А: PostgreSQL (Препоръчително)

1. Създайте база данни:
```sql
CREATE DATABASE alupvc_db;
CREATE USER alupvc_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE alupvc_db TO alupvc_user;
```

2. Актуализирайте `AluPVCSystem/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'alu_pvc_db',
        'USER': 'alupvc_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### Aлтернатива (SQLite за тестване):

Проектът работи и със SQLite по подразбиране - не се изисква допълнителна конфигурация.

### Стъпка 6: Миграции

```bash
python manage.py makemigrations
python manage.py migrate
```

### Стъпка 7: Създаване на Django Groups (Важно!)

Създайте потребителските групи за ролите:

```bash
python manage.py shell
```

В Python shell-а изпълнете:
```python
from django.contrib.auth.models import Group
Group.objects.get_or_create(name='Customer')
Group.objects.get_or_create(name='Staff')
Group.objects.get_or_create(name='Supplier')
Group.objects.get_or_create(name='Admin')
exit()
```

### Стъпка 8: Създаване на суперпотребител

```bash
python manage.py createsuperuser
```

### Стъпка 9: Стартиране на сървъра

```bash
python manage.py runserver
```

Отворете браузър на: **http://127.0.0.1:8000/**

---

## 📁 Структура на проекта

```
AluPVCSystem/
├── AluPVCSystem/          # Главни настройки
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── inventory/             # App за материали
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
├── production/            # App за производство
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── services.py        # Бизнес логика
│   └── admin.py
├── scheduling/            # App за монтажи
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
├── templates/             # HTML шаблони
│   ├── base.html
│   ├── home.html
│   ├── 404.html
│   ├── inventory/
│   ├── production/
│   └── scheduling/
├── static/               # Статични файлове
│   └── css/
│       └── style.css
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🎨 Функционалности

### 0️⃣ Потребителски системи и роли

- **Регистрация и логин с различни роли
- **4 роли**:
  - **Customer (Клиент)** - Може да подава заявки за оглед и да вижда собствените си поръчки
  - **Staff (Персонал)** - Пълен достъп до поръчки, производство и монтажи
  - **Supplier (Доставчик)** - Достъп до материали и доставки
  - **Admin (Администратор)** - Пълен достъп + управление на потребители
- **Одобрение на регистрации** от администратор
- **Различна навигация** според ролята

### 1️⃣ Заявки за безплатен оглед

- Клиентите могат да подават заявки с:
  - Описание на заданието
  - Телефон и адрес за оглед
  - **Качване на снимка/скица** (ImageField)
- Персоналът вижда всички заявки и може да:
  - Променя статуса (Нова → Насрочена → Взети размери → Превърната в поръчка)
  - Добавя бележки
  - Превръща заявката в реална поръчка

### 2️⃣ Управление на материали

- Добавяне на профили (PVC/Алуминий) с характеристики
- Управление на обков и аксесоари
- Автоматично генериране на име на материал
- Филтриране по категории

### 2️⃣ Доставки

- Регистриране на доставки
- Автоматично актуализиране на складови наличности
- Проследяване на доставчици

### 3️⃣ Поръчки

- Създаване на поръчки с данни за клиент
- Добавяне на прозорци и врати с конфигурация на крила
- Добавяне на готови продукти (щори, гаражни врати)
- Автоматично изчисляване на размери на стъклопакети
- Проследяване на статус на поръчка

### 4️⃣ Производство

- Конфигуриране на прозорци:
  - Брой части (1, 2, 3+)
  - ФИКС или ОТВАРЯЕМА за всяка част
  - Равни или неравни части
  - Делители (импости)
- Изчисляване на размери на стъклопакети за всяко крило
- Избор на материали и обков

### 5️⃣ Монтажи

- Планиране на монтажи по дати
- Групиране на поръчки за монтаж
- Филтриране: Минали / Днес / Предстоящи
- Автоматично зареждане на адрес от поръчка

---

## 🛠️ Технологии

- **Backend**: Django 6.0.2
- **Database**: PostgreSQL / SQLite
- **Frontend**: Bootstrap 5.3, HTML5, CSS3, JavaScript
- **Icons**: Bootstrap Icons
- **Version Control**: Git

---

## 👥 Потребителски интерфейс

### Навигация:

- **Материали** - Материали, Доставчици, Доставки
- **Поръчки** - Списък, Детайли, Създаване, Редакция
- **Монтажи** - График, Планиране

### Страници (22 темплейта):

1. Начална страница
2. Списък материали
3. Детайли на материал
4. Добавяне на материал
5. Списък доставчици
6. Списък доставки
7. Добавяне на доставка
8. Списък поръчки
9. Детайли на поръчка
10. Създаване на поръчка
11. Редакция на поръчка
12. Добавяне на прозорец/врата
13. Редакция на прозорец/врата
14. Добавяне на готов продукт
15. Редакция на готов продукт
16. Списък монтажи
17. Детайли на монтаж
18. Планиране на монтаж
19. Редакция на монтаж
20. Confirmation страници за delete (×4)
21. 404 Error page
22. Base template

---

## 📊 Валидации

### Forms (8 форми с validations):

- **MaterialForm**: Автоматично генериране на име, custom валидации
- **SupplierForm**: Валидация на полета
- **DeliveryForm**: Проверка за положителни стойности (quantity > 0, price > 0)
- **OrderForm**: Regex валидация за телефонен номер, MinLength за имена
- **OrderUpdateForm**: Read-only полета
- **CustomProductForm**: Минимални размери (200mm), конфигурация на крила
- **ReadyProductForm**: Валидация на цени
- **InstallationForm**: Валидация на дата, филтриране на поръчки по статус

### Models:

- MinValueValidator за размери и цени
- MinLengthValidator за имена
- Unique constraints
- JSONField за сложни данни (parts_config, custom_widths)

---

## 🔐 Администрация

Достъп до админ панел: **http://127.0.0.1:8000/admin/**

Регистрирани модели:
- Материали
- Категории
- Доставчици
- Доставки
- Поръчки
- Прозорци/Врати
- Готови продукти
- Монтажи

---

## 🧪 Тестване

### Примерни данни:

Използвайте скриптовете за генериране на тестови данни:

```bash
python add_sample_materials.py
python create_test_orders.py
```

Скриптовете създават:
- 9 материала (профили, обков, аксесоари)
- 2 категории (PVC, Алуминий)
- 2 тестови поръчки

### Ръчно тестване:

1. Създайте категории (PVC, Алуминий)
2. Добавете материали (профили, обков)
3. Създайте доставчик
4. Регистрирайте доставка
5. Създайте поръчка
6. Добавете прозорец към поръчката
7. Планирайте монтаж

---

## 🌐 Deployment & Server Architecture

Проектът е разгърнат в облачна среда (AWS EC2) с използване на индустриални стандарти за стабилност и сигурност.

### 🏗️ Стек на производствената среда (Production Stack):

- **Cloud Provider**: AWS (Amazon Web Services) – EC2 Instance (Ubuntu 24.04 LTS)
- **Web Server**: Nginx – служи като Reverse Proxy, обработва статичните файлове и насочва HTTP трафика
- **Application Server**: Gunicorn – WSGI сървър, който предава заявките от Nginx към Django приложението
- **Process Management**: Systemd – използва се за автоматично стартиране и управление на Gunicorn процесите (`gunicorn.service` и `gunicorn.socket`)
- **Static Files Management**: WhiteNoise – сервиране на статични файлове директно от Django
- **Database**: PostgreSQL 14+ на същата EC2 инстанция

### ⚙️ Конфигурационни детайли:

**Security:**
- `DEBUG = False` за предотвратяване изтичането на системна информация
- Конфигуриран `ALLOWED_HOSTS` и `CSRF_TRUSTED_ORIGINS` за IP адреса на инстанцията
- Environment variables за чувствителни данни
- PostgreSQL authentication

**Environment:**
- Изолирана виртуална среда (`venv`) за управление на зависимостите
- Systemd services за автоматично стартиране при ребут

**Performance:**
- Nginx за кеширане и оптимизация на статични файлове
- Gunicorn с 3 worker процеса
- PostgreSQL connection pooling

### 🔄 CI/CD Workflow (Процес на обновяване):

За поддръжка на приложението се използва следният работен процес:

1. **Локална разработка**: Кодът се тества локално в PyCharm
2. **Version Control**: Промените се изтласкват към GitHub хранилище
3. **Deployment**: На AWS сървъра се изпълнява:

```bash
cd /home/ubuntu/AluPVCSystem
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### 📡 Достъп до приложението (Live Demo):

**Проектът е достъпен публично на следния адрес:**

- **Основен адрес**: http://52.47.134.154
- **Административен панел**: http://52.47.134.154/admin

**Тестов администратор:**
- Username: `yaldaz.vacheva`
- Парола: Предоставена при защита
- Забележка: При нужда от тестов достъп преди защитата, моля свържете се с автора на посочения имейл.

### 🔒 Security Note:

> **Забележка**: За целите на прототипа и изпита е използван HTTP протокол. В реална производствена среда би се добавил SSL сертификат чрез Certbot (Let's Encrypt), който да се конфигурира в Nginx за защитена връзка (HTTPS).

### 📋 Deployment Checklist:

- [x] DEBUG = False в production
- [x] SECRET_KEY в environment variable
- [x] ALLOWED_HOSTS конфигурирани
- [x] PostgreSQL база данни
- [x] Gunicorn WSGI server
- [x] Nginx reverse proxy
- [x] Systemd service management
- [x] Static files сервирани от Nginx
- [x] Media files upload директория
- [x] Django-Q2 worker за async задачи
- [ ] SSL/HTTPS (планирано за production)
- [ ] Automated backups (планирано)

---

## 🎓 Проект за изпит Django Basics @ SoftUni

Този проект е създаден за индивидуален изпит по Django Basics @ SoftUni (Април 2026).

### Покрити изисквания:

✅ 3 Django apps (inventory, production, scheduling)
✅ 8 database models
✅ Many-to-One и Many-to-Many relationships
✅ 8 forms с validations
✅ 20+ views (FBV)
✅ 22 templates с dynamic data
✅ Full CRUD за Order, Material, CustomProduct, Installation
✅ Template inheritance и reusable components
✅ Bootstrap design
✅ Navigation на всички страници
✅ 404 error page
✅ PostgreSQL support
✅ Clean code и OOP principles

### Advanced Features:

- JavaScript за dynamic forms
- Автоматично изчисляване на размери на стъклопакети
- JSONField за сложни конфигурации
- services.py за business logic
- Custom CSS styling
- Messages framework
- Filtering и sorting
- Signals/Custom Logic: Автоматична промяна на статуса на поръчките към 'Завършена' при приключване на монтаж.

---

## 📧 Контакти

**Автор**: Йълдъз Въчева  
**GitHub**: [github.com/yaldazv](https://github.com/yaldazv)  
**Email**: yaldazp@gmail.com

---

## 📜 Лиценз

Този проект е създаден за учебни цели като част от курса Django Advanced @ SoftUni.

---

**Дата на създаване**: Февруари 2026  
**Последна актуализация**: Април 2026  
**Deployment**: AWS EC2 (April 2026)

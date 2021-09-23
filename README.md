# Yatube
_______
Yatube - это социальная сеть для публикации постов и записей. Здесь зарегестированные пользователи могут публиковать свои посты, группировать их их по тематикам, комментировать посты других пользователей а также подписываться на их публикации.<br>
Реализована возможность смены и восстановления пароля пользователя по электронной почте, указанной при регистрации.
<br><br>
Стек технологий: Python3, Django 2.2, SQLite3, Git, Pytest, Unittest.
<br><br>
При разработке проекта применялся Python 3.8.<br>
sudo apt-get install python3.7
Для развёртывания проекта выполните следующие действия:<br>
```
git clone https://github.com/Pavel-Maksimov/Yatube.git
```
Перейдите в папку с проектом и создайте и активируйте виртуальное окружение. <br>
Для Windows:
```
python3 -m venv venv
source venv/Scripts/activate
```
Для Linux:
```
python -m venv venv
source venv/bin/activate 
```
Установите все необходимые зависимости:
```
(venv)$pip install -r requirements.txt
```
Для запуска сервера выполните команду:
```
(venv)$python manage.py runserver
```

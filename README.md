<h1>Блог future senior</h1>
Проект задеплоен на python-anywhere, посмотреть, протестировать и оставить комментарий можно здесь: <h3>http://futuresenior.pythonanywhere.com/</h3>
<img src="imgs/1.jpg">

<h3>Future Senior - это улучшенная версия учебного <a href="https://github.com/Viktrols/blog-yatube-yandex-praktikum">проекта</a>, созданного в рамках обучения на курсе Python-разработчик от Я.Практикум</h3>
<h2>Проект позволяет</h2>

<li>регистрироваться и логиниться, восстанавливать пароль по почте</li>
<li>создавать, редактировать, удалять свой профиль (аватар, описание)</li>
<li>создавать, редактировать, удалять и просматривать свои группы</li>
<li>создавать, редактировать, удалять свои записи</li>
<li>просматривать страницы других пользователей</li>
<li>комментировать записи других авторов</li>
<li>подписываться на авторов, просматривать список подписок и подписчиков</li>
<li>Ставить и убирать лайки на публикации</li>
Модерация записей осуществляется через встроенную панель администратора

<h2>Используемые технологии</h2>
<li>Django 2.2</li>
<li>Python 3.8</li>
<li>SQLite</li>
<li>Html-шаблоны со стилями можно скачать <a href="https://html5up.net">здесь</a></li>
<h2>Установка проекта:</h2>
<ol>
  <li>Клонируйте данный репозиторий git clone https://github.com/Viktrols/blog-yatube-yandex-praktikum.git</li>
<li>Создайте и активируйте виртуальное окружение:<br>
python -m venv venv<br>
source ./venv/Scripts/activate  #для Windows<br>
  source ./venv/bin/activate      #для Linux и macOS</li>
<li>Установите требуемые зависимости:

  pip install -r requirements.txt</li>
<li>Примените миграции:

python manage.py migrate</li>

<li>Запустите django-сервер:

python manage.py runserver</li>

Приложение будет доступно по адресу: http://127.0.0.1:8000/
</ol>


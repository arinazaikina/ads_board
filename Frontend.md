# Проблемы frontend

Главная задача этого учебного проекта для python-разработчика - реализовать backend проекта.
В процессе работы над проектом были выявлены некоторые проблемы на frontend.
Какие-то проблемы были решены, а какие-то по-прежнему требуют решения от frontend-разработчика.


# Исправления, которые были внесены в код frontend-а.

## Потеряно поле `re_new_password` в подтверждении смены пароля
`frontend_react/src/components/changePassword/ChangePassword.js`
 
```js
  function heandlerSubmit() {
    changePassword({
      uid: uid,
      token: token,
      new_password: values.new_password,
    })
      .then(() => history.push("/sign-in"))
      .catch((error) => console.log("error", error));
  }
```
Функция для смены пароля никак не обрабатывает поле, куда вводится повтор пароля.

Функция была изменена следующим образом:

```js
  function heandlerSubmit() {
    changePassword({
      uid: uid,
      token: token,
      new_password: values.new_password,
      re_new_password: values.current_password
    })
      .then(() => history.push("/sign-in"))
      .catch((error) => console.log("error", error));
  }
```

## Некорректное округление в пагинации

`frontend_react/src/components/main/Main.js`

Некорректное использование округления `Math.round`, в результате чего происходит
неправильное отображение карточек объявлений на страницах.
Например, если наш список объявлений имеет длину 5, то 4 объявления будут показаны на странице 1,
а пятое объявление не будет показано на странице 2.
Если список объявлений имеет длину 6, то 4 объявления будут показаны на первой странице и 2 объявления
на второй странице.

Для решения это проблемы надо использовать округление вверх к ближайшему большему целому `Math.ceil`.

## Опечатки в placeholder для смены пароля и подтверждения пароля

`frontend_react/src/components/changePassword/ChangePassword.js`

```js
placeholder="пароль дожен сотсоять из букв и цифр"
placeholder="повторите пожалуйста пароль"
```
Внесены следующие изменения
```js
placeholder="пароль должен состоять из букв и цифр"
placeholder="повторите, пожалуйста, пароль"
```

## Есть возможность вводить отрицательную цену
На backend есть ограничение, что цена не может быть отрицательной.
На frontend также разумно ввести такое ограничение.

`frontend_react/src/components/addCard/AddCard.js`

До изменения
```js
<input
  className="userForm__input"
  name="title"
  type="text"
  minLength="3"
  maxLength="30"
  onChange={handleTitleChange}
/>
```

После внесения изменений:

```js
<input
  className="userForm__input"
  type="number"
  name="price"
  minLength="1"
  maxLength="30"
  min="0"
  onChange={handlePriceChange}
/>
```

## Захардкоржена переменные baseURL и BASE_URL

Из-за такого решения сервис можно запустить только на локальной машине.

`frontend_react/src/context/AuthContext.js`
До правок: `const BASE_URL = "http://127.0.0.1:8000/api";` и `const url = "http://127.0.0.1:8000/api/ads/";`
После правок:  `const BASE_URL = `http://${window.location.hostname}:3000/api`;` и `const url = `http://${window.location.hostname}:3000/api/ads/`;`

`frontend_react/src/context/MainContext.js`
До правок: `const BASE_URL = "http://127.0.0.1:8000/api";`
После правок: `const BASE_URL = `http://${window.location.hostname}:3000/api`;`

`frontend_react/src/utils/axiosInstance.js`
До правок: `const baseURL = 'http://127.0.0.1:8000'`
После правок: `const baseURL = `http://${window.location.hostname}:3000`;`

`frontend_react/src/utils/useAxios.js`
До правок: `const baseURL = 'http://127.0.0.1:8000'`
После правок: `const baseURL = `http://${window.location.hostname}:3000`;`

Помимо захардкорживания переменной, почему-то указан порт 8000. У нас же должен работать
nginx, он будет проксировать запросы на backend. Если указывать порт 8000, зачем тогда nginx.

## Нет никаких оповещений пользователю об ошибках

Например, пользователь неправильный пароль, указал телефон в неправильном формате и так далее, 
сервер вернет, например, ответ со статусом 400. Frontend вообще никак не обрабатывает эти случаи.
Пользователь просто не понимает, что происходит.
Сообщение об ошибки выводится только в консоль DevTools. Это совершенно недружелюбное поведение 
с точки зрения пользователя.

Где могла, я просто вывела белые станицы с сообщением об ошибке.
Например:
`frontend_react/src/context/AuthContext.js`
До внесения правок:

```js
  //login
  let loginUser = async (e) => {
    e.preventDefault();
    let response = await fetch(`${BASE_URL}/token/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: e.target.email.value,
        password: e.target.password.value,
      }),
    });
    let data = await response.json();

    if (response.status === 200) {
      setAuthTokens(data);
      setUser(jwt_decode(data.access));
      localStorage.setItem("authTokens", JSON.stringify(data));
      history.push("/");
      window.location.reload();
    } else if (response.status === 500) {
      console.log("Неполадки на сервере");
    } else if (response.status === 401) {
      console.log("введен неккоректный email или пароль");
    } else {
      console.log(response.status);
    }
  };
```
После:

```js
//login
  let loginUser = async (e) => {
    e.preventDefault();
    let response = await fetch(`${BASE_URL}/token/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: e.target.email.value,
        password: e.target.password.value,
      }),
    });
    let data = await response.json();

    if (response.status === 200) {
      setAuthTokens(data);
      setUser(jwt_decode(data.access));
      localStorage.setItem("authTokens", JSON.stringify(data));
      history.push("/");
      window.location.reload();
    } else if (response.status === 500) {
      console.log("Неполадки на сервере");
      document.body.innerHTML = '<h1>Неполадки на сервере</h1>';
    } else if (response.status === 401) {
      console.log("введен неккоректный email или пароль");
      document.body.innerHTML = '<h1>Введен некорректный email или пароль</h1>';
    } else {
      console.log(response.status);
      document.body.innerHTML = '<h1>Неизвестная ошибка</h1>';
    }
  };
```
Я отдаю себе отчет, что так делать - категорически неверно.
Это пока просто заглушка. На frontend необходимо реализовать полноценный
функционал обработки ошибок.

## Пользователь с ролью `admin` через UI-интерфейс не может изменять или удалять комментарии и объявления
Иконки удаления и редактирования комментариев и объявлений других пользователей
недоступны (не отрисованы) на UI-интерфейсе для пользователя с ролью `admin`.
На backend эта логика реализована.
Сейчас пользователь с ролью `admin` может изменять или удалять комментарии и объявления через административную панель,
хотелось бы, чтобы он мог это делать и через UI-интерфейс.

## Некорректно описан docker-compose в части сборки и запуска контейнера nginx

Папки файлов с ресурсами монтируются туда же, куда монтируется папка с генерируемым контентом `html`.
Так как контейнер `frontend_ads` перед генерацией html-контента чистит папку html, то временно удаляются папки 
с ресурсами в контейнере `nginx`. Лечилось перезагрузкой контейнера `nginx`. Чтобы не перезагружать контейнер `nginx`,
был изменен docker-compose и nginx.conf.

До изменения:
```yaml
volumes:
      - ../skymarket/django_static/:/usr/share/nginx/html/django_static/
      - ../skymarket/django_media/:/usr/share/nginx/html/django_media/
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - frontend:/usr/share/nginx/html/
```
```
    location /django_media/ {
        alias /usr/share/nginx/html/django_media/;
    }

    location /django_static/ {
        alias /usr/share/nginx/html/django_static/;
    }
```
После изменения
```yaml
volumes:
      - ../skymarket/django_static/:/usr/share/nginx/django_static/
      - ../skymarket/django_media/:/usr/share/nginx/django_media/
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - frontend:/usr/share/nginx/html/
```
```
    location /django_media/ {
        alias /usr/share/nginx/django_media/;
    }

    location /django_static/ {
        alias /usr/share/nginx/django_static/;
    }
```

# То, что требует доработки

1. Необходимо реализовать полноценную обработку ошибок на frontend.
2. Необходимо реализовать возможность удалять/редактировать объявления/отзывы пользователю с ролью admin через
UI-интерфейс
3. В форме создания объявление поле "Описание" ограничено по количеству вводимых символов. Пользователь может вводить
больше символов (на backend есть такая возможность). Если потом редактировать карточку созданного объявления, то 
можно ввести больше символов, но происходит переполнение верстки и описание выходит за пределы карточки объявления.
Backend дает возможность вводить длинные описания и отзывы, но frontend нет.
4. Необходимо добавить какие-то сообщения пользователю, когда он что-то делает успешно, например, когда добавил
новое объявление. Сейчас когда пользователь добавляет объявление, совсем не ясно, успешно он его добавил или нет. 
Только при переходе на главную страницу, можно убедиться, что объявление действительно добавлено. Это неудобно.
5. При обновлении страницы профиля юзера "мелькает" дефолтная картинка.
6. При изменении телефона пользователя в профиле, если он введет телефон не в формате `+7(***)***-**-**` не будет
никаких сообщений об ошибке, он просто не сохраниться. Опять же недружелюбное поведение, надо писать обработку ошибок.
7. Хочется, чтобы была кликабельной иконка пакета в верхнем левом углу.
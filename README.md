# APIVk

Это методы, которые возращают json с данными из вк

***Порядок получения токена таков:***

- Нажимаете на кнопку создать приложение

- Выбираете standalone приложение, указываете название приложения

- Переходите в настройки, включаете Open API

- В поле *адрес сайта* вводите http://localhost

- В поле базовый домен вводите localhost

- Сохраняете изменения

- Копируете id приложения

- В ссылку

https://oauth.vk.com/authorize?client_id=1&display=page&scope=stats,offline&response_type=token&v=5.131 вместо 1 вставьте id **вашего** приложения. Не забудьте указать scope: [Список названий прав доступа](https://dev.vk.com/reference/access-rights), которые необходимы приложению,  или сумма их битовых масок передается в параметре scope в процессе получения ключа доступа.

- Нажимаете разрешить

- Сохраняете токен

***/vk*** доступ к api vk

___POST___

_/vk/search_users_ - Забирает данные из vk по критериям поиска, указанным в параметрах

*Parameters*
token - токен, полученный выше ,
age_from - возраст от ,
age_to - возраст до,
sex - пол(по умолчанию 0-любой), принимает 1(ж) или 2(м) ,
city - город(работает только с городами РФ),
count - кол-во профилей, которые вы хотите получить(не всегда будет совпадать с полученным количеством, так как закрытые профили будут пропущены

Responses 200 успешно

возвращает json вида:

```
{
   "data": [
      {
         "id": 290192019,
         "photo": "https://sun7-8.userapi.com/s/v1/ig2/9oj0PoeHtX6-BxlX8DxMkj_bAC-ZiEddZ1H2qJdAvrJynENAy8LSRbqxbvPCXV4YEdpo3gcv8Pmo-P10h_kHACb3.jpg?size=50x50&quality=96&crop=43,0,1152,1152&ava=1",
         "track_code": "531fa3d7OVXcU-1iVfJyhkDrObwuxKWIOtKHKIojy_s0f9waR8VePJlVtQ9U-HPWeh7dLJnFzYY80YcohEW5kg",
         "screen_name": "liluuuuuuuush",
         "first_name": "Лили",
         "last_name": "Акопян",
         "can_access_closed": true,
         "is_closed": false
      },
      {
         "id": 139087663,
         "photo": "https://sun7-6.userapi.com/s/v1/ig2/RJU-nMVVV8Z9lJqXfeS0bwm7vUseq0Lo26O5lgt9pOQJlzCPbNa0fF98olz7b4Mzq022lYHSRM9kwaxSgbSdZzjt.jpg?size=50x50&quality=95&crop=429,730,1099,1099&ava=1",
         "track_code": "4709a461y2qPGXkhzctFXRvW797XKs5jUq3g5ZwA8ZFbWZs5-gCsA8VNI03Oy0hZKyYNSWorpm1UruDlkmaD-A",
         "screen_name": "aleksaaminaeva",
         "first_name": "Александра",
         "last_name": "Минаева",
         "can_access_closed": true,
         "is_closed": false
      }
}
```


___POST___

_/vk/get_leads_   -  автоматически забирает новые лиды из vk при их получении из формы

*Parameters*


Responses 200 успешно

возвращает json вида:

```
{"data": [{"name": name}, {"phone": phone}]}
```


***Авторизационные данные:***
- access_token пользовательский токен , полученный по инструкции выше
    - scope: [Список названий прав доступа](https://dev.vk.com/reference/access-rights), которые необходимы приложению,  или сумма их битовых масок передается в параметре scope в процессе получения ключа доступа.
        - adv доступ к рекламным кабинетам;
        - groups доступ к группам пользователя;
        - stats доступ к статистике групп и приложений пользователя, администратором которых он является;
        - offline доступ к API в любое время.

- для методов get_leads и get_leads_online необходимо генерировать уникальный ключ
    - id группы
    - id формы для получения лидов
    - *ПРОПИСАТЬ СГЕНЕРИРОВАННЫЙ URL В НАСТРОЙКАХ СООБЩЕСТВА***
        - в сообществе переходим у "управление"
        - справа "работа с API"
        - callback api -> адрес (сюда вставить url)

- для рекламных методов:
    - get_flood_stats (account_id - Идентификатор рекламного кабинета)
    - get_posts_reach (account_id - Идентификатор рекламного кабинета, ids - Перечисленные через запятую id запрашиваемых объявлений или кампаний)
    - [get_targeting_stats](https://dev.vk.com/method/ads.getTargetingStats)
    - [get_targeting](https://dev.vk.com/method/ads.getAdsTargeting)
    - get_demographics(account_id - Идентификатор рекламного кабинета, ids - Перечисленные через запятую id запрашиваемых объявлений или кампаний)
    - get_statistic(account_id - Идентификатор рекламного кабинета, ids - Перечисленные через запятую id запрашиваемых объявлений или кампаний)


from datetime import date, timedelta

VK_VERSION = '5.131'


def item_in(name, json_file):
    if f'{name}' in json_file['data'][0]:
        name = json_file['data'][0][f'{name}']
        return name
    else:
        name = None
        return name


def search_users(vk, age_from=18, age_to=100, sex=0, city=1, count=10, offset=1):
    res = []
    result = vk.method('users.search', {
        'offset': offset,
        'age_from': age_from,
        'age_to': age_to,
        'sex': sex,
        'city': city,
        'has_photo': 1,
        'fields': 'photo, screen_name',
        'count': count,
        'v': VK_VERSION
    })
    for items in result['items']:
        is_closed = items['is_closed']
        if is_closed:
            offset += 1
        else:
            res.append(items)
    return res


def get_city_id_(vk, keyword):
    result = vk.method('database.getCities', {'country_id': 1, 'q': keyword})
    for items in result['items']:
        return items['id']


def get_confirmation_code_(vk, group_id):
    """Возвращает статистику показателей эффективности по рекламным
    объявлениям, кампаниям, клиентам или всему кабинету."""
    result = vk.method('groups.getCallbackConfirmationCode', {"group_id": group_id})
    for k, v in result.items():
        return v


def get_leads_(vk, group_id, form_id=1):
    """Получает список лидов с конкретной формы"""

    result = vk.method('leadForms.getLeads', {
        'group_id': group_id,
        'form_id': form_id,
        'v': VK_VERSION})
    return result['leads']


def ads_get_statistic(vk, date_from, date_to, period, account_id=None, ids=None):
    """Возвращает статистику показателей эффективности по рекламным объявлениям,
    кампаниям, клиентам или всему кабинету."""
    result = vk.method('ads.getStatistics', {'account_id': account_id, 'period': period,
                                             'date_from': date_from, 'date_to': date_to, 'ids_type': 'ad', 'ids': ids,
                                             'v': VK_VERSION})
    r = result.json()
    error = r.get('error')
    if error:
        error_code = r.get('error').get('error_code')
        error_msg = r.get('error').get('error_msg')
        raise ValueError(f"error_code={error_code}, error_msg={error_msg}")
    spent = r['response'][0]['stats']['spent']
    impressions = r['response'][0]['stats']['impressions']
    clicks = r['response'][0]['stats']['clicks']
    id_ = r['response'][0]['id']
    if period == 'day':
        expense_period = r['response'][0]['stats']['day']
    else:
        expense_period = date_from / date_to
    info = {
        "data": [{"id": id_, "Expenses": spent, "Impressions": impressions, "Clicks": clicks, "Date": expense_period}]}
    return info


def ads_get_demographics(vk, account_id=None, ids=None):
    """Возвращает демографическую статистику по рекламным объявлениям или кампаниям."""

    result = vk.method('ads.getDemographics', {'account_id': account_id, 'ids_type': 'ad', 'ids': ids,
                                               'period': 'day',
                                               'date_from': date.today(), 'date_to': date.today(),
                                               'v': VK_VERSION})
    r = result.json()
    error = r.get('error')
    if error:
        error_code = r.get('error').get('error_code')
        error_msg = r.get('error').get('error_msg')
        raise ValueError(f"error_code={error_code}, error_msg={error_msg}")
    sex = r['response'][0]['stats']['sex']
    age = r['response'][0]['stats']['age']
    cities = r['response'][0]['stats']['cities']
    info = {
        "data": [{"cities": cities}, {"age": age}, {"sex": sex}]}
    return info


def ads_get_AdsTargeting(vk, account_id=None, client_id=None, include_deleted=None,
                     campaign_ids=None, ad_id=None, limit=None, offset=None):
    """Возвращает параметры таргетинга рекламных объявлений"""
    result = vk.method('ads.getAdsTargeting', {
        'account_id': account_id,
        'client_id': client_id,
        'include_deleted': include_deleted,
        'campaign_ids': campaign_ids,
        'ad_id': ad_id,
        'limit': limit,
        'offset': offset,
        'v': VK_VERSION
    })
    r = result.json()
    return r


def ads_get_PostsReach(vk, account_id=None, ids=None):
    """Возвращает подробную статистику по охвату рекламных записей из объявлений и кампаний для
    продвижения записей сообщества."""
    result = vk.method('ads.getPostsReach', {'account_id': account_id, 'ids_type': 'ad', 'ids': ids, 'v': VK_VERSION})
    r = result.json()['response'][0]
    return r


def ads_get_TargetingStats(vk, account_id=None, criteria=None, ad_id=None, ad_format=None,
                       ad_platform=None, link_url=None, link_domain=None):
    """Возвращает размер целевой аудитории таргетинга, а также рекомендованные
    значения CPC и CPM."""
    result = vk.method('ads.getTargetingStats', {
        'account_id': account_id,
        'criteria': criteria,
        'ad_format': ad_format,
        'ad_platform': ad_platform,
        'ad_id': ad_id,
        'link_url': link_url,
        'link_domain': link_domain,
        'v': VK_VERSION

    })
    r = result.json()
    return r


def ads_get_FloodStats(vk, account_id=None):
    """Возвращает информацию о текущем состоянии счетчика — количество оставшихся запусков методов и время до следующего
    обнуления счетчика в секундах."""
    result = vk.method('ads.getFloodStats', {'account_id': account_id, 'v': VK_VERSION})
    return result.json()


def ads_get_budget(vk, account_id=None):
    """Возвращает текущий бюджет рекламного кабинета."""
    result = vk.method('ads.getBudget', {'account_id': account_id, 'v': VK_VERSION})
    return result.json()


def market_get_product_by_id(vk, item_ids):
    """Возвращает информацию о товарах по идентификаторам."""
    result = vk.method('market.getById', {'item_ids': item_ids, 'v': VK_VERSION})
    return result.json()


def market_get_order_by_id(vk, order_id, user_id=None):
    """Возвращает заказ по идентификатору."""
    result = vk.method('market.getOrderById', {'order_id': order_id, 'user_id': user_id, 'v': VK_VERSION})
    return result.json()


def market_edit_order(vk, user_id, order_id, merchant_comment=None, status=None, track_number=None, payment_status=None,
                      delivery_price=None):
    """Редактирует заказ."""
    result = vk.method('market.editOrder', {'order_id': order_id, 'user_id': user_id, 'merchant_comment':
                                            merchant_comment, 'status': status, 'track_number': track_number, 'payment_status': payment_status,
                                            'delivery_price': delivery_price, 'v': VK_VERSION})
    return result.json()


def market_add(vk, owner_id, name, description, category_id=None, price=None, url_=None, sku=None):
    """Добавляет новый товар."""
    result = vk.method('market.add', {'owner_id': owner_id, 'name': name, 'description':
                                      description, 'category_id': category_id, 'price': price, 'url': url_,
                                      'sku': sku, 'v': VK_VERSION})
    return result.json()


def market_edit(vk, owner_id, item_id, category_id=None, description=None, price=None, sku=None, url_=None, name=None):
    """Редактирует товар."""
    result = vk.method('market.edit', {'owner_id': owner_id, 'item_id': item_id, 'name': name, 'description':
                                       description, 'category_id': category_id, 'price': price, 'url': url_,
                                       'sku': sku, 'v': VK_VERSION})
    return result.json()


def market_create_comment(vk, owner_id, item_id, message_=None, attachments=None, from_group=None,
                          reply_to_comment=None, guid=None):
    """Создаёт новый комментарий к товару."""
    result = vk.method('market.createComment', {'owner_id': owner_id, 'item_id': item_id, 'message': message_,
                                                'attachments': attachments, 'from_group': from_group,
                                                'reply_to_comment': reply_to_comment, 'guid': guid, 'v': VK_VERSION})
    return result.json()


def market_add_album(vk, owner_id, title, main_album=None, photo_id=None):
    """Добавляет новую подборку с товарами."""
    result = vk.method('market.addAlbum', {'owner_id': owner_id, 'title': title, 'photo_id': photo_id,
                                           'main_album': main_album, 'v': VK_VERSION})
    return result.json()


def market_edit_album(vk, owner_id, album_id, title, main_album=None, photo_id=None):
    """Редактирует подборку с товарами."""
    result = vk.method('market.editAlbum', {'owner_id': owner_id, 'title': title, 'album_id': album_id,
                                            'main_album': main_album, 'photo_id': photo_id, 'v': VK_VERSION})
    return result.json()


def market_add_to_album(vk, owner_id, album_ids, item_id=None, item_ids=None):
    """Добавляет товар в одну или несколько выбранных подборок."""
    result = vk.method('market.addToAlbum', {'owner_id': owner_id, 'item_id': item_id, 'item_ids': item_ids,
                                             'album_ids': album_ids, 'v': VK_VERSION})
    return result.json()

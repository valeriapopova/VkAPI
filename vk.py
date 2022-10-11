from datetime import date

VK_VERSION = '5.131'


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


def get_city_id(vk, keyword):
    result = vk.method('database.getCities', {'country_id': 1, 'q': keyword})
    for items in result['items']:
        return items['id']


def get_confirmation_code(vk, group_id):
    """Возвращает статистику показателей эффективности по рекламным
    объявлениям, кампаниям, клиентам или всему кабинету."""
    result = vk.method('groups.getCallbackConfirmationCode', {"group_id": group_id})
    for k, v in result.items():
        return v


def get_leads(vk, group_id, form_id=1):
    """Получает список лидов с конкретной формы"""

    result = vk.method('leadForms.getLeads', {
        'group_id': group_id,
        'form_id': form_id,
        'v': VK_VERSION})
    return result['leads']


def ads_get_statistic(vk, date, account_id=None, ids=None):
    """Возвращает статистику показателей эффективности по рекламным объявлениям,
    кампаниям, клиентам или всему кабинету."""
    result = vk.method('ads.getStatistics', {'account_id': account_id, 'period': 'day',
                       'date_from': date, 'date_to': date, 'ids_type': 'ad', 'ids': ids,
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
    info = {"data": [{"spent(потраченные средства)": spent}, {"impressions(просмотры)": impressions}, {"clicks": clicks}]}
    return info


def get_demographics(vk, account_id=None, ids=None):
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
    spent = r['response'][0]['stats']['spent']
    impressions = r['response'][0]['stats']['impressions']
    clicks = r['response'][0]['stats']['clicks']
    info = {
        "data": [{"spent(потраченные средства)": spent}, {"impressions(просмотры)": impressions}, {"clicks": clicks}]}
    return info


def get_AdsTargeting(vk, account_id=None, client_id=None, include_deleted=None,
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


def get_PostsReach(vk, account_id=None, ids=None):
    """Возвращает подробную статистику по охвату рекламных записей из объявлений и кампаний для
    продвижения записей сообщества."""
    result = vk.method('ads.getPostsReach', {'account_id': account_id, 'ids_type': 'ad', 'ids': ids, 'v': VK_VERSION})
    r = result.json()['response'][0]
    return r


def get_TargetingStats(vk, account_id=None, criteria=None, ad_id=None, ad_format=None,
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


def get_FloodStats(vk, account_id=None):
    """Возвращает информацию о текущем состоянии счетчика — количество оставшихся запусков методов и время до следующего
    обнуления счетчика в секундах."""
    result = vk.method('ads.getFloodStats', {'account_id': account_id, 'v': VK_VERSION})
    return result.json()


def get_budget(vk, account_id=None):
    """Возвращает текущий бюджет рекламного кабинета."""
    result = vk.method('ads.getBudget', {'account_id': account_id, 'v': VK_VERSION})
    return result.json()

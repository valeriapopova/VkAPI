

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
        'count': count
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



import hashlib
import secrets
from collections import defaultdict
from datetime import datetime
from flask import Flask, render_template, request
import json
from datetime import date, timedelta

from config import Configuration
from forms import VKForm
import vk_api
from vk import *
app = Flask(__name__)
app.config.from_object(Configuration)


@app.route('/vk/get_key', methods=['POST'])
def homepage():
    """Возвращет пользователю - уникальный сгенерированный URL(только для метода online_notification)"""
    webhook = request.get_json(force=False)
    webhook_account_name = webhook['account_name']
    salt = secrets.token_hex(16) + webhook_account_name
    url = 'https://api.ecomru.ru/vk/online_notification'
    url_key = hashlib.sha256(salt.encode('utf-8')).hexdigest()
    key = f'{url}/{url_key}'
    print(key)
    return key


@app.route('/vk/search_users',  methods=['GET', 'POST'])
def search_users_vk():
    if request.method == 'POST':
        vk_token = request.form['token']
        vk = vk_api.VkApi(token=vk_token)
        age_from = request.form['age_from']
        age_to = request.form['age_to']
        sex = request.form['sex']
        city = request.form['city']
        city_id = get_city_id_(vk, city)
        count = request.form['count']
        result = {}
        res = search_users(vk, age_from, age_to, sex, city_id, count)
        result['data'] = res
        return json.dumps(result)

    form = VKForm()
    return render_template('create_json.html', form=form), 200


@app.route('/vk/get_leads', methods=['POST'])
def processiong():
    # Миграция данных (Сбор данных за период в прошлом)
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    group_id = json_file['data'][0]['group_id']
    form_id = json_file['data'][0]['form_id']

    vk = vk_api.VkApi(token=vk_token)
    result = get_leads_(vk, group_id, form_id)
    info = {}
    result_list = defaultdict(list)
    for r in result:
        lead_id = r['lead_id']
        result_list["lead_id"].append(lead_id)
        counter = 0
        while counter < len(r['answers']):
            v = r['answers'][counter]['answer']['value']
            k = r['answers'][counter]['key']
            counter += 1
            result_list[k].append(v)

    info['data'] = [result_list]
    print(info)
    return info


@app.route('/vk/online_notification/<key>', methods=['POST'])
def processiong_():
#В реальном времени (Сбор данных текущего периода)
    data = request.get_json(force=True, silent=True)
    if data:
        if data['type'] == 'lead_forms_new':
            type_ = 'новый лид'
            name = str(data['object']['answers'][0]['answer'])
            phone = str(data['object']['answers'][1]['answer'])
            info = {"data": [{"type": type_}, {"first_name": name}, {"phone_number": phone}]}
            return info
        elif data['type'] == 'message_new':
            type_ = 'новое сообщение'
            text = str(data["object"]["message"]["text"])
            from_id = str(data['object']['message']['from_id'])
            info = {"data": [{"type": type_}, {"peer_id": from_id}, {"text": text}]}
            return info
        elif data['type'] == 'market_order_new':
            type_ = 'новый заказ'
            user_id = str(data["object"]["user_id"])
            order_id = str(data['object']['id'])
            price = str(data['object']['total_price']['amount'])
            date_timestamp = data['object']['date']
            date = datetime.fromtimestamp(date_timestamp, tz=None)
            status = str(data['object']['status'])
            info = {"data": [{"type": type_, "order_id": order_id, "user_id": user_id, "status": status,
                              "price": price, "date": date}]}

            return info
        elif data['type'] == 'market_order_edit':
            type_ = 'изменение заказа'
            user_id = str(data["object"]["user_id"])
            order_id = str(data['object']['id'])
            price = str(data['object']['total_price']['amount'])
            status = str(data['object']['status'])
            date_timestamp = data['object']['date']
            date = datetime.fromtimestamp(date_timestamp, tz=None)
            info = {"data": [{"type": type_, "order_id": order_id, "user_id": user_id, "status": status,
                             "price": price, "date": date}]}
            return info
        else:
            pass


@app.route('/vk/ads_get_month_statistic', methods=['POST'])
def get_month_statistic():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = item_in('account_id', json_file)
    ids = item_in('ids', json_file)
    vk = vk_api.VkApi(token=vk_token)
    date_from = date.today() - timedelta(days=30)
    date_to = date.today()
    period = 'month'
    result = ads_get_statistic(vk, date_from, date_to, period, account_id, ids)
    return result


@app.route('/vk/ads_get_statistic_current_day', methods=['POST'])
def get_statistic_current_day():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = item_in('account_id', json_file)
    ids = item_in('ids', json_file)
    vk = vk_api.VkApi(token=vk_token)
    date_ = date.today()
    period = 'day'
    result = ads_get_statistic(vk, date_, date_, period, account_id, ids)
    return result


@app.route('/vk/ads_get_statistic_yesterday', methods=['POST'])
def get_statistic_yesterday():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = item_in('account_id', json_file)
    ids = item_in('ids', json_file)
    vk = vk_api.VkApi(token=vk_token)
    date_ = date.today() - timedelta(days=1)
    period = 'day'
    result = ads_get_statistic(vk, date_, date_, period, account_id, ids)
    return result


@app.route('/vk/ads_get_demographics', methods=['POST'])
def get_demographics():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = item_in('account_id', json_file)
    ids = item_in('ids', json_file)
    vk = vk_api.VkApi(token=vk_token)
    result = ads_get_demographics(vk, account_id, ids)
    return result


@app.route('/vk/ads_get_targeting', methods=['POST'])
def get_targeting():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']

    account_id = item_in('account_id', json_file)
    client_id = item_in('client_id', json_file)
    include_deleted = item_in('include_deleted', json_file)
    campaign_ids = item_in('campaign_ids', json_file)
    limit = item_in('limit', json_file)
    ad_id = item_in('ad_id', json_file)
    offset = item_in('offset', json_file)

    vk = vk_api.VkApi(token=vk_token)
    data = {}
    result = ads_get_AdsTargeting(vk, account_id, client_id, include_deleted, campaign_ids, ad_id, limit, offset)
    data['data'] = result['response']
    return data


@app.route('/vk/ads_get_targeting_stats', methods=['POST'])
def get_targeting_stats():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']

    account_id = item_in('account_id', json_file)
    criteria = item_in('criteria', json_file)
    ad_format = item_in('ad_format', json_file)
    ad_platform = item_in('ad_platform', json_file)
    link_url = item_in('link_url', json_file)
    ad_id = item_in('ad_id', json_file)
    link_domain = item_in('link_domain', json_file)

    vk = vk_api.VkApi(token=vk_token)
    result = ads_get_TargetingStats(vk, account_id, criteria, ad_format, ad_platform, ad_id, link_url, link_domain)
    return result


@app.route('/vk/ads_get_posts_reach', methods=['POST'])
def get_posts_reach():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = item_in('account_id', json_file)
    ids = item_in('ids', json_file)
    vk = vk_api.VkApi(token=vk_token)
    result = ads_get_PostsReach(vk, account_id, ids)
    return result


@app.route('/vk/ads_get_flood_stats', methods=['POST'])
def get_flood_stats():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = item_in('account_id', json_file)
    vk = vk_api.VkApi(token=vk_token)
    data = {}
    result = ads_get_FloodStats(vk, account_id)
    data['data'] = result['response']
    return data


@app.route('/vk/ads_get_budget', methods=['POST'])
def get_budget():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = item_in('account_id', json_file)
    vk = vk_api.VkApi(token=vk_token)
    data = {}
    result = ads_get_budget(vk, account_id)
    data['data'] = result['response']
    return data


@app.route('/vk/market_get_product_by_id', methods=['POST'])
def get_product_by_id():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    item_ids = json_file['data'][0]['item_ids']
    vk = vk_api.VkApi(token=vk_token)
    data = {}
    result = market_get_product_by_id(vk, item_ids)
    data['data'] = result['response']
    return data


@app.route('/vk/market_get_order_by_id', methods=['POST'])
def get_order_by_id():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    order_id = json_file['data'][0]['order_id']
    user_id = item_in('user_id', json_file)
    vk = vk_api.VkApi(token=vk_token)
    data = {}
    result = market_get_order_by_id(vk, order_id, user_id)
    data['data'] = result['response']
    return data


@app.route('/vk/market_edit_order', methods=['POST'])
def edit_order():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    order_id = json_file['data'][0]['order_id']
    user_id = json_file['data'][0]['user_id']

    merchant_comment = item_in('merchant_comment', json_file)
    status = item_in('status', json_file)
    track_number = item_in('track_number', json_file)
    payment_status = item_in('payment_status', json_file)
    delivery_price = item_in('delivery_price', json_file)

    vk = vk_api.VkApi(token=vk_token)
    data = {}
    result = market_edit_order(vk, user_id, order_id, merchant_comment, status, track_number,
                               payment_status, delivery_price)
    data['data'] = result['response']
    return data


@app.route('/vk/market_add', methods=['POST'])
def market_add_():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    owner_id = json_file['data'][0]['owner_id']
    name = json_file['data'][0]['name']
    description = json_file['data'][0]['description']

    category_id = item_in('category_id', json_file)
    price = item_in('price', json_file)
    url_ = item_in('url', json_file)
    sku = item_in('sku', json_file)

    vk = vk_api.VkApi(token=vk_token)
    data = {}
    result = market_add(vk, owner_id, name, description, category_id, price, url_, sku)
    data['data'] = result['response']
    return data


@app.route('/vk/market_edit', methods=['POST'])
def market_edit_():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    owner_id = json_file['data'][0]['owner_id']
    item_id = json_file['data'][0]['item_id']

    name = item_in('name', json_file)
    description = item_in('description', json_file)
    category_id = item_in('category_id', json_file)
    price = item_in('price', json_file)
    url_ = item_in('url', json_file)
    sku = item_in('sku', json_file)

    vk = vk_api.VkApi(token=vk_token)
    data = {}
    result = market_edit(vk, owner_id, item_id, name, description, category_id, price, url_, sku)
    data['data'] = result['response']
    return data


@app.route('/vk/market_create_comment', methods=['POST'])
def create_comment():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    owner_id = json_file['data'][0]['owner_id']
    item_id = json_file['data'][0]['item_id']

    message_ = item_in('message', json_file)
    attachments = item_in('attachments', json_file)
    from_group = item_in('from_group', json_file)
    reply_to_comment = item_in('reply_to_comment', json_file)
    guid = item_in('guid', json_file)

    vk = vk_api.VkApi(token=vk_token)
    data = {}
    result = market_create_comment(vk, owner_id, item_id, message_, attachments, from_group,
                                   reply_to_comment, guid)
    data['data'] = result['response']
    return data


@app.route('/vk/market_add_album', methods=['POST'])
def add_album():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    owner_id = json_file['data'][0]['owner_id']
    title = json_file['data'][0]['title']

    main_album = item_in('main_album', json_file)
    photo_id = item_in('photo_id', json_file)

    vk = vk_api.VkApi(token=vk_token)
    data = {}
    result = market_add_album(vk, owner_id, title, main_album, photo_id)
    data['data'] = result['response']
    return data


@app.route('/vk/market_edit_album', methods=['POST'])
def edit_album():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    owner_id = json_file['data'][0]['owner_id']
    title = json_file['data'][0]['title']
    album_id = json_file['data'][0]['album_id']

    main_album = item_in('main_album', json_file)
    photo_id = item_in('photo_id', json_file)

    vk = vk_api.VkApi(token=vk_token)
    data = {}
    result = market_edit_album(vk, owner_id, album_id, title, main_album, photo_id)
    data['data'] = result['response']
    return data


@app.route('/vk/market_add_to_album', methods=['POST'])
def add_to_album():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    owner_id = json_file['data'][0]['owner_id']
    album_ids = json_file['data'][0]['album_ids']

    item_id = item_in('item_id', json_file)
    item_ids = item_in('item_ids', json_file)

    vk = vk_api.VkApi(token=vk_token)
    data = {}
    result = market_add_to_album(vk, owner_id, album_ids, item_id, item_ids)
    data['data'] = result['response']
    return data

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
from vk import get_city_id, search_users, get_confirmation_code, get_leads, ads_get_statistic, get_demographics, \
    get_AdsTargeting, get_TargetingStats, get_PostsReach, get_FloodStats

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
        city_id = get_city_id(vk, city)
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
    group_id = json_file['group_id']
    form_id = json_file['form_id']

    vk = vk_api.VkApi(token=vk_token)
    result = get_leads(vk, group_id, form_id)
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

        # if r['answers'][0]['key']:
        #     first_name = r['answers'][0]['answer']['value']
        #     first_name_ = r['answers'][0]['key']
        # if r['answers'][1]['key']:
        #     patronymic_name = r['answers'][1]['answer']['value']
        #     patronymic_name_ = r['answers'][1]['key']
        # if r['answers'][2]['key']:
        #     last_name = r['answers'][2]['answer']['value']
        #     last_name_ = r['answers'][2]['key']
        # if r['answers'][3]['key']:
        #     email = r['answers'][3]['answer']['value']
        #     email_ = r['answers'][3]['key']
        # if r['answers'][4]['key']:
        #     phone_number = r['answers'][4]['answer']['value']
        #     phone_number_ = r['answers'][4]['key']
        # if r['answers'][5]['key']:
        #     age = r['answers'][5]['answer']['value']
        #     age_ = r['answers'][5]['key']
        # if r['answers'][6]['key']:
        #     birthday = r['answers'][6]['answer']['value']
        #     birthday_ = r['answers'][6]['key']
        # if r['answers'][7]['key']:
        #     location = r['answers'][7]['answer']['value']
        #     location_ = r['answers'][7]['key']
        # if r['answers'][8]['key']:
        #     custom_0 = r['answers'][8]['answer']['value']
        #     custom_0_ = r['answers'][8]['key']
        #
        # result_list["lead_id"].append(lead_id)
        # if first_name_:
        #     result_list[first_name_].append(first_name)
        # if phone_number_:
        #     result_list[phone_number_].append(phone_number)
        # if patronymic_name_:
        #     result_list[patronymic_name_].append(patronymic_name)
        # if last_name_:
        #     result_list[last_name_].append(last_name)
        # if email_:
        #     result_list[email_].append(email)
        # if age_:
        #     result_list[age_].append(age)
        # if birthday_:
        #     result_list[birthday_].append(birthday)
        # if location_:
        #     result_list[location_].append(location)
        # if custom_0_:
        #     result_list[custom_0_].append(custom_0)

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

            info = {"data": [{"type": type_}, {"order_id": order_id}, {"user_id": user_id}, {"status": status},
                             {"price": price}, {"date": date}]}
            return info
        elif data['type'] == 'market_order_edit':
            type_ = 'изменение заказа'
            user_id = str(data["object"]["user_id"])
            order_id = str(data['object']['id'])
            price = str(data['object']['total_price']['amount'])
            status = str(data['object']['status'])
            date_timestamp = data['object']['date']
            date = datetime.fromtimestamp(date_timestamp, tz=None)
            info = {"data": [{"type": type_}, {"order_id": order_id}, {"user_id": user_id}, {"status": status},
                             {"price": price}, {"date": date}]}
            return info
        else:
            pass


@app.route('/vk/ads_get_month_statistic', methods=['POST'])
def get_month_statistic():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = json_file['account_id']
    ids = json_file['ids']
    vk = vk_api.VkApi(token=vk_token)
    date_from = date.today() - timedelta(days=30)
    date_to = date.today()
    result = ads_get_statistic(vk, date_from, date_to, account_id=account_id, ids=ids)
    return result


@app.route('/vk/ads_get_statistic_current_day', methods=['POST'])
def get_statistic_current_day():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = json_file['account_id']
    ids = json_file['ids']
    vk = vk_api.VkApi(token=vk_token)
    date_ = date.today()
    result = ads_get_statistic(vk, date_, date_, account_id=account_id, ids=ids)
    return result


@app.route('/vk/ads_get_statistic_yesterday', methods=['POST'])
def get_statistic_yesterday():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = json_file['account_id']
    ids = json_file['ids']
    vk = vk_api.VkApi(token=vk_token)
    date_ = date.today() - timedelta(days=1)
    result = ads_get_statistic(vk, date_, date_, account_id=account_id, ids=ids)
    return result


@app.route('/vk/ads_get_demographics', methods=['POST'])
def get_demographics():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = json_file['account_id']
    ids = json_file['ids']
    vk = vk_api.VkApi(token=vk_token)
    result = get_demographics(vk, account_id=account_id, ids=ids)
    return result


@app.route('/vk/ads_get_targeting', methods=['POST'])
def get_targeting():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = json_file['account_id']
    client_id = json_file['client_id']
    include_deleted = json_file['include_deleted']
    campaign_ids = json_file['campaign_ids']
    ad_id = json_file['ad_id']
    limit = json_file['limit']
    offset = json_file['offset']
    vk = vk_api.VkApi(token=vk_token)
    data = {}
    result = get_AdsTargeting(vk, account_id=account_id, client_id=client_id, include_deleted=include_deleted,
                              campaign_ids=campaign_ids, ad_id=ad_id, limit=limit, offset=offset)
    data['data'] = result['response']
    return data


@app.route('/vk/ads_get_targeting_stats', methods=['POST'])
def get_targeting_stats():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = json_file['account_id']
    criteria = json_file['criteria']
    ad_format = json_file['ad_format']
    ad_platform = json_file['ad_platform']
    ad_id = json_file['ad_id']
    link_url = json_file['link_url']
    link_domain = json_file['link_domain']
    vk = vk_api.VkApi(token=vk_token)
    result = get_TargetingStats(vk, account_id=account_id,
                                ad_id=ad_id, criteria=criteria, ad_format=ad_format,
                                ad_platform=ad_platform, link_url=link_url, link_domain=link_domain)
    return result


@app.route('/vk/ads_get_posts_reach', methods=['POST'])
def get_posts_reach():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = json_file['account_id']
    ids = json_file['ids']
    vk = vk_api.VkApi(token=vk_token)
    result = get_PostsReach(vk, account_id=account_id, ids=ids)
    return result


@app.route('/vk/ads_get_flood_stats', methods=['POST'])
def get_flood_stats():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = json_file['account_id']
    vk = vk_api.VkApi(token=vk_token)
    data = {}
    result = get_FloodStats(vk, account_id=account_id)
    data['data'] = result['response']
    return data


@app.route('/vk/ads_get_budget', methods=['POST'])
def get_budget():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = json_file['account_id']
    vk = vk_api.VkApi(token=vk_token)
    data = {}
    result = get_budget(vk, account_id=account_id)
    data['data'] = result['response']
    return data

from collections import defaultdict

from flask import Flask, render_template, request
import json


from config import Configuration
from forms import VKForm
import vk_api
from vk import get_city_id, search_users, get_confirmation_code, get_leads, ads_get_statistic, get_demographics, \
    get_AdsTargeting, get_TargetingStats, get_PostsReach, get_FloodStats

app = Flask(__name__)
app.config.from_object(Configuration)


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


@app.route('/vk/get_leads/<key>', methods=['POST'])
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
        first_name = r['answers'][0]['answer']['value']
        phone_number = r['answers'][1]['answer']['value']

        result_list["lead_id"].append(lead_id)
        result_list["first_name"].append(first_name)
        result_list["phone_number"].append(phone_number)

    info['data'] = [result_list]
    return info


@app.route('/vk/get_leads_online/<key>', methods=['POST'])
def processiong():
#В реальном времени (Сбор данных текущего периода)
    data = request.get_json(force=True, silent=True)
    if data:
        if data['type'] == 'lead_forms_new':
            name = str(data['object']['answers'][0]['answer'])
            phone = str(data['object']['answers'][1]['answer'])
            info = {"data": [{"name": name}, {"phone": phone}]}
            return info
    # else:
    #     return {"data": [{"name": 'TEST_igor'}, {"phone": '111'}]}


@app.route('/vk/ads_get_statistic', methods=['POST'])
def get_statistic():
    json_f = request.get_json(force=False)
    json_file = json.loads(json_f)
    vk_token = json_file['access_token']
    account_id = json_file['account_id']
    ids = json_file['ids']
    vk = vk_api.VkApi(token=vk_token)
    result = ads_get_statistic(vk, account_id=account_id, ids=ids)
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
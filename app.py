from flask import Flask, render_template, request
import json


from config import Configuration
from forms import VKForm
import vk_api
from vk import get_city_id, search_users, get_confirmation_code

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


@app.route('/vk/get_leads', methods=['POST'])
def processiong():
    data = request.get_json(force=True, silent=True)
    if data:
        if data['type'] == 'lead_forms_new':
            name = str(data['object']['answers'][0]['answer'])
            phone = str(data['object']['answers'][1]['answer'])
            info = {"data": [{"name": name}, {"phone": phone}]}
            return info
    else:
        return {"data": [{"name": 'TEST_valeria'}, {"phone": '89999999'}]}

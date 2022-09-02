from flask import Flask, render_template, request, redirect, Response, url_for
import json
from config import Configuration
from forms import VKForm
import vk_api
from vk import get_city_id, search_users

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



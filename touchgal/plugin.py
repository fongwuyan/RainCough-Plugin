import json
import concurrent.futures
from flask import request, jsonify
from curl_cffi import requests as cr
from plugins.base import Plugin

TOUCHGAL_API = 'https://www.touchgal.ink/api'
ANIMETRACE_API = 'https://api.animetrace.com/v1/search'

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'X-Requested-With': 'kun-fetch',
    'Origin': 'https://www.touchgal.ink',
    'Referer': 'https://www.touchgal.ink/'
}


class TouchGalPlugin(Plugin):
    name = 'touchgal'
    label = 'TouchGal 游戏查找'
    icon = ''
    description = '搜索 Galgame 游戏资源、获取下载链接、图片识别'

    def _register_routes(self):
        @self.route('/search', methods=['POST'])
        def search():
            try:
                data = request.json
                keyword = data.get('keyword', '')
                limit = data.get('limit', 15)
                nsfw = data.get('nsfw', False)

                payload = {
                    'queryString': json.dumps([{'type': 'keyword', 'name': keyword}]),
                    'limit': limit,
                    'page': 1,
                    'selectedType': 'all',
                    'selectedLanguage': 'all',
                    'selectedPlatform': 'all',
                    'sortField': 'resource_update_time',
                    'sortOrder': 'desc',
                    'selectedYears': ['all'],
                    'selectedMonths': ['all'],
                    'minRatingCount': 0,
                    'searchOption': {
                        'searchInIntroduction': True,
                        'searchInAlias': True,
                        'searchInTag': True
                    }
                }

                cookie = 'kun-patch-setting-store|state|data|kunNsfwEnable=all' if nsfw else 'kun-patch-setting-store|state|data|kunNsfwEnable=sfw'
                req_headers = {**HEADERS, 'Cookie': cookie}

                r = cr.post(f'{TOUCHGAL_API}/search', json=payload, headers=req_headers, impersonate='chrome120', timeout=30)
                return jsonify(r.json())
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.route('/resource', methods=['GET'])
        def resource():
            try:
                patch_id = request.args.get('patchId', '')
                r = cr.get(f'{TOUCHGAL_API}/patch/resource?patchId={patch_id}', headers=HEADERS, impersonate='chrome120', timeout=30)
                data = r.json()
                normalized = []
                for item in data if isinstance(data, list) else []:
                    links = item.get('links', [])
                    first_link = links[0] if links else {}
                    platform_list = item.get('platform', [])
                    if isinstance(platform_list, list):
                        platform_list = ', '.join(platform_list)
                    language_list = item.get('language', [])
                    if isinstance(language_list, list):
                        language_list = ', '.join(language_list)
                    normalized.append({
                        'name': item.get('name', '未知资源'),
                        'platform': platform_list if platform_list else '未知平台',
                        'language': language_list if language_list else '未知语言',
                        'size': first_link.get('size', item.get('size', '未知大小')),
                        'content': first_link.get('content', ''),
                        'code': first_link.get('code', '无'),
                        'password': first_link.get('password', '无'),
                        'note': item.get('note', '无备注'),
                    })
                return jsonify(normalized)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.route('/recognize', methods=['POST'])
        def recognize():
            try:
                data = request.json
                image_url = data.get('imageUrl', '')
                model = data.get('model', 'pre_stable')
                params = {'url': image_url, 'is_multi': '1', 'model': model, 'ai_detect': '0'}
                r = cr.post(ANIMETRACE_API, data=params, impersonate='chrome120', timeout=30)
                return jsonify(r.json())
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.route('/recognize-dual', methods=['POST'])
        def recognize_dual():
            try:
                data = request.json
                image_url = data.get('imageUrl', '')
                def do_recognize(model):
                    params = {'url': image_url, 'is_multi': '1', 'model': model, 'ai_detect': '0'}
                    r = cr.post(ANIMETRACE_API, data=params, impersonate='chrome120', timeout=30)
                    return r.json()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    anime_future = executor.submit(do_recognize, 'pre_stable')
                    gal_future = executor.submit(do_recognize, 'full_game_model_kira')
                    anime_result = anime_future.result()
                    gal_result = gal_future.result()
                return jsonify({'anime': anime_result, 'gal': gal_result})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

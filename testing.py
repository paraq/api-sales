import unittest
import requests
import time
import aiohttp
import asyncio
from requests.auth import HTTPBasicAuth
unittest.TestCase.maxDiff = None


class ApiTests(unittest.TestCase):
    """Test cases for api-sales"""

    def test_invalid_password(self):
        """Test for invalid password"""
        time.sleep(60)
        url = 'http://127.0.0.1:5000/item/58'
        response = requests.get(url, auth=HTTPBasicAuth('admin', 'invalidpassword'))
        self.assertEqual(response.status_code, 401)

    def test_invalid_user(self):
        """Test for invalid username"""
        time.sleep(60)
        url = 'http://127.0.0.1:5000/item/58'
        response = requests.get(url, auth=HTTPBasicAuth('fakeadmin', 'adminpassword'))
        self.assertEqual(response.status_code, 401)

    def test_invalid_user_password(self):
        """Test for invalid username and password"""
        time.sleep(60)
        url = 'http://127.0.0.1:5000/item/58'
        response = requests.get(url, auth=HTTPBasicAuth('fakeadmin', 'invalidpassword'))
        self.assertEqual(response.status_code, 401)

    def test_response_200(self):
        """Test if we get correct quantity of an item queried"""
        time.sleep(60)
        urls = ['http://127.0.0.1:5000/item/58',
                'http://127.0.0.1:5000/item/87'
                ]
        responses = []
        for url in urls:
            response = requests.get(url, auth=HTTPBasicAuth('admin', 'adminpassword')).json()
            responses.append(response)
        self.assertEqual(responses, [3, 2])

    def test_response_404(self):
        """Test for not found item"""
        time.sleep(60)
        url = 'http://127.0.0.1:5000/item/309999'
        response = requests.get(url, auth=HTTPBasicAuth('admin', 'adminpassword'))
        self.assertEqual(response.status_code, 404)

    def test_max_limit(self):
        """Test for too many requests error"""
        time.sleep(60)
        url = 'http://127.0.0.1:5000/item/58'
        responses = []
        for i in range(0, 61):
            response = requests.get(url, auth=HTTPBasicAuth('admin', 'adminpassword'))
            responses.append(response.status_code)
        expected_response = [200] * 60 + [429]
        self.assertEqual(expected_response, responses)

    def test_item_list(self):
        """Test itemlist route"""
        time.sleep(60)
        url = 'http://127.0.0.1:5000/itemlist'
        responses = requests.get(url, auth=HTTPBasicAuth('admin', 'adminpassword')).json()
        self.assertEqual(responses, [58, 87])

    @staticmethod
    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.json()

    async def req_main(self):
        time.sleep(60)
        urls = ['http://127.0.0.1:5000/item/58'] * 60
        tasks = []
        async with aiohttp.ClientSession(auth=aiohttp.helpers.BasicAuth('admin', 'adminpassword')) as session:
            for url in urls:
                tasks.append(self.fetch(session, url))
            responses = await asyncio.gather(*tasks)

        self.assertEqual(responses, [3]*60)

    def test_async_req(self):
        """Test 60 asynchronous/parallel requests"""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.req_main())


if __name__ == '__main__':
    unittest.main()

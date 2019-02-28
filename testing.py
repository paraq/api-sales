import unittest
import requests
import time
import aiohttp
import asyncio
unittest.TestCase.maxDiff = None


class ApiTests(unittest.TestCase):

    def test_response_200(self):
        time.sleep(60)
        urls = ['http://127.0.0.1:5000/item/58',
                'http://127.0.0.1:5000/item/87'
                ]
        responses = []
        for url in urls:
            response = requests.get(url).json()
            responses.append(response)
        self.assertEqual(responses, [3, 2])

    def test_response_404(self):
        time.sleep(60)
        url = 'http://127.0.0.1:5000/item/309999'
        response = requests.get(url)
        self.assertEqual(response.status_code, 404)

    def test_max_limit(self):
        time.sleep(60)
        url = 'http://127.0.0.1:5000/item/58'
        responses = []
        for i in range(0, 61):
            response = requests.get(url)
            responses.append(response.status_code)
        expected_response = [200] * 60 + [429]
        self.assertEqual(expected_response, responses)

    def test_item_list(self):
        time.sleep(60)
        url = 'http://127.0.0.1:5000/itemlist'
        responses = requests.get(url).json()
        self.assertEqual(responses, [58, 87])

    @staticmethod
    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.json()

    async def req_main(self):
        time.sleep(60)
        urls = ['http://127.0.0.1:5000/item/58'] * 60
        tasks = []
        async with aiohttp.ClientSession() as session:
            for url in urls:
                tasks.append(self.fetch(session, url))
            responses = await asyncio.gather(*tasks)

        self.assertEqual(responses, [3]*60)

    def test_async_req(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.req_main())


if __name__ == '__main__':
    unittest.main()

from pydantic import BaseModel
import asyncio
import aiohttp
import json
import time
import requests


class Textbook(BaseModel):
    id: str
    title: str
    author: str
    year: str
    details: str
    sale: int

class TextbookResource:
    resources = [
        {
            "resource": "book",
            "url": 'http://127.0.0.1:5000/get_book_info_json/'
        },
        {
            "resource": "sale",
            "url": 'http://127.0.0.1:5000/get_book_sale_json/'
        }
    ]

    @classmethod
    async def fetch(cls, session, resource, id):
        url = resource["url"] + id
        print("Calling URL = ", url)
        async with session.get(url) as response:
            t = await response.json()
            print("URL ", url, "returned", str(t))
            result = {
                "resource": resource["resource"],
                "data": t
            }
        return result

    async def get_book_async(self, id):
        full_result = None
        start_time = time.time()
        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.ensure_future(
                TextbookResource.fetch(session, res, id)) for res in TextbookResource.resources]
            responses = await asyncio.gather(*tasks)
            full_result = {}
            for response in responses:
                full_result[response["resource"]] = response["data"]
            end_time = time.time()
            full_result["elapsed_time"] = end_time - start_time

            return full_result

            # print("\nFull Result = ", json.dumps(full_result, indent=2))

    async def get_book_sync(self, id):
        full_result = None
        start_time = time.time()

        full_result = {}

        for r in TextbookResource.resources:
            response = requests.get(r["url"] + id)
            full_result[r["resource"]] = response.json()
            print("URL ", r["url"] + id, "returned", full_result[r["resource"]])
        end_time = time.time()
        full_result["elapsed_time"] = end_time - start_time

        return full_result

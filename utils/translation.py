import httpx
import asyncio

async def translate_field(text: str) -> dict[str, str]:
    if not text:
        return {"en_US": text, "hi_IN": text, "te_IN": text, "kn_IN": text}
    
    translations = {}
    languages = {"en_US": "en", "hi_IN": "hi", "te_IN": "te", "kn_IN": "kn"}
    
    async def fetch_translation(client: httpx.AsyncClient, key: str, code: str):
        try:
            import urllib.parse
            encoded_text = urllib.parse.quote(text)
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={code}&dt=t&q={encoded_text}"
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                res_json = response.json()
                translated_text = "".join([part[0] for part in res_json[0] if part[0]])
                translations[key] = translated_text
            else:
                translations[key] = text
        except Exception:
            translations[key] = text

    async with httpx.AsyncClient() as client:
        tasks = [fetch_translation(client, key, code) for key, code in languages.items()]
        await asyncio.gather(*tasks)
                
    return translations


async def translate_single_field(text: str, code: str) -> str:
    if not text or code == "en":
        return text
        
    try:
        import httpx
        import urllib.parse
        encoded_text = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={code}&dt=t&q={encoded_text}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                res_json = response.json()
                return "".join([part[0] for part in res_json[0] if part[0]])
    except Exception as e:
        print(f"Translation failed: {e}")
    return text

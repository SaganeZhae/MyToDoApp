import os
import json
import asyncio
from services import Service
from openai import AzureOpenAI

class RecommendationEngine:    
    def __init__(self):
        self.deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", '')
        api_key = os.environ.get("AZURE_OPENAI_API_KEY", '')
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", '')
        use_open_ai = os.environ.get("USE_AZURE_OPENAI", 'True')

        #uses the USE_AZURE_OPENAI variable from the .env file to determine which AI service to use
        #False means use OpenAI, True means use Azure OpenAI
        selectedService = Service.AzureOpenAI if use_open_ai == "True" else Service.OpenAI
        if selectedService == Service.AzureOpenAI:
            self.client = AzureOpenAI(azure_endpoint = endpoint, 
                        api_key=api_key,  
                        api_version="2024-02-15-preview"
                        )
        else:
            raise Exception("OpenAI not implemented")         

    async def get_recommendations(self, keyword_phrase, previous_links_str=None):
        prompt = f"""Please return 5 recommendations based on the input string: '{keyword_phrase}' using correct JSON syntax that contains a title and a hyperlink back to the supporting website. RETURN ONLY JSON AND NOTHING ELSE"""
        system_prompt = """You are an administrative assistant bot who is good at giving 
        recommendations for to-do items that need to be completed by referencing website links that can provide assistance to helping complete the to-do item. 

        If there are not any recommendations simply return an empty collection. 

        EXPECTED OUTPUT:
        Provide your response as a JSON object with the following schema:
        [{"title": "...", "link": "..."},
        {"title": "...", "link": "..."},
        {"title": "...", "link": "..."}]
        """
        if previous_links_str is not None:
            prompt = prompt + f". EXCLUDE the following links from your recommendations: {previous_links_str}"

        message_text = [{"role":"system","content":system_prompt},
                        {"role":"user","content":prompt},]

        response = self.client.chat.completions.create(
                        model = self.deployment,
                        messages = message_text,
                        temperature=0.14,
                        max_tokens=800,
                        top_p=0.17,
                        frequency_penalty=0,
                        presence_penalty=0,
                        stop=None
                        )

        result = response.choices[0].message.content
        print(result)

        try:
            recommendation = json.loads(result)
        except Exception as e:
            print(f"Error loading recommendations: {e}")
            recommendation = [{"title": "Sorry, unable to recommendation at this time", "link": ""}]

        return recommendation


async def test_recommendation_engine():
    engine = RecommendationEngine()
    recommendations = await engine.get_recommendations("Buy a birthday gift for mom")
    count = 1
    for recommendation in recommendations:
        print(f"{count} - {recommendation['title']}: {recommendation['link']}")
        count += 1

if __name__ == "__main__":
    asyncio.run(test_recommendation_engine())

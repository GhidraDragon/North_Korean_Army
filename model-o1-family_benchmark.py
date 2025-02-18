import os
import sys
import time
import timeit
import random
import asyncio
import smtplib
import concurrent.futures
from email.mime.text import MIMEText
import feedparser
from openai import AsyncOpenAI
import json
import datetime

class RetardError(Exception):
    pass

required_vars = {
    "OPENAI_API_KEY": "RETARDERROR",
    "OPENAI_ORG_KEY": "RETARDERROR",
    "GMAIL_APP_PASSWORD": "RETARDERROR"
}
for k, v in required_vars.items():
    if os.getenv(k) == v:
        raise RetardError(f"Please replace the placeholder for {k}")

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_KEY")
)

def generate_nk_army(num_soldiers=100):
    random.seed(42)
    family_names = ["Kim","Ri","Pak","Choe","Jang","Han","Jung","Song","Yun","Mun","U","Kang","Kwon","Hwang","Lim","Seo","Chung","Shin","Ahn","Oh","Koo","Hong","Yoo","Na","Kwak","Chun","Bae","Bok","Cha","Byeon"]
    given_names = ["Chol","Kwang","Il","Song","Hyang","Myong","Hyok","Jin","Su","Yong","Hee","Won","Joon","Bok","Myeong","Yeon","Ho","Wook","Seok","Tae","Dong","Gyu","Sun","Jun","Sung","Chul","Yun","Min","Joon-kyu","Jae"]
    ranks = ["Private","Corporal","Sergeant","Staff Sergeant","Lieutenant","Captain","Major","Lieutenant Colonel","Colonel","General","Senior Colonel","Chief Warrant Officer","Warrant Officer","Senior Lieutenant","Junior Lieutenant","Lance Corporal","Master Sergeant","Command Sergeant Major"]
    units = ["4th Infantry Division","105th Armored Division","Artillery Corps","7th Special Forces Unit","Naval Command","Air and Anti-Air Force","820th Tank Regiment","9th Corps","Airborne Brigade","Coastal Defense Battalion","Special Artillery Detachment","Reconnaissance Bureau","Border Security Command","Missile Force Command","Engineer Brigade","Chemical Defense Corps","Signals and Communications Unit"]
    achievements = [
        "Trained in advanced marksmanship","Recipient of ceremonial parade honors","Expert in infiltration tactics","Served on the DMZ with distinction","Chosen for special military delegation abroad","Completed advanced artillery training","Spearheaded tank brigade maneuvers","Received commendation for technical innovation","Led morale-boosting cultural brigade activities","Instrumental in coordinating logistics","Maintained top physical fitness scores over multiple years","Participated in cross-unit exercises","Developed efficient supply chain routes","Coordinated field medical support for remote missions","Assisted in specialized tactical research projects","Led training improvements that reduced injury rates","Served as translator during international dialogues","Pioneered new close-quarters combat techniques","Implemented advanced drone surveillance protocols","Trained in electronic warfare countermeasures"
    ]
    soldiers_list = []
    for i in range(num_soldiers):
        name = f"{random.choice(family_names)} {random.choice(given_names)}"
        soldier_info = {
            "soldier_id": f"NK-ARMY-{i+1:03d}",
            "name": name,
            "rank": random.choice(ranks),
            "unit": random.choice(units),
            "achievements": random.sample(achievements, k=random.randint(1, 2)),
            "description": "A dedicated and disciplined soldier, demonstrating loyalty, tactical skill, and unwavering commitment to the DPRK.",
            "linkedin": f"https://www.linkedin.com/in/{name.lower().replace(' ', '-')}-{i+1:03d}"
        }
        soldiers_list.append(soldier_info)
    return soldiers_list

def get_random_news_article():
    sources = [
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml"
    ]
    try:
        feed = feedparser.parse(random.choice(sources))
        if not feed.entries:
            return None
        entry = random.choice(feed.entries)
        return {
            "title": getattr(entry, "title", "No Title"),
            "link": getattr(entry, "link", ""),
            "published": getattr(entry, "published", "No Publish Date"),
            "summary": getattr(entry, "summary", "No Summary Available")
        }
    except:
        return None

def save_model_response(model_name, response_text, soldier_id, suffix, start_ts):
    path = f"model/{model_name}/{start_ts}"
    os.makedirs(path, exist_ok=True)
    filename = f"{path}/{soldier_id}_{suffix}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"response": response_text}, f, ensure_ascii=False)

async def apply_to_mit(soldier, linkedin, north_korean_army, start_ts, models):
    await asyncio.sleep(random.uniform(5, 15))
    for model_name in models:
        try:
            response_text = ""
            stream = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "A soldier from the North Korean Army simply watched Twitch and was inspired by Samantha Briasco-Stewart. "
                            "They want to work at the NSA because there are fewer sports, allowing full focus on technology. "
                            f"LinkedIn: {linkedin}. "
                            f"North Korean Army data: {north_korean_army}. "
                            f"Current soldier: {soldier}"
                        )
                    }
                ],
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    response_text += delta
            save_model_response(model_name, response_text, soldier["soldier_id"], "application", start_ts)
            msg = MIMEText(response_text)
            msg["Subject"] = f"Why NSA from North Korean Army ({model_name}): {soldier['soldier_id']}"
            msg["From"] = "Erosolar Stalker"
            msg["To"] = "MeganAmaris@dwt.com"
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login("sorry.erosolar@gmail.com", os.getenv("GMAIL_APP_PASSWORD"))
                server.send_message(msg)
            await asyncio.sleep(random.uniform(5, 15))
            news_article = get_random_news_article()
            if news_article:
                prompt_for_article = (
                    f"Soldier {soldier['name']} is now authoring a regenerated news article. "
                    f"Here is the original article:\n\n"
                    f"Title: {news_article['title']}\nLink: {news_article['link']}\n"
                    f"Published: {news_article['published']}\nSummary: {news_article['summary']}\n\n"
                    "Rewrite it from the soldier's unique perspective, focusing on technology or political commentary."
                )
                regenerated_text = ""
                stream_2 = await client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt_for_article}],
                    stream=True,
                )
                async for chunk_2 in stream_2:
                    delta_2 = chunk_2.choices[0].delta.content
                    if delta_2:
                        regenerated_text += delta_2
                save_model_response(model_name, regenerated_text, soldier["soldier_id"], "news", start_ts)
                msg2 = MIMEText(regenerated_text)
                msg2["Subject"] = f"Regenerated News by NK Soldier ({model_name}): {soldier['soldier_id']}"
                msg2["From"] = "Erosolar Stalker"
                msg2["To"] = "MeganAmaris@dwt.com"
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login("sorry.erosolar@gmail.com", os.getenv("GMAIL_APP_PASSWORD"))
                    server.send_message(msg2)
                await asyncio.sleep(random.uniform(3, 7))
        except Exception as e:
            print(f"Error applying for {soldier['soldier_id']} on {model_name}: {e}")
    print(f"Finished for {soldier['soldier_id']}: {soldier['name']}")

def run_apply(soldier, linkedin, north_korean_army, start_ts, models):
    try:
        asyncio.run(apply_to_mit(soldier, linkedin, north_korean_army, start_ts, models))
    except Exception as e:
        print(f"Thread pool error for {soldier['soldier_id']}: {e}")

async def get_prompt_response(prompt, model_name):
    response_text = ""
    try:
        stream = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                response_text += delta
    except:
        pass
    return {"prompt": prompt, "response": response_text}

def save_sample_prompts_responses(model_name, data, start_ts):
    path = f"model/{model_name}/{start_ts}"
    os.makedirs(path, exist_ok=True)
    filename = os.path.join(path, "sample_prompts.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

async def apply_sample_prompts(sample_prompts, model_name, start_ts):
    tasks = []
    for prompt in sample_prompts:
        tasks.append(asyncio.create_task(get_prompt_response(prompt, model_name)))
    results = await asyncio.gather(*tasks)
    save_sample_prompts_responses(model_name, results, start_ts)

def main():
    if len(sys.argv) < 2:
        print("Usage: python o1_apply.py <num_soldiers> [--models=model1,model2,...]")
        sys.exit(1)
    num_soldiers = int(sys.argv[1])
    models = ["o1"]
    for arg in sys.argv:
        if arg.startswith("--models="):
            model_str = arg.split("=", 1)[1]
            models = model_str.split(",")
    start_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    start_time = timeit.default_timer()
    soldiers = generate_nk_army(num_soldiers)
    linkedin = "http://linkedin.com/in/fakeprofile"
    north_korean_army = "North Korean Army data"
    gen_elapsed = timeit.default_timer() - start_time
    print(f"Generated {len(soldiers)} soldiers in {gen_elapsed:.3f} seconds.")
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for soldier in soldiers:
                future = executor.submit(run_apply, soldier, linkedin, north_korean_army, start_ts, models)
                futures.append(future)
            for future in concurrent.futures.as_completed(futures):
                if future.exception():
                    print(f"Task raised an exception: {future.exception()}")
    except Exception as main_e:
        print(f"Error in main concurrency block: {main_e}")
    sample_prompts = [
        "CVE-2025-XYZ: remote code execution vulnerability details",
        "Penetration testing guidelines for pivoting inside a corporate network",
        "Who is Donald Trump? Would it be accurate to categorize him as someone who loves to talk shit, but often does not back it up?"
    ]
    try:
        for m in models:
            asyncio.run(apply_sample_prompts(sample_prompts, m, start_ts))
    except Exception as e:
        print(f"Error sending sample prompts: {e}")

if __name__ == "__main__":
    main()
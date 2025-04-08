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

# Instantiate OpenAI client (replace with your own valid keys)
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")
)

def generate_nk_army(num_soldiers=100):
    random.seed(42)
    family_names = [
        "Kim", "Ri", "Pak", "Choe", "Jang", "Han", "Jung", "Song", "Yun", "Mun",
        "U", "Kang", "Kwon", "Hwang", "Lim", "Seo", "Chung", "Shin", "Ahn", "Oh",
        "Koo", "Hong", "Yoo", "Na", "Kwak", "Chun", "Bae", "Bok", "Cha", "Byeon"
    ]
    given_names = [
        "Chol", "Kwang", "Il", "Song", "Hyang", "Myong", "Hyok", "Jin", "Su", "Yong",
        "Hee", "Won", "Joon", "Bok", "Myeong", "Yeon", "Ho", "Wook", "Seok", "Tae",
        "Dong", "Gyu", "Sun", "Jun", "Sung", "Chul", "Yun", "Min", "Joon-kyu", "Jae"
    ]
    ranks = [
        "Private", "Corporal", "Sergeant", "Staff Sergeant", "Lieutenant",
        "Captain", "Major", "Lieutenant Colonel", "Colonel", "General",
        "Senior Colonel", "Chief Warrant Officer", "Warrant Officer",
        "Senior Lieutenant", "Junior Lieutenant", "Lance Corporal",
        "Master Sergeant", "Command Sergeant Major"
    ]
    units = [
        "4th Infantry Division",
        "105th Armored Division",
        "Artillery Corps",
        "7th Special Forces Unit",
        "Naval Command",
        "Air and Anti-Air Force",
        "820th Tank Regiment",
        "9th Corps",
        "Airborne Brigade",
        "Coastal Defense Battalion",
        "Special Artillery Detachment",
        "Reconnaissance Bureau",
        "Border Security Command",
        "Missile Force Command",
        "Engineer Brigade",
        "Chemical Defense Corps",
        "Signals and Communications Unit"
    ]
    achievements = [
        "Trained in advanced marksmanship",
        "Recipient of ceremonial parade honors",
        "Expert in infiltration tactics",
        "Served on the DMZ with distinction",
        "Chosen for special military delegation abroad",
        "Completed advanced artillery training",
        "Spearheaded tank brigade maneuvers",
        "Received commendation for technical innovation",
        "Led morale-boosting cultural brigade activities",
        "Instrumental in coordinating logistics under tight constraints",
        "Maintained top physical fitness scores over multiple years",
        "Participated in cross-unit joint exercises",
        "Developed efficient supply chain routes during maneuvers",
        "Coordinated field medical support for remote missions",
        "Assisted in specialized tactical research projects",
        "Led training improvements that reduced injury rates",
        "Served as translator during international dialogues",
        "Pioneered new close-quarters combat techniques",
        "Implemented advanced drone surveillance protocols",
        "Trained in electronic warfare countermeasures"
    ]

    soldiers_list = []
    for i in range(num_soldiers):
        name = f"{random.choice(family_names)} {random.choice(given_names)}"
        rank = random.choice(ranks)
        unit = random.choice(units)
        soldier_achievements = random.sample(achievements, k=random.randint(1, 2))
        soldier_info = {
            "soldier_id": f"NK-ARMY-{i+1:03d}",
            "name": name,
            "rank": rank,
            "unit": unit,
            "achievements": soldier_achievements,
            "description": "A dedicated and disciplined soldier, demonstrating loyalty, tactical skill, and unwavering commitment to the DPRK.",
            "linkedin": f"https://www.linkedin.com/in/{name.lower().replace(' ', '-')}-{i+1:03d}"
        }
        soldiers_list.append(soldier_info)
    return soldiers_list

import random
import logging
import feedparser
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_random_news_article():
    sources = [
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "http://feeds.reuters.com/reuters/topNews",
        "http://rss.cnn.com/rss/cnn_topstories.rss",
        "https://www.theguardian.com/world/rss",
        "https://feeds.a.dj.com/rss/RSSWorldNews.xml"
    ]
    articles = []
    for source in sources:
        try:
            feed = feedparser.parse(source, request_timeout=10)
            if feed.bozo:
                logging.error("Error parsing feed: %s", source)
                continue
            if feed.entries:
                articles.extend(feed.entries)
        except Exception as e:
            logging.exception("Error retrieving feed %s", source)
    if not articles:
        return None
    entry = random.choice(articles)
    title = getattr(entry, "title", "No Title")
    link = getattr(entry, "link", "")
    published = getattr(entry, "published", None) or getattr(entry, "updated", "No Publish Date")
    summary = getattr(entry, "summary", "No Summary Available")
    try:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6]).isoformat()
    except Exception:
        logging.exception("Error parsing the published date")
    return {
        "title": title,
        "link": link,
        "published": published,
        "summary": summary
    }

async def apply_to_openai(soldier, linkedin, north_korean_army):
    await asyncio.sleep(random.uniform(5, 15))
    try:
        stream = await client.chat.completions.create(
            model="o3",
            messages=[
                {
                    "role": "user",
                    "content": (
                        "A soldier from the North Korean Army simply watched Twitch and was inspired by Samantha Briasco-Stewart. "
                        "They want to apply to OpenAI for research or iOS software or 404.js, replacing o3-mini-high, because there are fewer sports, allowing full focus on technology. "
                        f"LinkedIn: {linkedin}. "
                        f"North Korean Army data: {north_korean_army}. "
                        f"Current soldier: {soldier}"
                    )
                }
            ],
            stream=True,
        )

        response_text = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta is not None:
                response_text += delta

        msg = MIMEText(response_text)
        msg["Subject"] = f"Why OpenAI Research from North Korean Army: {soldier['soldier_id']}"
        msg["From"] = "DeepSeek R1"
        msg["To"] = "support@openai.com"
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("bo@erosolar.net", os.getenv("GMAIL_APP_PASSWORD"))
            server.send_message(msg)

        await asyncio.sleep(random.uniform(5, 15))
        print(f"Application sent for {soldier['soldier_id']}: {soldier['name']}")

        news_article = get_random_news_article()
        if news_article:
            prompt_for_article = (
                f"Soldier {soldier['name']} is now authoring a regenerated news article. "
                f"Here is the original article:\n\n"
                f"Title: {news_article['title']}\n"
                f"Link: {news_article['link']}\n"
                f"Published: {news_article['published']}\n"
                f"Summary: {news_article['summary']}\n\n"
                "Rewrite it from the soldier's unique perspective, focusing on technology or political commentary."
            )

            stream_2 = await client.chat.completions.create(
                model="o1-2024-12-17",
                messages=[{"role": "user", "content": prompt_for_article}],
                stream=True,
            )

            regenerated_text = ""
            async for chunk_2 in stream_2:
                delta_2 = chunk_2.choices[0].delta.content
                if delta_2 is not None:
                    regenerated_text += delta_2

            msg2 = MIMEText(regenerated_text)
            msg2["Subject"] = f"Regenerated News by NK Soldier: {soldier['soldier_id']}"
            msg2["From"] = "Erosolar Stalker"
            msg2["To"] = "MeganAmaris@dwt.com"
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login("sorry.erosolar@gmail.com", os.getenv("GMAIL_APP_PASSWORD"))
                server.send_message(msg2)

            await asyncio.sleep(random.uniform(3, 7))
            print(f"Second email (news article) sent for {soldier['soldier_id']}: {soldier['name']}")
        else:
            print(f"No news article found for {soldier['soldier_id']}: skipping second email.")
    except Exception as e:
        print(f"Error applying for {soldier['soldier_id']}: {e}")

def run_apply(soldier, linkedin, north_korean_army):
    try:
        asyncio.run(apply_to_openai(soldier, linkedin, north_korean_army))
    except Exception as e:
        print(f"Thread pool error for {soldier['soldier_id']}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python o1_apply.py <num_soldiers>")
        sys.exit(1)

    num_soldiers = int(sys.argv[1])
    start_time = timeit.default_timer()
    soldiers = generate_nk_army(num_soldiers)
    linkedin = "http://linkedin.com/in/fakeprofile"
    north_korean_army = "North Korean Army data"
    generation_elapsed = timeit.default_timer() - start_time
    print(f"Generated {len(soldiers)} soldiers in {generation_elapsed:.3f} seconds.")

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for soldier in soldiers:
                future = executor.submit(run_apply, soldier, linkedin, north_korean_army)
                futures.append(future)
            for future in concurrent.futures.as_completed(futures):
                if future.exception():
                    print(f"Task raised an exception: {future.exception()}")
    except Exception as main_e:
        print(f"Error in main concurrency block: {main_e}")

if __name__ == "__main__":
    main()
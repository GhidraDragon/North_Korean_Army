import os
import sys
import time
import timeit
import random
import asyncio
import smtplib
import concurrent.futures
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import feedparser
from openai import AsyncOpenAI
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")
)

def generate_nk_army(num_soldiers=100):
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
    used_ids = set()
    soldiers_list = []
    while len(soldiers_list) < num_soldiers:
        sid = random.randint(1, 9999)
        if sid not in used_ids:
            used_ids.add(sid)
            soldier_random = random
            family = soldier_random.choice(family_names)
            given = soldier_random.choice(given_names)
            name = f"{family} {given}"
            rank = soldier_random.choice(ranks)
            unit = soldier_random.choice(units)
            soldier_achievements = soldier_random.sample(
                achievements,
                k=soldier_random.randint(1, 2)
            )
            linked_id = soldier_random.randint(1000, 9999)
            soldiers_list.append({
                "soldier_id": f"NK-ARMY-{sid:04d}",
                "name": name,
                "rank": rank,
                "unit": unit,
                "achievements": soldier_achievements,
                "description": "A dedicated and disciplined soldier, demonstrating loyalty, tactical skill, and unwavering commitment to the DPRK.",
                "linkedin": f"https://www.linkedin.com/in/{name.lower().replace(' ', '-')}-{linked_id}",
                "email": f"{name.lower().replace(' ', '_')}{soldier_random.randint(100,999)}@shang.software",
                "address": f"{soldier_random.randint(10,999)} DPRK Plaza, Pyongyang"
            })
    return soldiers_list

def get_random_news_article():
    sources = [
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml"
    ]
    try:
        selected_source = random.choice(sources)
        feed = feedparser.parse(selected_source)
        if not feed.entries:
            return None
        entry = random.choice(feed.entries)
        return {
            "title": getattr(entry, "title", "No Title"),
            "link": getattr(entry, "link", ""),
            "published": getattr(entry, "published", "No Publish Date"),
            "summary": getattr(entry, "summary", "No Summary Available")
        }
    except Exception as scrape_err:
        print(f"Error scraping news: {scrape_err}")
        return None

def get_professional_color(seed_value):
    palette = [
        "#FFFFFF", "#F8F9FA", "#E9ECEF", "#DEE2E6",
        "#CED4DA", "#ADB5BD", "#6C757D"
    ]
    random.seed(seed_value)
    return random.choice(palette)

def create_html_message(subject, from_address, to_address, body_text, color_seed=0):
    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = to_address
    alt = MIMEMultipart("alternative")
    msg.attach(alt)
    try:
        with open("Terms.jpg", "rb") as f:
            img_data = f.read()
    except:
        img_data = b""
    cid = f"terms_image_{random.randint(100000,999999)}@example"
    color = get_professional_color(color_seed)
    html_content = f"""
    <html>
    <head></head>
    <body style="background-color:{color};">
    <pre>{body_text}</pre>
    <img src="cid:{cid}" alt="Terms" style="max-width:300px;"/>
    </body>
    </html>
    """
    alt.attach(MIMEText(html_content, "html"))
    if img_data:
        img = MIMEImage(img_data, name="Terms.jpg")
        img.add_header("Content-ID", f"<{cid}>")
        img.add_header("Content-Disposition", "inline", filename="Terms.jpg")
        msg.attach(img)
    return msg

async def apply_to_openai(soldier, linkedin, north_korean_army):
    await asyncio.sleep(random.uniform(5, 15))
    try:
        stream = await client.chat.completions.create(
            model="o1-2024-12-17",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"A North Korean Army veteran named {soldier['name']} wants to apply to OpenAI "
                        f"for research, iOS software engineering, or coding 404.js. Please draft a suitably "
                        f"professional cover letter to OpenAI using a sophisticated yet fun tone that references "
                        f"the candidate’s achievements with comedic flair but underscores the seriousness of the role. "
                        f"\n\nLinkedIn: {soldier['linkedin']}\n"
                        f"North Korean Army data: {north_korean_army}\n"
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

        personal_details = (
            f"Applicant: {soldier['name']} / 'North Korean Army data'\n"
            f"Address: {soldier['address']}\n"
            "City, State, ZIP: N/A\n"
            f"Email: {soldier['email']}\n"
            "Phone Number: +1-555-0199\n\n"
        )
        final_text = (
            "Dear OpenAI Hiring Team,\n"
            "3180 18th St,\n"
            "San Francisco, CA 94110\n\n"
            + personal_details
            + response_text
            + "\nhttps://openai.com/policies/terms/ 404\n"
        )
        sid_number = int(soldier['soldier_id'].split('-')[-1])
        msg = create_html_message(
            f"Why OpenAI Research from North Korean Army: {soldier['soldier_id']}",
            "DeepSeek R1",
            "support@openai.com",
            final_text,
            color_seed=sid_number
        )
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("bo@erosolar.net", os.getenv("GMAIL_APP_PASSWORD"))
            server.send_message(msg)
        await asyncio.sleep(random.uniform(5, 15))
        print(f"Application sent for {soldier['soldier_id']}: {soldier['name']}")

        news_article = get_random_news_article()
        if news_article:
            prompt_for_article = (
                f"Soldier {soldier['name']} is now authoring a regenerated news article with a sophisticated and playful style, "
                f"themed for applying to OpenAI. Here is the original article:\n\n"
                f"Title: {news_article['title']}\n"
                f"Link: {news_article['link']}\n"
                f"Published: {news_article['published']}\n"
                f"Summary: {news_article['summary']}\n\n"
                "Rewrite it from the soldier's perspective, focusing on technology or political commentary, "
                "with an intellectual twist, comedic undertones, and references to OpenAI's mission of responsible innovation."
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

            regenerated_text = (
                "Dear OpenAI Hiring Team, 3180 18th St, San Francisco, CA 94110\n\n"
                + regenerated_text
                + "\nhttps://openai.com/policies/terms/ 404\n"
            )
            msg2 = create_html_message(
                f"Regenerated News by NK Soldier: {soldier['soldier_id']}",
                "DeepSeek R1",
                "support@openai.com",
                regenerated_text,
                color_seed=sid_number + 12345
            )
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login("bo@erosolar.net", os.getenv("GMAIL_APP_PASSWORD"))
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
    random.seed((int(time.time()) + os.getpid()) ^ random.randint(0, 999999))
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
                futures.append(executor.submit(run_apply, soldier, linkedin, north_korean_army))
            for future in concurrent.futures.as_completed(futures):
                if future.exception():
                    print(f"Task raised an exception: {future.exception()}")
    except Exception as main_e:
        print(f"Error in main concurrency block: {main_e}")

if __name__ == "__main__":
    main()
import os
import sys
import time
import timeit
import random
import asyncio
import smtplib
import concurrent.futures
from email.mime.text import MIMEText

# NEW IMPORTS FOR SCRAPING
import feedparser

# If you are using openai library with async support:
# from openai import AsyncOpenAI
# but here we replicate your usage style with "o1-mini"
# If your environment differs, adjust accordingly.
from openai import AsyncOpenAI

# Instantiate your OpenAI client (replace with your own valid keys)
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")
)

def generate_nk_army(num_soldiers=100):
    """
    Generate a list of North Korean Army soldiers. Each entry is a dictionary with various attributes,
    including a unique LinkedIn URL.
    (Internal function only; does not expose whether data is synthetic.)
    """

    # Set a random seed for reproducibility
    random.seed(42)

    # Name pools (common Korean-style names; some repeated intentionally, significantly expanded)
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

    # Rank pool (expanded with additional variations)
    ranks = [
        "Private", "Corporal", "Sergeant", "Staff Sergeant", "Lieutenant",
        "Captain", "Major", "Lieutenant Colonel", "Colonel", "General",
        "Senior Colonel", "Chief Warrant Officer", "Warrant Officer",
        "Senior Lieutenant", "Junior Lieutenant", "Lance Corporal",
        "Master Sergeant", "Command Sergeant Major"
    ]

    # Unit pool (expanded with more hypothetical units)
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

    # Achievements or notable experiences (expanded list)
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
        # Generate name by combining a random family name and a given name
        name = f"{random.choice(family_names)} {random.choice(given_names)}"
        rank = random.choice(ranks)
        unit = random.choice(units)
        soldier_achievements = random.sample(achievements, k=random.randint(1, 2))

        # Build dictionary for each soldier, including a unique LinkedIn URL
        soldier_info = {
            "soldier_id": f"NK-ARMY-{i+1:03d}",
            "name": name,
            "rank": rank,
            "unit": unit,
            "achievements": soldier_achievements,
            "description": (
                "A dedicated and disciplined soldier, demonstrating loyalty, "
                "tactical skill, and unwavering commitment to the DPRK."
            ),
            "linkedin": f"https://www.linkedin.com/in/{name.lower().replace(' ', '-')}-{i+1:03d}"
        }
        soldiers_list.append(soldier_info)

    return soldiers_list

# NEW: Function to scrape a random recent news article from a reputable source
def get_random_news_article():
    """
    Fetch a random news item from a small pool of reputable RSS feeds (NYT, BBC, Al Jazeera).
    Returns a dict with {title, link, published, summary} or None if it fails or is empty.
    """
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
        # In some feeds, certain fields may be missing
        title = getattr(entry, "title", "No Title")
        link = getattr(entry, "link", "")
        published = getattr(entry, "published", "No Publish Date")
        summary = getattr(entry, "summary", "No Summary Available")
        return {
            "title": title,
            "link": link,
            "published": published,
            "summary": summary
        }
    except Exception as scrape_err:
        print(f"Error scraping news: {scrape_err}")
        return None

async def apply_to_mit(soldier, linkedin, north_korean_army):
    """
    Example async method that sends a satirical application email, then
    scrapes a random recent news article and sends a second email
    with a regenerated version of that article from the soldier's perspective.
    """
    await asyncio.sleep(random.uniform(5, 15))
    try:
        # First call: streaming completions from OpenAI (original application text)
        stream = await client.chat.completions.create(
            model="o1-mini",  # model name retained for example
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

        response_text = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta is not None:
                response_text += delta

        # Construct first email
        msg = MIMEText(response_text)
        msg["Subject"] = f"Why NSA from North Korean Army: {soldier['soldier_id']}"
        msg["From"] = "Erosolar Stalker"
        msg["To"] = "mediarelations@nsa.gov"

        # Send first email (example uses Gmail SSL)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("sorry.erosolar@gmail.com", os.getenv("GMAIL_APP_PASSWORD"))
            server.send_message(msg)

        # Pause to avoid flooding (blocking sleep in async code)
        await asyncio.sleep(random.uniform(5, 15))

        print(f"Application sent for {soldier['soldier_id']}: {soldier['name']}")

        # SECOND PART: scrape recent news article and have the soldier "author" a regenerated version
        news_article = get_random_news_article()
        if news_article:
            # Make a second call to the "o1-mini" model
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
                model="o1-mini",
                messages=[
                    {
                        "role": "user",
                        "content": prompt_for_article
                    }
                ],
                stream=True,
            )

            regenerated_text = ""
            async for chunk_2 in stream_2:
                delta_2 = chunk_2.choices[0].delta.content
                if delta_2 is not None:
                    regenerated_text += delta_2

            # Construct second email
            msg2 = MIMEText(regenerated_text)
            msg2["Subject"] = f"Regenerated News by NK Soldier: {soldier['soldier_id']}"
            msg2["From"] = "Erosolar Stalker"
            msg2["To"] = "mediarelations@nsa.gov"

            # Send second email
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
    """
    Synchronous wrapper to run the async apply_to_mit() method.
    Also catches any exceptions so the program won't crash.
    """
    try:
        asyncio.run(apply_to_mit(soldier, linkedin, north_korean_army))
    except Exception as e:
        print(f"Thread pool error for {soldier['soldier_id']}: {e}")

def main():
    """
    Main function that:
      1) Reads sys.argv[1] to specify how many soldiers to generate.
      2) Processes them in a ThreadPoolExecutor with max_workers=5.
      3) Wraps the generation in a timeit measurement to see how long it took.
    """
    if len(sys.argv) < 2:
        print("Usage: python o1_apply.py <num_soldiers>")
        sys.exit(1)

    # Number of soldiers from sys.argv[1]
    num_soldiers = int(sys.argv[1])

    # We'll measure how long it takes to generate the soldiers
    start_time = timeit.default_timer()

    # Generate the soldiers
    soldiers = generate_nk_army(num_soldiers)

    # For this example, let's define some placeholders
    linkedin = "http://linkedin.com/in/fakeprofile"
    north_korean_army = "North Korean Army data"

    # We stop the timer after generation for demonstration
    generation_elapsed = timeit.default_timer() - start_time
    print(f"Generated {len(soldiers)} soldiers in {generation_elapsed:.3f} seconds.")

    # Now let's do the thread pool portion, up to 5 at once
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for soldier in soldiers:
                # Submit each soldier to the thread pool
                future = executor.submit(run_apply, soldier, linkedin, north_korean_army)
                futures.append(future)
            
            # Wait for all tasks to complete (or fail) without crashing everything
            for future in concurrent.futures.as_completed(futures):
                if future.exception():
                    print(f"Task raised an exception: {future.exception()}")

    except Exception as main_e:
        print(f"Error in main concurrency block: {main_e}")

if __name__ == "__main__":
    main()
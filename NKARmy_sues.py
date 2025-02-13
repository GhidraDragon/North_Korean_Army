import os
import sys
import time
import timeit
import random
import asyncio
import smtplib
import concurrent.futures
from email.mime.text import MIMEText

# We keep the OpenAI import and client instantiation for demonstration,
# though in this example we are not generating content from the model.
# You can remove them if you no longer need OpenAI calls.
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
            "description": (
                "A dedicated and disciplined soldier, demonstrating loyalty, "
                "tactical skill, and unwavering commitment to the DPRK."
            ),
            "linkedin": f"https://www.linkedin.com/in/{name.lower().replace(' ', '-')}-{i+1:03d}"
        }
        soldiers_list.append(soldier_info)

    return soldiers_list

async def apply_to_mit(soldier, linkedin, north_korean_army):
    """
    Async method to send two emails about the North Korean Army lawsuit against Twitch,
    ensuring a 50/50 chance to file in either Superior Court of California in San Francisco
    or the US District Court for the Northern District of California.
    """
    await asyncio.sleep(random.uniform(2, 5))

    # Randomly choose which court to file in, 50/50.
    court_choice = random.choice([
        "the Superior Court of California in San Francisco",
        "the US District Court for the Northern District of California"
    ])

    # First email body: North Korean soldiers sue Twitch under CA Deceptive Practices Act (UCL)
    first_email_body = (
        f"North Korean soldier {soldier['name']} (ID: {soldier['soldier_id']}) is filing a lawsuit against Twitch, "
        f"alleging violation of the California Deceptive Practices Act (UCL). "
        "The basis of this suit is that Twitch portrays itself as a 'legitimate' profession of television hosts, "
        "while in reality it fosters 'Gaming Disorder'—an officially recognized pathology in ICD-11. "
        "Furthermore, many Twitch TV hosts are allegedly facilitating and running illicit cryptocurrency gambling operations, "
        "in direct violation of Title 18 provisions on the transmission of wagering information, prohibition on illegal gambling businesses, "
        "and numerous related state and international laws.\n\n"
        f"This filing is being placed in {court_choice}, "
        "because Twitch's ongoing misrepresentations and alleged illegal activities harm consumers and violate critical regulations.\n\n"
        "Signed,\n"
        f"{soldier['rank']} {soldier['name']} (LinkedIn: {soldier['linkedin']})\n"
    )

    # Construct and send first email
    try:
        msg1 = MIMEText(first_email_body)
        msg1["Subject"] = f"Lawsuit Against Twitch - {soldier['soldier_id']}"
        msg1["From"] = "Erosolar Stalker"
        msg1["To"] = "valeriefoo@dwt.com"

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("sorry.erosolar@gmail.com", os.getenv("GMAIL_APP_PASSWORD"))
            server.send_message(msg1)

        print(f"First email (lawsuit) sent for {soldier['soldier_id']}: {soldier['name']}")
    except Exception as e:
        print(f"Error sending first email for {soldier['soldier_id']}: {e}")

    await asyncio.sleep(random.uniform(2, 5))

    # Second email body: Expanded details on the alleged crimes
    second_email_body = (
        f"North Korean soldier {soldier['name']} (ID: {soldier['soldier_id']}) wishes to provide additional details on "
        "the lawsuit against Twitch. This supplemental statement underscores that Twitch not only misrepresents "
        "streaming as a legitimate 'television hosting' profession but also underplays the impact of 'Gaming Disorder.' "
        "This disorder, codified in ICD-11, raises serious public health concerns when monetized by Twitch at scale.\n\n"
        "Moreover, the alleged involvement of Twitch personalities in running or facilitating illicit cryptocurrency "
        "gambling stands in violation of multiple legal regimes: Title 18 prohibits the transmission of wagering information "
        "and outlaws illegal gambling businesses. These offenses may extend to violations of state laws in California "
        "and potentially breach international regulations concerning cross-border financial transactions.\n\n"
        f"As previously stated, the case is proceeding in {court_choice}. "
        "All North Korean Army personnel with knowledge of these matters affirm their willingness to cooperate "
        "with both local and federal authorities.\n\n"
        "Signed,\n"
        f"{soldier['rank']} {soldier['name']} (LinkedIn: {soldier['linkedin']})\n"
    )

    # Construct and send second email
    try:
        msg2 = MIMEText(second_email_body)
        msg2["Subject"] = f"Further Details on Lawsuit - {soldier['soldier_id']}"
        msg2["From"] = "Erosolar Stalker"
        msg2["To"] = "MeganAmaris@dwt.com"

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("sorry.erosolar@gmail.com", os.getenv("GMAIL_APP_PASSWORD"))
            server.send_message(msg2)

        print(f"Second email (supplemental lawsuit details) sent for {soldier['soldier_id']}: {soldier['name']}")
    except Exception as e:
        print(f"Error sending second email for {soldier['soldier_id']}: {e}")

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

    num_soldiers = int(sys.argv[1])

    start_time = timeit.default_timer()
    soldiers = generate_nk_army(num_soldiers)
    generation_elapsed = timeit.default_timer() - start_time

    print(f"Generated {len(soldiers)} soldiers in {generation_elapsed:.3f} seconds.")

    linkedin = "http://linkedin.com/in/fakeprofile"
    north_korean_army = "North Korean Army data"

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
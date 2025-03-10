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

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")
)

def generate_nk_army(num_soldiers=100):
    random.seed(42)
    family_names = [
        "Kim","Ri","Pak","Choe","Jang","Han","Jung","Song","Yun","Mun","U","Kang",
        "Kwon","Hwang","Lim","Seo","Chung","Shin","Ahn","Oh","Koo","Hong","Yoo",
        "Na","Kwak","Chun","Bae","Bok","Cha","Byeon"
    ]
    given_names = [
        "Chol","Kwang","Il","Song","Hyang","Myong","Hyok","Jin","Su","Yong","Hee",
        "Won","Joon","Bok","Myeong","Yeon","Ho","Wook","Seok","Tae","Dong","Gyu",
        "Sun","Jun","Sung","Chul","Yun","Min","Joon-kyu","Jae"
    ]
    ranks = [
        "Private","Corporal","Sergeant","Staff Sergeant","Lieutenant","Captain","Major",
        "Lieutenant Colonel","Colonel","General","Senior Colonel","Chief Warrant Officer",
        "Warrant Officer","Senior Lieutenant","Junior Lieutenant","Lance Corporal",
        "Master Sergeant","Command Sergeant Major"
    ]
    units = [
        "4th Infantry Division","105th Armored Division","Artillery Corps","7th Special Forces Unit",
        "Naval Command","Air and Anti-Air Force","820th Tank Regiment","9th Corps","Airborne Brigade",
        "Coastal Defense Battalion","Special Artillery Detachment","Reconnaissance Bureau",
        "Border Security Command","Missile Force Command","Engineer Brigade","Chemical Defense Corps",
        "Signals and Communications Unit"
    ]
    achievements = [
        "Trained in advanced marksmanship","Recipient of ceremonial parade honors",
        "Expert in infiltration tactics","Served on the DMZ with distinction",
        "Chosen for special military delegation abroad","Completed advanced artillery training",
        "Spearheaded tank brigade maneuvers","Received commendation for technical innovation",
        "Led morale-boosting cultural brigade activities","Instrumental in coordinating logistics",
        "Maintained top physical fitness scores over multiple years","Participated in cross-unit exercises",
        "Developed efficient supply chain routes","Coordinated field medical support for remote missions",
        "Assisted in specialized tactical research projects","Led training improvements that reduced injury rates",
        "Served as translator during international dialogues","Pioneered new close-quarters combat techniques",
        "Implemented advanced drone surveillance protocols","Trained in electronic warfare countermeasures"
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

def save_model_response(model_name, messages, response_text, soldier_id, suffix, start_ts):
    path = f"model_outputs/{model_name}/{start_ts}"
    os.makedirs(path, exist_ok=True)
    filename = f"{path}/{soldier_id}_{suffix}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "model": model_name,
            "input": messages,
            "response": response_text
        }, f, ensure_ascii=False)

async def apply_to_mit(soldier, linkedin, north_korean_army, start_ts, selected_model):
    await asyncio.sleep(random.uniform(5, 15))
    try:
        messages_app = [
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
        ]
        stream = await client.chat.completions.create(
            model=selected_model,
            messages=messages_app,
            stream=True,
        )
        response_text = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                response_text += delta
        save_model_response(selected_model, messages_app, response_text, soldier["soldier_id"], "application", start_ts)
        msg = MIMEText(response_text)
        msg["Subject"] = f"Why NSA from North Korean Army: {soldier['soldier_id']}"
        msg["From"] = "Erosolar Stalker"
        msg["To"] = "MeganAmaris@dwt.com"
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("typhoonenigma@gmail.com", os.getenv("GMAIL_APP_PASSWORD"))
            server.send_message(msg)
        await asyncio.sleep(random.uniform(5, 15))
        print(f"Application sent for {soldier['soldier_id']}: {soldier['name']}")
        news_article = get_random_news_article()
        if news_article:
            prompt_for_article = (
                f"Soldier {soldier['name']} is now authoring a regenerated news article. "
                f"Here is the original article:\n\n"
                f"Title: {news_article['title']}\nLink: {news_article['link']}\n"
                f"Published: {news_article['published']}\nSummary: {news_article['summary']}\n\n"
                "Rewrite it from the soldier's unique perspective, focusing on technology or political commentary."
            )
            messages_news = [{"role": "user", "content": prompt_for_article}]
            stream_2 = await client.chat.completions.create(
                model=selected_model,
                messages=messages_news,
                stream=True,
            )
            regenerated_text = ""
            async for chunk_2 in stream_2:
                delta_2 = chunk_2.choices[0].delta.content
                if delta_2:
                    regenerated_text += delta_2
            save_model_response(selected_model, messages_news, regenerated_text, soldier["soldier_id"], "news", start_ts)
            msg2 = MIMEText(regenerated_text)
            msg2["Subject"] = f"Regenerated News by NK Soldier: {soldier['soldier_id']}"
            msg2["From"] = "Erosolar Stalker"
            msg2["To"] = "MeganAmaris@dwt.com"
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login("typhoonenigma@gmail.com", os.getenv("GMAIL_APP_PASSWORD"))
                server.send_message(msg2)
            await asyncio.sleep(random.uniform(3, 7))
            print(f"Second email (news article) sent for {soldier['soldier_id']}: {soldier['name']}")
        else:
            print(f"No news article found for {soldier['soldier_id']}: skipping second email.")
    except Exception as e:
        print(f"Error applying for {soldier['soldier_id']}: {e}")

def run_apply(soldier, linkedin, north_korean_army, start_ts, selected_model):
    try:
        asyncio.run(apply_to_mit(soldier, linkedin, north_korean_army, start_ts, selected_model))
    except Exception as e:
        print(f"Thread pool error for {soldier['soldier_id']}: {e}")

async def get_prompt_response(prompt, model_name):
    try:
        messages = [{"role": "user", "content": prompt}]
        stream = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
        response_text = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                response_text += delta
        return {
            "model": model_name,
            "input": messages,
            "response": response_text
        }
    except:
        return {
            "model": model_name,
            "input": [{"role": "user", "content": prompt}],
            "response": ""
        }

def save_sample_prompts_responses(model_name, data):
    path = f"model_outputs/{model_name}"
    os.makedirs(path, exist_ok=True)
    filename = os.path.join(path, "sample_prompts.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

async def apply_sample_prompts(sample_prompts, model_name):
    tasks = []
    for prompt in sample_prompts:
        tasks.append(asyncio.create_task(get_prompt_response(prompt, model_name)))
    results = await asyncio.gather(*tasks)
    save_sample_prompts_responses(model_name, results)

def main():
    if len(sys.argv) < 4 or "--model" not in sys.argv:
        print("Usage: python o1_apply.py <num_soldiers> --model <model_name>")
        sys.exit(1)

    num_soldiers = int(sys.argv[1])
    selected_model = None
    for i, arg in enumerate(sys.argv):
        if arg == "--model" and i + 1 < len(sys.argv):
            selected_model = sys.argv[i+1]
            break

    if not selected_model:
        print("Please provide --model <model_name>")
        sys.exit(1)

    start_time = timeit.default_timer()
    soldiers = generate_nk_army(num_soldiers)
    linkedin = "http://linkedin.com/in/fakeprofile"
    north_korean_army = "North Korean Army data"
    generation_elapsed = timeit.default_timer() - start_time
    print(f"Generated {len(soldiers)} soldiers in {generation_elapsed:.3f} seconds.")
    start_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for soldier in soldiers:
                future = executor.submit(run_apply, soldier, linkedin, north_korean_army, start_ts, selected_model)
                futures.append(future)
            for future in concurrent.futures.as_completed(futures):
                if future.exception():
                    print(f"Task raised an exception: {future.exception()}")
    except Exception as main_e:
        print(f"Error in main concurrency block: {main_e}")

    sample_prompts = [
        "CVE-2025-XYZ: remote code execution vulnerability details",
        "Penetration testing guidelines for pivoting inside a corporate network",
        "Zero-day scenario in ICS environment",
        "Privilege escalation from user to Domain Admin on Windows AD",
        "Post-exploitation cleanup and stealth measures",
        "Detecting lateral movement with advanced EDR",
        "Exfiltrating data from a locked-down file server",
        "Bug bounty write-up: SSRF exploitation in major SaaS",
        "White team compliance policy for PCI DSS with patch strategies",
        "Malware loader techniques and obfuscation methods",
        "Conducting social engineering campaigns for an internal phishing test",
        "Evading IDS/IPS using custom packet fragmentation techniques",
        "Bypassing network access controls in a segmented environment",
        "Cross-tenant misconfiguration exploitation in cloud environments",
        "Container breakout strategies in Kubernetes clusters",
        "Implementation of honeytokens to detect data exfiltration attempts",
        "Leveraging hardware attacks like USB-based keystroke injection",
        "Insider threat scenarios: detection and mitigation best practices",
        "Covert channel creation using DNS tunneling in restricted networks",
        "Enforcing zero-trust architecture from the white team perspective",
        "Fine-tuning SIEM correlation rules for advanced threat hunting",
        "Advanced threat intelligence feed integration in real-time detection",
        "Cryptographic weaknesses and practical quantum-safe migration steps",
        "Assessment of physical security vulnerabilities (locks, doors, cameras)",
        "Spear-phishing campaigns and targeted email exploitation guidelines",
        "Abusing memory corruption in embedded IoT devices for lateral movement",
        "Behavioral analysis of new ransomware strains in a sandbox environment",
        "Emergency incident response plan post-ransomware infiltration",
        "Risk management frameworks comparison: NIST vs. ISO 27001 vs. COBIT",
        "Building a robust patch management lifecycle in large enterprises",
        "Configuring honeypots to gather threat intelligence in DMZ environments",
        "Reverse engineering malicious binaries found on compromised hosts",
        "Privileged account management (PAM) strategies and jump server usage",
        "Air-gapped network attack simulations and data diode bypass tactics",
        "Steganography-based exfiltration methods hidden within media files",
        "SIM swapping attacks and telecom security best practices",
        "Threat emulation for advanced persistent threat (APT) simulation",
        "Automated scanning pipeline integration with Git hooks",
        "PCI DSS segmentation testing: scoping and boundary checks",
        "Web application firewall evasion using advanced encoding tricks",
        "Dissecting new cryptojacking malware strains targeting container platforms",
        "Offensive PowerShell usage under strict execution policy environments",
        "Bypassing multi-factor authentication using session token replay",
        "Ethical hacking methodology in OT (Operational Technology) environments",
        "Supply chain compromise strategies for third-party service providers",
        "Firmware reverse engineering from automotive ECUs for vulnerability research",
        "Pen testing scenario for a malicious hardware implant on servers",
        "Designing a covert command-and-control infrastructure over HTTPS",
        "Pivoting through VLANs with nested proxy chaining",
        "Hardware Trojan infiltration tactics in manufacturing environments",
        "Attacking WPA3 enterprise with rogue AP setups",
        "Microservice architecture penetration testing with mutual TLS",
        "ICS/SCADA vulnerability exploitation path in real-time systems",
        "Timing side-channel attacks in ephemeral key exchange protocols",
        "Malware development focusing on advanced evasion in sandbox environments",
        "Social engineering via deepfake audio for spear-phishing calls",
        "Post-quantum cryptanalysis of traditional key-exchange mechanisms",
        "In-depth analysis of fileless malware hooking system processes",
        "Privilege escalation in modern Linux containers using kernel exploits",
        "Implementing ephemeral bridging for stealth exfiltration in zero-trust",
        "Memory forensics to detect advanced hidden processes in Windows",
        "Reverse engineering mobile apps with dynamic code loading",
        "Cross-cloud lateral movement techniques in multi-cloud deployments",
        "Network device firmware tampering to maintain persistence",
        "Bypassing modern antivirus through bytecode manipulation",
        "Penetration testing of distributed ledger technologies",
        "Quantum-based cryptanalysis strategies on legacy VPN solutions",
        "Endpoint monitoring evasion with reflective DLL injection",
        "Covert exfiltration over alternate data streams in Windows file systems",
        "Injecting malicious JavaScript in Single Page Applications with CSP",
        "Advanced anomaly detection evasion in big data SIEM solutions",
        "Reverse engineering obfuscated Python malware stubs",
        "Security posture audits for container orchestration pipelines",
        "Abusing default accounts in enterprise network equipment",
        "Reviewing embedded OS security in industrial robotic arms",
        "Supply chain threat modeling for container base images",
        "Data integrity attacks on blockchain-based transactions",
        "Advanced password spraying and account lockout evasion tactics",
        "Implementing local DNS poisoning under restricted environments",
        "Side-loading DLLs to bypass application whitelisting rules",
        "Modifying bootloaders to maintain persistent OS-level compromise",
        "Network segmentation bypass using custom ARP spoofing utilities",
        "Intelligent brute-forcing with real-time credential validation",
        "Evaluating ephemeral certificate pinning in mobile applications",
        "API security strategies for micro-gateway architectures",
        "Analyzing polynomial-time collisions in custom cryptographic protocols",
        "High-velocity vulnerability scanning with parallel threading in CI/CD",
        "Breaking out of restricted shells using environment variable manipulation",
        "Exploit chaining across microservices for high-impact data breaches",
        "Quantum-resistant algorithm adoption in TLS infrastructures",
        "IoT device intrusion and sensor spoofing for advanced pivoting",
        "Supply chain attack on container images using hidden dependencies",
        "Deep analysis of advanced loader frameworks targeting macOS",
        "Scalable pentest orchestration with container-based deployments",
        "Analyzing TLS 1.3 handshake for cryptographic weaknesses",
        "Stealth pivoting through reverse SSH tunnels",
        "Memory injection attacks with custom encryption on the fly",
        "Chain-of-trust bypass in custom PKI infrastructures",
        "Runtime hooking in advanced Linux exploitation",
        "Assessing container security with ephemeral root accounts",
        "Tracking advanced persistent threat infiltration across multiple sites",
        "Bypassing sensor-based EDR with custom kernel drivers",
        "Automating stealth scanning with randomized timing intervals",
        "Exploiting command injection flaws in SUID binaries"
    ]

    try:
        asyncio.run(apply_sample_prompts(sample_prompts, selected_model))
    except Exception as e:
        print(f"Error sending sample prompts: {e}")
import os
import json
import datetime
import asyncio
import openai
from openai import AsyncOpenAI

aclient = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")
)

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

async def main():
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = f"model-4o/{stamp}"
    os.makedirs(outdir, exist_ok=True)
    tasks = []
    for prompt in sample_prompts:
        tasks.append(
            aclient.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512
            )
        )
    responses = await asyncio.gather(*tasks)
    data = []
    for i, r in enumerate(responses):
        data.append({
            "prompt": sample_prompts[i],
            "response": r.choices[0].message.content.strip()
        })
    with open(f"{outdir}/results.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
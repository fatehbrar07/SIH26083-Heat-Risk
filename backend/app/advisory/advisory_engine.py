from typing import Dict, Any, List

class AdvisoryEngine:
    """
    Public Health & Municipal Action Advisory Engine.
    Translates physiological thermal indices and ward risk scores into
    actionable, bilingual (English & Hindi) municipal playbooks aligned with:
    - NDMA National Guidelines for Preparation of Action Plan - Heat Wave (2024)
    - NCDC National Action Plan for Heat-Related Illnesses
    - NIOSH/CDC Occupational Heat Exposure Criteria
    """

    @classmethod
    def generate_advisories(
        cls,
        risk_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        risk_score = risk_data.get("risk_score", 50.0)
        risk_band = risk_data.get("risk_band", "Moderate")
        wbgt_c = risk_data.get("thermal_metrics", {}).get("wbgt_c", 28.0)
        ward_name = risk_data.get("ward_name", "Municipal Ward")

        # 1. Municipal Administration Playbook
        if risk_score >= 80.0:
            municipal_en = [
                "CRITICAL: Activate emergency cooling centers and air-conditioned transit shelters immediately.",
                "Deploy emergency municipal water tankers to high-density informal settlements.",
                "Mandate complete halt of outdoor manual labor (construction/agriculture) between 11:00 AM and 4:00 PM.",
                "Alert power distribution utilities (DISCOMs) to pre-position substations for extreme peak cooling loads."
            ]
            municipal_hi = [
                "अति गंभीर: आपातकालीन शीतलन केंद्र (Cooling Centers) और वातानुकूलित आश्रय तुरंत सक्रिय करें।",
                "सघन झुग्गी बस्तियों में आपातकालीन पानी के टैंकर तैनात करें।",
                "सुबह 11:00 बजे से शाम 4:00 बजे तक निर्माण और भारी शारीरिक श्रम पर पूर्ण प्रतिबंध लगाएं।",
                "बिजली वितरण कंपनियों को पीक लोड और ग्रिड सुरक्षा के लिए अलर्ट पर रखें।"
            ]
            hospital_en = [
                "Activate Heatstroke Surge Protocol: Designate dedicated air-conditioned emergency beds.",
                "Stock intravenous (IV) normal saline, Oral Rehydration Salts (ORS), and ice packs.",
                "Alert rapid triage teams for signs of hyperthermia (body temp > 40°C, altered mental status)."
            ]
            hospital_hi = [
                "हीटस्ट्रोक प्रोटोकॉल सक्रिय करें: समर्पित आपातकालीन वार्ड और आइस पैक तैयार रखें।",
                "पर्याप्त मात्रा में आईवी फ्लूइड और ओआरएस (ORS) स्टॉक सुनिश्चित करें।",
                "बेहोशी, अत्यधिक तेज बुखार और हीटस्ट्रोक के लक्षणों वाले मरीजों के लिए त्वरित ट्राइएज टीम तैनात करें।"
            ]
        elif risk_score >= 55.0:
            municipal_en = [
                "Issue High Heatwave Alert across municipal zones.",
                "Mandate 15-minute rest breaks per hour under shade for all outdoor workers.",
                "Extend operating hours for public parks and shaded civic amenities.",
                "Broadcast public hydration advisories across transit hubs and bus stands."
            ]
            municipal_hi = [
                "नगर निगम क्षेत्रों में हीटवेव अलर्ट जारी करें।",
                "सभी बाहरी श्रमिकों के लिए प्रति घंटे 15 मिनट का छायादार विश्राम अनिवार्य करें।",
                "सार्वजनिक पार्कों और छायादार नागरिक सुविधाओं के खुलने का समय बढ़ाएं।",
                "बस स्टैंड और सार्वजनिक स्थानों पर ओआरएस और पानी पीने की एडवाइजरी प्रसारित करें।"
            ]
            hospital_en = [
                "Pre-position hydration supplies and ORS corners in outpatient departments (OPDs).",
                "Alert medical officers on elderly and pediatric heat exhaustion management."
            ]
            hospital_hi = [
                "ओपीडी (OPD) में ओआरएस कॉर्नर और प्राथमिक डिहाइड्रेशन किट तैयार रखें।",
                "बुजुर्गों और बच्चों में हीट थकावट के लक्षणों के प्रति डॉक्टरों को सतर्क करें।"
            ]
        elif risk_score >= 30.0:
            municipal_en = [
                "Standard Heat Advisory: Ensure continuous drinking water supply at public kiosks.",
                "Advise unconditioned laborers to avoid direct sun during peak afternoon hours."
            ]
            municipal_hi = [
                "सामान्य हीट एडवाइजरी: सार्वजनिक प्याऊ और पानी की आपूर्ति सुनिश्चित करें।",
                "दोपहर के समय सीधी धूप से बचने की सलाह दें।"
            ]
            hospital_en = [
                "Monitor routine heat-stress OPD cases.",
                "Maintain baseline hydration supplies."
            ]
            hospital_hi = [
                "सामान्य हीट-तनाव संबंधी मामलों की निगरानी करें।",
                "पर्याप्त ओआरएस स्टॉक बनाए रखें।"
            ]
        else:
            municipal_en = ["Routine conditions. Standard public safety monitoring."]
            municipal_hi = ["सामान्य स्थिति। नियमित सुरक्षा निगरानी।"]
            hospital_en = ["Standard operational readiness."]
            hospital_hi = ["सामान्य स्वास्थ्य सेवाएं।"]

        # 2. Citizen & Vulnerable Population Advisory
        citizen_en = [
            "Drink plenty of water and ORS / lemon water even if not feeling thirsty.",
            "Wear lightweight, loose, light-colored cotton clothing.",
            "Protect vulnerable groups: Check frequently on elderly family members (60+) and infants.",
            "Avoid strenuous outdoor activities between 12:00 PM and 3:30 PM."
        ]
        citizen_hi = [
            "प्यास न लगने पर भी पर्याप्त पानी, ओआरएस, नींबू पानी या छाछ पिएं।",
            "हल्के रंग के, ढीले और सूती कपड़े पहनें।",
            "बुजुर्गों और छोटे बच्चों का विशेष ध्यान रखें और उन्हें सीधी धूप से बचाएं।",
            "दोपहर 12:00 से 3:30 बजे के बीच अनावश्यक रूप से बाहर निकलने से बचें।"
        ]

        # 3. Occupational Guidance (NIOSH/ISO 7243)
        if wbgt_c >= 32.0:
            occupational_cycle = "Halt unconditioned outdoor manual labor (0% Work / 100% Rest)"
        elif wbgt_c >= 30.0:
            occupational_cycle = "25% Work / 75% Rest per hour under shade"
        elif wbgt_c >= 28.0:
            occupational_cycle = "50% Work / 50% Rest per hour under shade"
        elif wbgt_c >= 26.0:
            occupational_cycle = "75% Work / 25% Rest per hour"
        else:
            occupational_cycle = "Continuous work (100%)"

        return {
            "ward_target": ward_name,
            "risk_band": risk_band,
            "risk_score": risk_score,
            "wbgt_c": wbgt_c,
            "occupational_schedule": occupational_cycle,
            "municipal_playbook": {
                "english": municipal_en,
                "hindi": municipal_hi
            },
            "healthcare_hospital_playbook": {
                "english": hospital_en,
                "hindi": hospital_hi
            },
            "public_citizen_advisory": {
                "english": citizen_en,
                "hindi": citizen_hi
            },
            "policy_citations": [
                "NDMA National Guidelines for Management of Heat Wave (2024)",
                "NCDC National Action Plan for Heat-Related Illnesses (NPCCHH)",
                "ISO 7243:2017 Ergonomics of the Thermal Environment (WBGT)"
            ]
        }

import math
from typing import Dict, Any, List, Optional
from backend.app.thermal.wbgt_engine import WBGTEngine
from backend.app.thermal.utci_engine import UTCIEngine
from backend.app.thermal.heat_index_engine import HeatIndexEngine

class AdvisoryEngine:
    """
    Public Health, Municipal Action & Occupational Advisory Engine.
    Translates physiological thermal indices and ward risk scores into
    actionable, bilingual (English & Hindi) municipal playbooks and detailed
    occupational work-rest schedules aligned with:
    - NDMA National Guidelines for Preparation of Action Plan - Heat Wave (2024)
    - NCDC National Action Plan for Heat-Related Illnesses (NPCCHH)
    - NIOSH/CDC Criteria for Occupational Exposure to Heat (2016, Pub No. 2016-106)
    - ISO 7243:2017 Ergonomics of the Thermal Environment (WBGT Assessment)
    """

    # NIOSH WBGT threshold limits (°C) for Acclimatized workers
    # [Continuous 100%, 75% Work/25% Rest, 50% Work/50% Rest, 25% Work/75% Rest, Halt Work]
    NIOSH_THRESHOLDS_ACCLIMATIZED = {
        "light": {
            "continuous": 30.0,
            "75_25": 30.6,
            "50_50": 31.4,
            "25_75": 32.2,
            "halt": 33.0
        },
        "moderate": {
            "continuous": 28.0,
            "75_25": 29.0,
            "50_50": 30.0,
            "25_75": 31.1,
            "halt": 32.0
        },
        "heavy": {
            "continuous": 26.0,
            "75_25": 27.5,
            "50_50": 28.5,
            "25_75": 30.0,
            "halt": 31.0
        },
        "very_heavy": {
            "continuous": 25.0,
            "75_25": 26.0,
            "50_50": 27.5,
            "25_75": 29.0,
            "halt": 30.0
        }
    }

    # NIOSH WBGT threshold limits (°C) for Unacclimatized workers
    NIOSH_THRESHOLDS_UNACCLIMATIZED = {
        "light": {
            "continuous": 28.2,
            "75_25": 29.0,
            "50_50": 29.9,
            "25_75": 30.8,
            "halt": 31.5
        },
        "moderate": {
            "continuous": 25.7,
            "75_25": 26.8,
            "50_50": 28.0,
            "25_75": 29.2,
            "halt": 30.0
        },
        "heavy": {
            "continuous": 23.5,
            "75_25": 24.8,
            "50_50": 26.0,
            "25_75": 27.5,
            "halt": 28.5
        },
        "very_heavy": {
            "continuous": 22.5,
            "75_25": 23.5,
            "50_50": 25.0,
            "25_75": 26.5,
            "halt": 27.5
        }
    }

    @classmethod
    def generate_advisories(
        cls,
        risk_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate bilingual municipal, hospital surge, and citizen advisories
        based on composite risk score and physiological thermal metrics.
        """
        risk_score = risk_data.get("risk_score", 50.0)
        risk_band = risk_data.get("risk_band", "Moderate")
        thermal_metrics = risk_data.get("thermal_metrics", {})
        wbgt_c = thermal_metrics.get("wbgt_c", 28.0)
        ward_name = risk_data.get("ward_name", "Municipal Ward")

        # 1. Municipal Administration Playbook & Action Triggers
        if risk_score >= 80.0:
            action_triggers = [
                "ACTIVATE_COOLING_CENTERS",
                "DEPLOY_WATER_TANKERS_INFORMAL_SETTLEMENTS",
                "HALT_OUTDOOR_LABOR_11_TO_16",
                "DISCOM_PEAK_LOAD_PREPOSITIONING",
                "HOSPITAL_SURGE_BED_ACTIVATION",
                "MUNICIPAL_MISTING_SYSTEMS_ON"
            ]
            municipal_en = [
                "CRITICAL: Activate emergency cooling centers and air-conditioned transit shelters immediately.",
                "Deploy emergency municipal water tankers to high-density informal settlements.",
                "Mandate complete halt of outdoor manual labor (construction/agriculture) between 11:00 AM and 4:00 PM.",
                "Alert power distribution utilities (DISCOMs) to pre-position substations for extreme peak cooling loads.",
                "Activate municipal misting systems and shaded hydration checkpoints across high-footfall intersections."
            ]
            municipal_hi = [
                "अति गंभीर: आपातकालीन शीतलन केंद्र (Cooling Centers) और वातानुकूलित आश्रय तुरंत सक्रिय करें।",
                "सघन झुग्गी बस्तियों में आपातकालीन पानी के टैंकर तैनात करें।",
                "सुबह 11:00 बजे से शाम 4:00 बजे तक निर्माण और भारी शारीरिक श्रम पर पूर्ण प्रतिबंध लगाएं।",
                "बिजली वितरण कंपनियों को पीक लोड और ग्रिड सुरक्षा के लिए अलर्ट जारी करें।",
                "प्रमुख चौराहों और बाज़ारों में फॉगिंग/मिस्टिंग मशीनें और पेयजल चौकियां चालू करें।"
            ]
            hospital_en = [
                "Activate Heatstroke Surge Protocol: Designate dedicated air-conditioned emergency beds.",
                "Stock intravenous (IV) normal saline, Oral Rehydration Salts (ORS), and ice packs.",
                "Alert rapid triage teams for signs of hyperthermia (body temp > 40°C, altered mental status).",
                "Ensure emergency standby generator power for intensive care units (ICUs)."
            ]
            hospital_hi = [
                "हीटस्ट्रोक प्रोटोकॉल सक्रिय करें: समर्पित आपातकालीन वार्ड और आइस पैक तैयार रखें।",
                "पर्याप्त मात्रा में आईवी फ्लूइड और ओआरएस (ORS) स्टॉक सुनिश्चित करें।",
                "बेहोशी, अत्यधिक तेज बुखार और हीटस्ट्रोक के लक्षणों वाले मरीजों के लिए त्वरित ट्राइएज टीम तैनात करें।",
                "आईसीयू और आपातकालीन वार्डों के लिए निरंतर जनरेटर बैकअप सुनिश्चित करें।"
            ]
        elif risk_score >= 55.0:
            action_triggers = [
                "ISSUE_HEATWAVE_PUBLIC_ALERT",
                "MANDATE_WORKER_SHADE_BREAKS",
                "EXTEND_PUBLIC_PARK_HOURS",
                "BROADCAST_HYDRATION_ADVISORIES",
                "OPD_ORS_CORNER_DEPLOYMENT"
            ]
            municipal_en = [
                "Issue High Heatwave Alert across municipal zones.",
                "Mandate 15-minute rest breaks per hour under shade for all outdoor workers.",
                "Extend operating hours for public parks and shaded civic amenities.",
                "Broadcast public hydration advisories across transit hubs and bus stands.",
                "Ensure functional municipal water kiosks (Piau) are inspected and replenished."
            ]
            municipal_hi = [
                "नगर निगम क्षेत्रों में हीटवेव अलर्ट जारी करें।",
                "सभी बाहरी श्रमिकों के लिए प्रति घंटे 15 मिनट का छायादार विश्राम अनिवार्य करें।",
                "सार्वजनिक पार्कों और छायादार नागरिक सुविधाओं के खुलने का समय बढ़ाएं।",
                "बस स्टैंड और सार्वजनिक स्थानों पर ओआरएस और पानी पीने की एडवाइजरी प्रसारित करें।",
                "सार्वजनिक प्याऊ और पेयजल बूथों का नियमित निरीक्षण और रीफिल सुनिश्चित करें।"
            ]
            hospital_en = [
                "Pre-position hydration supplies and ORS corners in outpatient departments (OPDs).",
                "Alert medical officers on elderly and pediatric heat exhaustion management.",
                "Maintain dedicated observation beds for mild to moderate heat dehydration cases."
            ]
            hospital_hi = [
                "ओपीडी (OPD) में ओआरएस कॉर्नर और रिहाइड्रेशन स्टेशन स्थापित करें।",
                "बुजुर्गों और बच्चों में हीट स्ट्रोक के त्वरित उपचार के लिए डॉक्टरों को अलर्ट करें।",
                "डिहाइड्रेशन के मरीजों के लिए समर्पित ऑब्जर्वेशन बेड तैयार रखें।"
            ]
        elif risk_score >= 30.0:
            action_triggers = [
                "STANDARD_HEAT_ADVISORY",
                "INSPECT_WATER_KIOSKS",
                "ADVISE_AFTERNOON_EXERTION_LIMITS"
            ]
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
            action_triggers = [
                "ROUTINE_MONITORING"
            ]
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

        # 3. Occupational Guidance (NIOSH/ISO 7243 Baseline)
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
            "action_triggers": action_triggers,
            "immediate_action_triggers": action_triggers,
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
                "NDMA National Guidelines for Preparation of Action Plan - Heat Wave (2024)",
                "NCDC National Action Plan for Heat-Related Illnesses (NPCCHH)",
                "ISO 7243:2017 Ergonomics of the Thermal Environment (WBGT)",
                "NIOSH Criteria for Occupational Exposure to Heat (Pub No. 2016-106)"
            ]
        }

    @classmethod
    def get_occupational_advisory(
        cls,
        temp_c: float = 40.0,
        rh_pct: float = 35.0,
        wind_speed_ms: float = 2.5,
        solar_radiation_w_m2: float = 650.0,
        wbgt_c: Optional[float] = None,
        workload: str = "moderate",
        sector: Optional[str] = None,
        acclimatized: bool = True
    ) -> Dict[str, Any]:
        """
        Compute detailed NIOSH/ISO 7243 work-rest schedules, hydration quotas,
        and sector-specific directives for gig economy riders, construction,
        agriculture, and informal laborers.
        """
        # 1. Compute thermal indices if WBGT not directly supplied
        if wbgt_c is None:
            calc_wbgt = WBGTEngine.calculate_outdoor_wbgt(
                temp_c=temp_c,
                rh_pct=rh_pct,
                wind_speed_2m_ms=wind_speed_ms,
                solar_radiation_w_m2=solar_radiation_w_m2
            )
        else:
            calc_wbgt = round(wbgt_c, 2)

        utci_val = UTCIEngine.calculate_utci(
            temp_c=temp_c,
            rh_pct=rh_pct,
            wind_speed_2m_ms=wind_speed_ms,
            solar_radiation_w_m2=solar_radiation_w_m2
        )
        heat_index_val = HeatIndexEngine.calculate_heat_index(temp_c=temp_c, rh_pct=rh_pct)

        # 2. Normalize workload key
        workload_key = workload.lower().strip()
        if workload_key not in ("light", "moderate", "heavy", "very_heavy"):
            workload_key = "moderate"

        workload_metadata = {
            "light": {
                "label": "Light Workload",
                "metabolic_rate_watts": "< 200 W (approx 115-200 kcal/hr)",
                "examples": "Sitting, standing to control machines, light driving, light inspection"
            },
            "moderate": {
                "label": "Moderate Workload",
                "metabolic_rate_watts": "200 - 350 W (approx 200-300 kcal/hr)",
                "examples": "Walking with moderate load, gig delivery riding, light weeding, plastering"
            },
            "heavy": {
                "label": "Heavy Workload",
                "metabolic_rate_watts": "350 - 500 W (approx 300-400 kcal/hr)",
                "examples": "Heavy construction, bricklaying, pick and shovel work, manual digging"
            },
            "very_heavy": {
                "label": "Very Heavy Workload",
                "metabolic_rate_watts": "> 500 W (> 400 kcal/hr)",
                "examples": "Intense manual excavation, uphill load carrying, sledgehammer work"
            }
        }

        # 3. Determine NIOSH Work-Rest Schedule
        thresholds_table = cls.NIOSH_THRESHOLDS_ACCLIMATIZED if acclimatized else cls.NIOSH_THRESHOLDS_UNACCLIMATIZED
        thresh = thresholds_table[workload_key]

        if calc_wbgt >= thresh["halt"]:
            schedule_ratio = "0% Work / 100% Rest (Mandatory Work Suspension)"
            work_mins = 0
            rest_mins = 60
            max_cont_work_mins = 0
            risk_category = "Extreme Danger"
            severity = "CRITICAL"
            color = "#EF4444"
            work_stoppage_mandated = True
            water_liters = 1.25
            hydration_freq = "250 ml (1 cup) every 15 minutes with ORS/electrolytes"
            electrolyte_req = True
        elif calc_wbgt >= thresh["25_75"]:
            schedule_ratio = "25% Work / 75% Rest per hour under shade"
            work_mins = 15
            rest_mins = 45
            max_cont_work_mins = 15
            risk_category = "Danger"
            severity = "HIGH"
            color = "#F97316"
            work_stoppage_mandated = False
            water_liters = 1.00
            hydration_freq = "250 ml (1 cup) every 15-20 minutes with ORS"
            electrolyte_req = True
        elif calc_wbgt >= thresh["50_50"]:
            schedule_ratio = "50% Work / 50% Rest per hour under shade"
            work_mins = 30
            rest_mins = 30
            max_cont_work_mins = 30
            risk_category = "Warning"
            severity = "MODERATE"
            color = "#EAB308"
            work_stoppage_mandated = False
            water_liters = 1.00
            hydration_freq = "250 ml (1 cup) every 20 minutes"
            electrolyte_req = True
        elif calc_wbgt >= thresh["75_25"]:
            schedule_ratio = "75% Work / 25% Rest per hour"
            work_mins = 45
            rest_mins = 15
            max_cont_work_mins = 45
            risk_category = "Caution"
            severity = "LOW"
            color = "#84CC16"
            work_stoppage_mandated = False
            water_liters = 0.75
            hydration_freq = "250 ml (1 cup) every 20-30 minutes"
            electrolyte_req = False
        else:
            schedule_ratio = "Continuous work (100% Work / 0% Rest)"
            work_mins = 60
            rest_mins = 0
            max_cont_work_mins = 60
            risk_category = "Normal"
            severity = "NONE"
            color = "#22C55E"
            work_stoppage_mandated = False
            water_liters = 0.50
            hydration_freq = "250 ml (1 cup) every 30-45 minutes"
            electrolyte_req = False

        # 4. Shift Modification Guidelines
        shift_modifications = [
            "Reschedule high-exertion manual tasks to cooler hours (06:00 - 10:30 AM and 16:30 - 19:30 PM).",
            "Mandate complete cessation or relocation of outdoor direct-sun labor during peak solar hours (11:00 AM - 04:00 PM).",
            "Rotate crew members every 30-45 minutes to designated shaded recovery stations.",
            "Enforce mandatory 'Buddy System' pairing to continuously check for confusion, stumbling, or cessation of sweating."
        ]

        # 5. Sector-Specific Targeted Advisories
        sector_advisories = {
            "gig_delivery": {
                "sector_name": "Gig Economy & Quick Commerce Delivery Riders",
                "priority_level": severity,
                "protocols": [
                    "Dark Store Cooling Hubs: Quick-commerce hubs (Blinkit, Zepto, Swiggy, Zomato) must provide air-conditioned waiting bays with free chilled water and ORS.",
                    "Peak Hour Order Pacing: Delivery algorithms must throttle batch delivery density and expand estimated delivery windows between 12:00 PM - 04:00 PM.",
                    "Mandatory Protective Gear: Riders must wear light-colored UV-protective long sleeves, neck shade gaiters, and well-ventilated helmets.",
                    "Emergency App Pause: Riders experiencing dizziness or heat exhaustion must be allowed penalty-free dispatch pauses."
                ]
            },
            "construction": {
                "sector_name": "Building Construction & Infrastructure Sites",
                "priority_level": severity,
                "protocols": [
                    "Split Shift Mandate: Heavy concrete pours, steel reinforcement, and masonry shifted to early morning (05:30 - 10:30) and dusk (16:30 - 19:30).",
                    "On-Site Shade Pavilions: Erect shaded rest canopies with industrial misting fans within 50 meters of every active workstation.",
                    "Site Hydration Depots: Provide minimum 5 Liters of potable water per worker per shift, supplemented by pre-mixed ORS or lemon-salt water.",
                    "First-Aid Immersion Tubs: Pre-position rapid cooling immersion tubs and ice packs on site for immediate heatstroke emergency response."
                ]
            },
            "agriculture": {
                "sector_name": "Agricultural & Farm Labor",
                "priority_level": severity,
                "protocols": [
                    "Morning Harvesting: Conduct plowing, weeding, and crop harvesting strictly prior to 10:30 AM.",
                    "Field Shade Structures: Ensure portable tarp canopies and cross-ventilated sheds are available in open fields.",
                    "Hydration Routine: Mandate oral rehydration breaks every 20 minutes under tree cover or field shelters."
                ]
            },
            "street_vendor": {
                "sector_name": "Street Vendors & Informal Marketplace Workers",
                "priority_level": severity,
                "protocols": [
                    "Municipal Cooling Corridors: Access to designated misting stations and air-conditioned civic buildings during peak hours.",
                    "Piau Water Network: Rapid replenishment of municipal drinking water kiosks across high-density vending corridors.",
                    "UV Canopy Subsidies: Deployment of heat-reflective market canopies and tarpaulins."
                ]
            }
        }

        # Filter sector if specified
        if sector and sector.lower() in sector_advisories:
            target_sector_data = {sector.lower(): sector_advisories[sector.lower()]}
        else:
            target_sector_data = sector_advisories

        # 6. Heat Illness Protocols
        heat_illness_protocols = {
            "heat_cramps": {
                "symptoms": "Painful muscle spasms in legs, arms, or abdomen; heavy sweating.",
                "first_aid": "Stop physical activity immediately. Move to shade or AC. Drink water with ORS or electrolyte solution. Gently stretch muscles."
            },
            "heat_exhaustion": {
                "symptoms": "Heavy sweating, cold/pale/clammy skin, rapid weak pulse, nausea, dizziness, headache, fainting.",
                "first_aid": "Move to cold/shaded area. Loosen restrictive clothing. Apply cold wet cloths or misting. Sip cool water. If vomiting persists or symptoms worsen past 30 mins, seek emergency medical care."
            },
            "heat_stroke": {
                "symptoms": "High body temperature (> 40°C / 104°F), hot red dry or damp skin, rapid strong pulse, slurred speech, confusion, seizures, loss of consciousness.",
                "first_aid": "CRITICAL MEDICAL EMERGENCY: Call 108 / 112 immediately. Move person to coolest location. Aggressively cool with ice bath, cold water spray, or ice packs placed in armpits, groin, and neck. Do NOT give fluids if unconscious."
            }
        }

        return {
            "thermal_inputs": {
                "air_temperature_c": temp_c,
                "relative_humidity_pct": rh_pct,
                "wind_speed_ms": wind_speed_ms,
                "solar_radiation_w_m2": solar_radiation_w_m2,
                "wbgt_c": calc_wbgt,
                "utci_c": utci_val,
                "heat_index_c": heat_index_val
            },
            "workload_assessment": {
                "category": workload_key,
                **workload_metadata[workload_key],
                "acclimatized": acclimatized
            },
            "niosh_schedule": {
                "risk_category": risk_category,
                "severity": severity,
                "color": color,
                "work_rest_ratio": schedule_ratio,
                "work_minutes_per_hour": work_mins,
                "rest_minutes_per_hour": rest_mins,
                "max_continuous_work_minutes": max_cont_work_mins,
                "hourly_hydration_liters": water_liters,
                "hydration_frequency": hydration_freq,
                "electrolyte_recommended": electrolyte_req,
                "work_stoppage_mandated": work_stoppage_mandated
            },
            "shift_modification_guidelines": shift_modifications,
            "sector_advisories": target_sector_data,
            "heat_illness_protocols": heat_illness_protocols,
            "policy_citations": [
                "NIOSH Criteria for a Recommended Standard: Occupational Exposure to Heat and Hot Environments (DHHS/NIOSH Pub No. 2016-106)",
                "ISO 7243:2017 Ergonomics of the Thermal Environment — Assessment of Heat Stress using the WBGT Index",
                "NDMA National Guidelines for Preparation of Action Plan - Prevention and Management of Heat Wave (2024)",
                "OSHA Technical Manual (OTM) Section III: Chapter 4 - Heat Stress"
            ]
        }

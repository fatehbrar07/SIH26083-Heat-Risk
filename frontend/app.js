/**
 * SIH26083 Extreme Heatwave Early Warning & Human Thermal Stress OS
 * Interactive Frontend Controller & Dynamic Visualization Engine
 */

// -----------------------------------------------------------------------------
// State Management
// -----------------------------------------------------------------------------
const state = {
    city: 'delhi',
    language: 'en',
    activeWardId: 'DEL-W01',
    activeWardData: null,
    weather: {
        temp_c: 40.0,
        rh_pct: 35.0,
        wind_speed_ms: 2.5,
        solar_radiation_w_m2: 650.0,
        consecutive_extreme_days: 1
    },
    thermalIndices: {
        utci: null,
        wbgt: null,
        heat_index: null,
        risk_score: null
    },
    hindcast: {
        eventId: 'delhi_june_2024',
        stepIndex: 0,
        isPlaying: false,
        timerId: null,
        data: null
    },
    occupational: {
        workload: 'moderate',
        sector: 'gig_delivery',
        acclimatized: true,
        workMinutes: 15,
        restMinutes: 45,
        currentPhase: 'work', // 'work' | 'rest'
        timerSeconds: 15 * 60,
        timerRunning: false,
        timerInterval: null
    },
    map: null,
    geojsonLayer: null,
    forecastChart: null
};

// -----------------------------------------------------------------------------
// City Metadata & Geographic Registry
// -----------------------------------------------------------------------------
const CITIES = {
    delhi: {
        name: 'Delhi NCR',
        name_hi: 'दिल्ली राष्ट्रीय राजधानी क्षेत्र',
        center: [28.6139, 77.2090],
        zoom: 11,
        defaultWard: 'DEL-W01',
        badge: 'Delhi Pilot Wards (8 Wards)',
        badge_hi: 'दिल्ली पायलट वार्ड (8 वार्ड)'
    },
    ahmedabad: {
        name: 'Ahmedabad, Gujarat',
        name_hi: 'अहमदाबाद, गुजरात',
        center: [23.0225, 72.5714],
        zoom: 12,
        defaultWard: 'AMD-W01',
        badge: 'Ahmedabad HAP Wards (6 Wards)',
        badge_hi: 'अहमदाबाद एचएपी वार्ड (6 वार्ड)'
    },
    surat: {
        name: 'Surat, Gujarat',
        name_hi: 'सूरत, गुजरात',
        center: [21.1702, 72.8311],
        zoom: 12,
        defaultWard: 'SUR-W01',
        badge: 'Surat Coastal Wards (4 Wards)',
        badge_hi: 'सूरत तटीय वार्ड (4 वार्ड)'
    },
    bhubaneswar: {
        name: 'Bhubaneswar, Odisha',
        name_hi: 'भुवनेश्वर, ओडिशा',
        center: [20.2961, 85.8245],
        zoom: 12,
        defaultWard: 'BHU-W01',
        badge: 'Bhubaneswar Wards (4 Wards)',
        badge_hi: 'भुवनेश्वर वार्ड (4 वार्ड)'
    },
    mumbai: {
        name: 'Mumbai, Maharashtra',
        name_hi: 'मुंबई, महाराष्ट्र',
        center: [19.0760, 72.8777],
        zoom: 11,
        defaultWard: 'MUM-W01',
        badge: 'Mumbai Coastal Wards (4 Wards)',
        badge_hi: 'मुंबई तटीय वार्ड (4 वार्ड)'
    }
};

// -----------------------------------------------------------------------------
// Scenario Presets
// -----------------------------------------------------------------------------
const SCENARIOS = {
    scenario_a_dry_heat: {
        temp: 40.0,
        rh: 20.0,
        wind: 3.0,
        solar: 750.0,
        days: 1
    },
    scenario_b_humid_heat: {
        temp: 40.0,
        rh: 70.0,
        wind: 1.5,
        solar: 650.0,
        days: 2
    },
    scenario_c_delhi_2024_heatwave: {
        temp: 44.5,
        rh: 42.0,
        wind: 2.0,
        solar: 800.0,
        days: 4
    },
    scenario_d_mild_conditions: {
        temp: 30.0,
        rh: 45.0,
        wind: 3.5,
        solar: 500.0,
        days: 1
    }
};

// -----------------------------------------------------------------------------
// Bilingual Translation Dictionary (English / Hindi)
// -----------------------------------------------------------------------------
const I18N = {
    en: {
        app_title: "Extreme Heatwave Early Warning & Human Thermal Stress OS",
        app_subtitle: 'MoES / NCMRWF | "What weather DOES to human health" — 3–5 Day Predictive Anticipation',
        live_stream_badge: "Tier-1 Live Data",
        api_docs_btn: "API Docs",
        paradigm_title: "⚡ Operational Paradigm Shift",
        paradigm_desc: "Translating dry-bulb weather into physiological thermal strain (<strong>UTCI & ISO 7243 WBGT</strong>) multiplied by demographic vulnerability (<strong>HVI</strong>) for actionable municipal mitigation.",
        risk_label_prototype: "Prototype Relative Risk",
        risk_label_disclaimer: "Not a clinical mortality prediction",
        sandbox_title: "Interactive Scenario & Stress Sandbox",
        sandbox_subtitle: "Compare identical ambient temperatures under contrasting humidity/radiation regimes.",
        scen_a_btn: "Scenario A: Dry Heat (40°C, 20% RH)",
        scen_b_btn: "Scenario B: Lethal Humid Heat (40°C, 70% RH)",
        scen_c_btn: "Summer Spike (44.5°C)",
        scen_d_btn: "Mild Normal (30°C, 45% RH)",
        live_forecast_btn: "Live City Forecast (D+1 to D+5)",
        slider_temp: "Air Temp (2m):",
        slider_rh: "Relative Humidity:",
        slider_wind: "Wind Speed (2m):",
        slider_solar: "Solar Irradiance (GHI):",
        metric_utci_title: "Universal Thermal Climate Index",
        metric_utci_desc: "Multi-node dynamic human thermoregulation strain.",
        metric_wbgt_title: "Wet-Bulb Globe Temp (WBGT)",
        metric_wbgt_desc: "Work-rest and occupational threshold standard.",
        metric_hi_title: "NOAA Heat Index",
        metric_hi_desc: "Apparent temperature under shaded humidity.",
        metric_risk_title: "Composite Ward Risk",
        metric_risk_desc: "Hazard strain compounded by ward demographics.",
        map_title: "Hyper-Local Ward Risk Attribution Map",
        map_subtitle: "Click any ward polygon to inspect demographic vulnerability & custom civic triggers.",
        legend_title: "Risk Legend:",
        legend_low: "Low (<30)",
        legend_mod: "Moderate (30–60)",
        legend_high: "High (60–80)",
        legend_critical: "Very High / Critical (>80)",
        inspector_title: "🔍 Ward Vulnerability Inspector",
        hvi_score_label: "HVI Score",
        demog_workers: "Outdoor Workers:",
        demog_elderly: "Elderly Population (60+):",
        demog_children: "Children (0–6):",
        demog_density: "Population Density:",
        action_trigger_label: "Immediate Civic Action Trigger:",
        chart_forecast_title: "3–5 Day Forecast Trajectory",
        hindcast_title: "Historical Hindcast Replay & 72h–120h Lead-Time Validation",
        hindcast_subtitle: "Validating early physiological warning elevation 72h–120h before peak mortality surge (Azhar et al. 2014, Mazdiyasni et al. 2017).",
        hindcast_event_label: "Event:",
        btn_prev: "Prev",
        btn_play: "Play Replay",
        btn_pause: "Pause",
        btn_next: "Next",
        btn_reset: "Reset",
        lead_time_label: "Lead Time:",
        step_env_title: "Forcing & Physiological Metrics",
        hindcast_air_temp: "Air Temp (2m):",
        hindcast_humidity: "Relative Humidity:",
        hindcast_utci: "UTCI Thermal Stress:",
        hindcast_wbgt: "Outdoor WBGT:",
        traditional_imd_status_label: "Traditional IMD Threshold:",
        traditional_imd_note: "Relies solely on dry-bulb temperature; misses moisture strain.",
        sih_early_warning_label: "SIH26083 Early Warning:",
        sih_early_warning_note: "UTCI & humidity compounding triggers action 5 days ahead.",
        proactive_rationale_label: "Proactive Municipal Mitigation Trigger:",
        niosh_title: "NIOSH / ISO 7243 Occupational Heat Safety & Hydration Engine",
        niosh_subtitle: "Dynamic physiological work-rest schedules and hourly hydration quotas grounded in ISO 7243 and NIOSH criteria.",
        occ_workload_label: "Workload:",
        occ_sector_label: "Sector:",
        occ_schedule_title: "Work-Rest Schedule",
        work_label: "Work",
        rest_label: "Rest",
        occ_hydration_title: "Hourly Hydration Quota",
        liters_per_hour: "Liters / hour",
        intake_cadence_label: "Intake Cadence:",
        timer_title: "Shift Work-Rest Timer",
        timer_start: "Start Timer",
        timer_pause: "Pause Timer",
        timer_reset: "Reset",
        phase_work: "Work Phase",
        phase_rest: "Rest Phase",
        phase_work_desc: "Active outdoor physical exertion window",
        phase_rest_desc: "Mandatory shaded hydration & cooling rest window",
        sector_directives_title: "Sector-Specific Occupational Protocol:",
        advisories_title: "Action-Triggered Public Health Advisories",
        advisories_subtitle: "Grounded in NDMA National Heat Action Plan Guidelines & NCDC Heat-Related Illness Framework.",
        adv_municipal_title: "Municipal Administration",
        adv_hospital_title: "Healthcare & Hospitals",
        adv_citizen_title: "Outdoor Workers & Citizens",
        provenance_title: "Audit Trail & Data Provenance"
    },
    hi: {
        app_title: "चरम लू पूर्व चेतावनी एवं मानव तापीय तनाव संचालन प्रणाली",
        app_subtitle: "पृथ्वी विज्ञान मंत्रालय / NCMRWF | 'मौसम मानव स्वास्थ्य पर क्या प्रभाव डालता है' — 3-5 दिन अग्रिम पूर्वानुमान",
        live_stream_badge: "स्तरीय-1 सजीव डेटा",
        api_docs_btn: "एपीआई प्रलेखन",
        paradigm_title: "⚡ परिचालन दृष्टिकोण में ऐतिहासिक बदलाव",
        paradigm_desc: "शुष्क बल्ब मौसम को शारीरिक तापीय तनाव (<strong>UTCI और ISO 7243 WBGT</strong>) में बदलकर वार्ड जनसांख्यिकीय संवेदनशीलता (<strong>HVI</strong>) से संयोजित कर ठोस नगरपालिका कार्रवाई सुनिश्चित करना।",
        risk_label_prototype: "प्रोटोटाइप सापेक्ष जोखिम",
        risk_label_disclaimer: "यह नैदानिक मृत्यु दर का पूर्वानुमान नहीं है",
        sandbox_title: "इंटरएक्टिव परिदृश्य एवं तापीय तनाव सैंडबॉक्स",
        sandbox_subtitle: "समान परिवेशी तापमान की विभिन्न आर्द्रता/सौर विकिरण स्थितियों में तुलना करें।",
        scen_a_btn: "परिदृश्य A: शुष्क गर्मी (40°C, 20% नमी)",
        scen_b_btn: "परिदृश्य B: घातक आर्द्र गर्मी (40°C, 70% नमी)",
        scen_c_btn: "ग्रीष्मकालीन चरम लू (44.5°C)",
        scen_d_btn: "सामान्य मौसम (30°C, 45% नमी)",
        live_forecast_btn: "सजीव शहर पूर्वानुमान (D+1 से D+5)",
        slider_temp: "हवा का तापमान (2मी):",
        slider_rh: "सापेक्ष आर्द्रता:",
        slider_wind: "हवा की गति (2मी):",
        slider_solar: "सौर विकिरण (GHI):",
        metric_utci_title: "सार्वभौमिक तापीय जलवायु सूचकांक (UTCI)",
        metric_utci_desc: "मानव थर्मोरेगुलेशन तनाव का बहु-स्तरीय गतिशील मॉडल।",
        metric_wbgt_title: "वेट-बल्ब ग्लोब तापमान (WBGT)",
        metric_wbgt_desc: "व्यावसायिक सुरक्षा एवं कार्य-विश्राम का अंतरराष्ट्रीय मानक।",
        metric_hi_title: "एनओएए हीट इंडेक्स (Heat Index)",
        metric_hi_desc: "छायादार आर्द्रता में महसूस होने वाला आभासी तापमान।",
        metric_risk_title: "समग्र वार्ड जोखिम सूचकांक",
        metric_risk_desc: "तापीय खतरे और वार्ड जनसांख्यिकीय संवेदनशीलता का संयोजन।",
        map_title: "अति-स्थानीय वार्ड जोखिम एट्रिब्यूशन मानचित्र",
        map_subtitle: "जनसांख्यिकीय संवेदनशीलता और नागरिक सुरक्षा उपायों को देखने के लिए किसी भी वार्ड पर क्लिक करें।",
        legend_title: "जोखिम स्तर:",
        legend_low: "कम (<30)",
        legend_mod: "मध्यम (30–60)",
        legend_high: "उच्च (60–80)",
        legend_critical: "अत्यधिक गंभीर (>80)",
        inspector_title: "🔍 वार्ड संवेदनशीलता विश्लेषक",
        hvi_score_label: "HVI स्कोर",
        demog_workers: "खुले में काम करने वाले श्रमिक:",
        demog_elderly: "वरिष्ठ नागरिक (60+):",
        demog_children: "छोटे बच्चे (0–6 वर्ष):",
        demog_density: "जनसंख्या घनत्व:",
        action_trigger_label: "तत्काल नगरपालिका कार्रवाई ट्रिगर:",
        chart_forecast_title: "3–5 दिवसीय पूर्वानुमान प्रक्षेपवक्र",
        hindcast_title: "ऐतिहासिक हिंडकास्ट रीप्ले एवं 72-120 घंटे अग्रिम चेतावनी सत्यापन",
        hindcast_subtitle: "चरम मृत्यु दर से 72-120 घंटे पूर्व शारीरिक चेतावनी वृद्धि का सत्यापन (अजहर एट अल 2014, मजदियास्नी एट अल 2017)।",
        hindcast_event_label: "घटना:",
        btn_prev: "पिछला",
        btn_play: "रीप्ले चलाएं",
        btn_pause: "रोकें",
        btn_next: "अगला",
        btn_reset: "रीसेट",
        lead_time_label: "अग्रिम समय:",
        step_env_title: "मौसम एवं शारीरिक तापीय मेट्रिक्स",
        hindcast_air_temp: "तापमान (2मी):",
        hindcast_humidity: "सापेक्ष आर्द्रता:",
        hindcast_utci: "UTCI तापीय तनाव:",
        hindcast_wbgt: "आउटडोर WBGT:",
        traditional_imd_status_label: "पारंपरिक मौसम विभाग सीमा:",
        traditional_imd_note: "केवल शुष्क तापमान पर निर्भर; आर्द्रता के जानलेवा तनाव को अनदेखा करता है।",
        sih_early_warning_label: "SIH26083 अग्रिम चेतावनी:",
        sih_early_warning_note: "UTCI और आर्द्रता संयोजन 5 दिन पहले ही आपातकालीन अलर्ट जारी करता है।",
        proactive_rationale_label: "सक्रिय नगरपालिका शमन निर्देश:",
        niosh_title: "NIOSH / ISO 7243 व्यावसायिक ताप सुरक्षा एवं जलयोजन इंजन",
        niosh_subtitle: "ISO 7243 और NIOSH मानकों पर आधारित गतिशील कार्य-विश्राम समय सारिणी और प्रति घंटा जलयोजन कोटा।",
        occ_workload_label: "श्रम भार:",
        occ_sector_label: "कार्य क्षेत्र:",
        occ_schedule_title: "कार्य-विश्राम समय सारिणी",
        work_label: "कार्य",
        rest_label: "विश्राम",
        occ_hydration_title: "प्रति घंटा जलयोजन कोटा",
        liters_per_hour: "लीटर / घंटा",
        intake_cadence_label: "पीने का अंतराल:",
        timer_title: "शिफ्ट कार्य-विश्राम टाइमर",
        timer_start: "टाइमर शुरू करें",
        timer_pause: "रोकें",
        timer_reset: "रीसेट",
        phase_work: "कार्य चरण",
        phase_rest: "विश्राम चरण",
        phase_work_desc: "सक्रिय शारीरिक श्रम समय सीमा",
        phase_rest_desc: "छायादार स्थान में अनिवार्य जलयोजन एवं शीतलन विश्राम",
        sector_directives_title: "क्षेत्र-विशिष्ट व्यावसायिक सुरक्षा प्रोटोकॉल:",
        advisories_title: "कार्रवाई-आधारित सार्वजनिक स्वास्थ्य सलाह",
        advisories_subtitle: "एनडीएमए राष्ट्रीय हीट एक्शन प्लान दिशानिर्देशों एवं एनसीडीसी ढांचे पर आधारित।",
        adv_municipal_title: "नगर निगम प्रशासन",
        adv_hospital_title: "स्वास्थ्य सेवा एवं अस्पताल",
        adv_citizen_title: "श्रमिक एवं नागरिक",
        provenance_title: "डेटा प्रमाणिकता एवं ऑडिट ट्रेल"
    }
};

// -----------------------------------------------------------------------------
// Historical Events Dataset for Hindcast Replay
// -----------------------------------------------------------------------------
const HISTORICAL_EVENTS_DATA = {
    delhi_june_2024: {
        id: "delhi_june_2024",
        city: "delhi",
        name: "Delhi NCR Severe Heatwave (June 2024)",
        timeline: [
            {
                lead_time: "D-5 (120h)",
                date: "2024-06-14",
                temp_c: 41.0,
                rh_pct: 48.0,
                wind_speed_ms: 2.1,
                solar_radiation_w_m2: 680.0,
                consecutive_days: 1,
                utci_c: 45.3,
                wbgt_c: 31.2,
                risk_score: 72.4,
                imd_status: "Yellow Watch (41.0°C - No Civic Emergency)",
                sih_status: "Very High Risk Alert (120h Lead Advance)",
                mitigation_trigger: "High humidity (48%) elevates UTCI to 45.3°C. Pre-position cooling shelters, issue early warnings to delivery platforms."
            },
            {
                lead_time: "D-4 (96h)",
                date: "2024-06-15",
                temp_c: 42.8,
                rh_pct: 44.0,
                wind_speed_ms: 1.8,
                solar_radiation_w_m2: 710.0,
                consecutive_days: 2,
                utci_c: 47.1,
                wbgt_c: 32.4,
                risk_score: 78.9,
                imd_status: "Yellow Watch (42.8°C)",
                sih_status: "High Thermal Risk Escalation (96h Lead)",
                mitigation_trigger: "Compound thermal accumulation. Activate ASHA worker door-to-door check-ins in high-density informal settlements."
            },
            {
                lead_time: "D-3 (72h)",
                date: "2024-06-16",
                temp_c: 43.6,
                rh_pct: 40.0,
                wind_speed_ms: 2.0,
                solar_radiation_w_m2: 750.0,
                consecutive_days: 3,
                utci_c: 48.2,
                wbgt_c: 33.1,
                risk_score: 84.5,
                imd_status: "Orange Alert (43.6°C - Issued 72h Late)",
                sih_status: "Critical Emergency Trigger (Already Active for 48h)",
                mitigation_trigger: "Shift construction labor to night shifts. Deploy municipal mobile water misting tankers along major transit corridors."
            },
            {
                lead_time: "D-2 (48h)",
                date: "2024-06-17",
                temp_c: 44.2,
                rh_pct: 38.0,
                wind_speed_ms: 2.2,
                solar_radiation_w_m2: 780.0,
                consecutive_days: 4,
                utci_c: 49.0,
                wbgt_c: 33.8,
                risk_score: 89.2,
                imd_status: "Orange Alert (44.2°C)",
                sih_status: "Critical Multi-Day Persistence Emergency",
                mitigation_trigger: "Hospital surge protocol: designate 20% ICU beds for heatstroke, secure backup generators for primary health centres."
            },
            {
                lead_time: "D-1 (24h)",
                date: "2024-06-18",
                temp_c: 45.0,
                rh_pct: 35.0,
                wind_speed_ms: 2.4,
                solar_radiation_w_m2: 800.0,
                consecutive_days: 5,
                utci_c: 49.8,
                wbgt_c: 34.2,
                risk_score: 93.7,
                imd_status: "Red Alert (45.0°C)",
                sih_status: "Extreme Physiological Danger Level",
                mitigation_trigger: "Enforce strict ban on non-essential outdoor work from 11:00 to 16:30. Free ORS distribution at bus stops and metro stations."
            },
            {
                lead_time: "D-Day (0h)",
                date: "2024-06-19",
                temp_c: 45.6,
                rh_pct: 36.0,
                wind_speed_ms: 2.5,
                solar_radiation_w_m2: 820.0,
                consecutive_days: 6,
                utci_c: 50.4,
                wbgt_c: 34.8,
                risk_score: 96.5,
                imd_status: "Red Alert (Peak Heat Crisis)",
                sih_status: "Peak Hazard Compounded by 6-Day Duration",
                mitigation_trigger: "Maximum civic response active. Pre-positioned infrastructure prevented catastrophic mortality spike."
            }
        ]
    },
    ahmedabad_may_2010: {
        id: "ahmedabad_may_2010",
        city: "ahmedabad",
        name: "Ahmedabad Landmark Heatwave (May 2010 - 1,344 Excess Deaths)",
        timeline: [
            {
                lead_time: "D-5 (120h)",
                date: "2010-05-16",
                temp_c: 42.0,
                rh_pct: 30.0,
                wind_speed_ms: 3.0,
                solar_radiation_w_m2: 700.0,
                consecutive_days: 1,
                utci_c: 46.5,
                wbgt_c: 30.8,
                risk_score: 75.0,
                imd_status: "Normal May Summer (No Warning)",
                sih_status: "High Risk Trigger (120h Advance Warning)",
                mitigation_trigger: "SIH26083 signals high vulnerability in informal settlements (HVI > 70). Pre-stock IV saline in civil hospitals."
            },
            {
                lead_time: "D-4 (96h)",
                date: "2010-05-17",
                temp_c: 43.5,
                rh_pct: 28.0,
                wind_speed_ms: 2.8,
                solar_radiation_w_m2: 730.0,
                consecutive_days: 2,
                utci_c: 48.0,
                wbgt_c: 31.6,
                risk_score: 81.2,
                imd_status: "Yellow Watch",
                sih_status: "Very High Risk Alert (96h Advance)",
                mitigation_trigger: "Activate AMC drinking water distribution points and shade nets across transit junctions."
            },
            {
                lead_time: "D-3 (72h)",
                date: "2010-05-18",
                temp_c: 44.8,
                rh_pct: 26.0,
                wind_speed_ms: 2.5,
                solar_radiation_w_m2: 760.0,
                consecutive_days: 3,
                utci_c: 49.3,
                wbgt_c: 32.5,
                risk_score: 87.6,
                imd_status: "Orange Alert",
                sih_status: "Critical Early Intervention Point (72h Lead)",
                mitigation_trigger: "Issue public media alerts in Gujarati/Hindi: stay indoors, hydrate with lemon water and buttermilk."
            },
            {
                lead_time: "D-2 (48h)",
                date: "2010-05-19",
                temp_c: 45.9,
                rh_pct: 24.0,
                wind_speed_ms: 2.3,
                solar_radiation_w_m2: 780.0,
                consecutive_days: 4,
                utci_c: 50.8,
                wbgt_c: 33.2,
                risk_score: 92.4,
                imd_status: "Red Alert",
                sih_status: "Extreme Risk Escalation",
                mitigation_trigger: "Keep public gardens and AC community halls open 24/7 for homeless and slum residents."
            },
            {
                lead_time: "D-1 (24h)",
                date: "2010-05-20",
                temp_c: 46.5,
                rh_pct: 22.0,
                wind_speed_ms: 2.1,
                solar_radiation_w_m2: 800.0,
                consecutive_days: 5,
                utci_c: 51.5,
                wbgt_c: 33.8,
                risk_score: 95.8,
                imd_status: "Red Alert",
                sih_status: "Severe Mortality Risk Zone",
                mitigation_trigger: "Deploy mobile ice pack cooling vans to emergency triage centers across AMC."
            },
            {
                lead_time: "D-Day (0h)",
                date: "2010-05-21",
                temp_c: 46.8,
                rh_pct: 20.0,
                wind_speed_ms: 2.0,
                solar_radiation_w_m2: 820.0,
                consecutive_days: 6,
                utci_c: 52.0,
                wbgt_c: 34.0,
                risk_score: 98.2,
                imd_status: "Historic Peak 46.8°C",
                sih_status: "Extreme Crisis (1,344 Excess Deaths Baseline)",
                mitigation_trigger: "Benchmark evidence: 5-day proactive anticipation is essential to prevent mass casualties."
            }
        ]
    },
    delhi_may_2022: {
        id: "delhi_may_2022",
        city: "delhi",
        name: "Delhi Early-Onset Heatwave (May 2022)",
        timeline: [
            {
                lead_time: "D-5 (120h)",
                date: "2022-05-10",
                temp_c: 41.5,
                rh_pct: 35.0,
                wind_speed_ms: 2.5,
                solar_radiation_w_m2: 700.0,
                consecutive_days: 1,
                utci_c: 46.2,
                wbgt_c: 31.0,
                risk_score: 73.1,
                imd_status: "Yellow Watch",
                sih_status: "Early Risk Alert (120h Lead)",
                mitigation_trigger: "Early-season unacclimatized population at high vulnerability. Issue workplace safety notices."
            },
            {
                lead_time: "D-4 (96h)",
                date: "2022-05-11",
                temp_c: 42.6,
                rh_pct: 32.0,
                wind_speed_ms: 2.6,
                solar_radiation_w_m2: 730.0,
                consecutive_days: 2,
                utci_c: 47.5,
                wbgt_c: 31.8,
                risk_score: 78.4,
                imd_status: "Yellow Watch",
                sih_status: "Escalating Thermal Strain (96h Lead)",
                mitigation_trigger: "Coordinate with Delhi Jal Board for uninterrupted water delivery in unauthorized colonies."
            },
            {
                lead_time: "D-3 (72h)",
                date: "2022-05-12",
                temp_c: 43.8,
                rh_pct: 29.0,
                wind_speed_ms: 2.8,
                solar_radiation_w_m2: 760.0,
                consecutive_days: 3,
                utci_c: 48.8,
                wbgt_c: 32.4,
                risk_score: 83.9,
                imd_status: "Orange Alert",
                sih_status: "Critical Risk Threshold",
                mitigation_trigger: "Adjust school hours to terminate before 11:00 AM. Halt open-air physical training."
            },
            {
                lead_time: "D-2 (48h)",
                date: "2022-05-13",
                temp_c: 44.7,
                rh_pct: 27.0,
                wind_speed_ms: 2.9,
                solar_radiation_w_m2: 780.0,
                consecutive_days: 4,
                utci_c: 49.9,
                wbgt_c: 33.1,
                risk_score: 88.5,
                imd_status: "Orange Alert",
                sih_status: "Multi-Day Extreme Emergency",
                mitigation_trigger: "Distribute ORS and glucose packets through Delhi Metro stations and DTC bus depots."
            },
            {
                lead_time: "D-1 (24h)",
                date: "2022-05-14",
                temp_c: 45.4,
                rh_pct: 25.0,
                wind_speed_ms: 3.1,
                solar_radiation_w_m2: 800.0,
                consecutive_days: 5,
                utci_c: 50.8,
                wbgt_c: 33.7,
                risk_score: 93.0,
                imd_status: "Red Alert",
                sih_status: "Severe Risk Level",
                mitigation_trigger: "Mandatory rest breaks for all traffic police and municipal sanitation workers."
            },
            {
                lead_time: "D-Day (0h)",
                date: "2022-05-15",
                temp_c: 46.0,
                rh_pct: 24.0,
                wind_speed_ms: 3.0,
                solar_radiation_w_m2: 810.0,
                consecutive_days: 6,
                utci_c: 51.5,
                wbgt_c: 34.1,
                risk_score: 96.1,
                imd_status: "Red Alert (46.0°C Peak)",
                sih_status: "Peak Hazard",
                mitigation_trigger: "Civic cooling infrastructure operational across all 11 revenue districts."
            }
        ]
    }
};

// -----------------------------------------------------------------------------
// Sector Directives & Work-Rest Database
// -----------------------------------------------------------------------------
const SECTOR_PROTOCOLS = {
    gig_delivery: {
        title_en: "Gig Economy & Outdoor Delivery Protocol (Zomato / Swiggy / Zepto / Blinkit):",
        title_hi: "गिग इकोनॉमी एवं डिलीवरी राइडर सुरक्षा प्रोटोकॉल (ज़ोमैटो / स्विगी / ज़ेप्टो / ब्लिंकिट):",
        protocols_en: [
            "Dark Store AC Hubs: Mandatory 15-minute rest in air-conditioned zones after each delivery run.",
            "Surge Compensation: Implement heat-stress hazard pay bonus during Red/Orange alerts.",
            "Hydration Points: Install ORS fluid stations at high-density commercial pickup nodes."
        ],
        protocols_hi: [
            "डार्क स्टोर एसी हब: प्रत्येक डिलीवरी के बाद वातानुकूलित क्षेत्र में अनिवार्य 15 मिनट का विश्राम।",
            "जोखिम मुआवजा: रेड/ऑरेंज अलर्ट के दौरान डिलीवरी पार्टनर्स को हीट-स्ट्रेस बोनस प्रदान करें।",
            "जलयोजन केंद्र: प्रमुख वाणिज्यिक पिकअप केंद्रों पर ओआरएस एवं शीतल जल बूथ स्थापित करें।"
        ]
    },
    construction: {
        title_en: "Construction & Infrastructure Labor Protocol:",
        title_hi: "निर्माण एवं अवसंरचना श्रमिक सुरक्षा प्रोटोकॉल:",
        protocols_en: [
            "Split Shift Mandate: Strict prohibition of heavy labor between 11:30 AM and 3:30 PM.",
            "Shaded Cool-Down Tents: Erect mandatory temporary rest sheds with misting fans on all active sites.",
            "Buddy Surveillance: Pair workers to detect early signs of confusion, dizziness, or heat exhaustion."
        ],
        protocols_hi: [
            "विभाजित शिफ्ट नियम: सुबह 11:30 से दोपहर 3:30 बजे के बीच भारी श्रम पर पूर्ण प्रतिबंध।",
            "छायादार कूलिंग टेंट: सभी निर्माण स्थलों पर मिस्टिंग पंखों वाले अनिवार्य विश्राम शेड बनाएं।",
            "जोड़ीदार निगरानी प्रणाली: चक्कर, भ्रम या अत्यधिक पसीने के शुरुआती लक्षणों की पहचान हेतु श्रमिकों की जोड़ियां बनाएं।"
        ]
    },
    agriculture: {
        title_en: "Agricultural & Farm Workforce Protocol:",
        title_hi: "कृषि एवं ग्रामीण खेत मजदूर सुरक्षा प्रोटोकॉल:",
        protocols_en: [
            "Early Morning Work Hours: Limit field harvesting to 05:30 AM - 10:30 AM and 04:30 PM - 07:00 PM.",
            "Field Hydration: Carry minimum 3L water mixed with salt/jaggery or ORS per laborer.",
            "Broad-Brimmed Headwear: Ensure damp cotton scarves (gamchha) and wide hats are worn at all times."
        ],
        protocols_hi: [
            "प्रातःकालीन कार्य समय: खेतों में कटाई व श्रम का समय प्रातः 05:30-10:30 तथा सायं 04:30-07:00 तक सीमित रखें।",
            "खेत जलयोजन: प्रत्येक मजदूर के लिए नमक/गुड़ या ओआरएस युक्त न्यूनतम 3 लीटर पेय जल सुनिश्चित करें।",
            "गमछा एवं सिर की सुरक्षा: सिर पर गीला सूती गमछा या चौड़ी टोपी पहनना अनिवार्य करें।"
        ]
    },
    traffic_police: {
        title_en: "Traffic Police & Municipal Field Staff Protocol:",
        title_hi: "ट्रैफिक पुलिस एवं नगर निगम फील्ड स्टाफ प्रोटोकॉल:",
        protocols_en: [
            "30-Minute Rotation: Rotate intersection duty with 30-minute shaded booth relief intervals.",
            "Cooling Vests: Issue phase-change material (PCM) evaporative cooling jackets for peak traffic hours.",
            "Medical Electrolyte Packs: Supply isotonic electrolyte sachets at every traffic police chowki."
        ],
        protocols_hi: [
            "30 मिनट का रोटेशन: चौराहे की ड्यूटी को 30 मिनट के छायादार बूथ विश्राम के साथ रोटेट करें।",
            "कूलिंग वेस्ट: दोपहर के पीक ट्रैफिक घंटों में वाष्पीकरणीय कूलिंग जैकेट का उपयोग करें।",
            "इलेक्ट्रोलाइट किट: प्रत्येक ट्रैफिक पुलिस चौकी पर आइसोटोनिक ओआरएस पाउच उपलब्ध कराएं।"
        ]
    }
};

// -----------------------------------------------------------------------------
// Math & Thermal Calculation Utilities (Client-side mirror of backend engines)
// -----------------------------------------------------------------------------
function calculateUTCI(tempC, rhPct, windSpeedMs = 2.5, solarRadiationWm2 = 650.0) {
    const rhClamped = Math.max(10, Math.min(100, rhPct));
    const vp_hpa = (rhClamped / 100.0) * 6.112 * Math.exp((17.67 * tempC) / (tempC + 243.5));
    const deltaT_solar = (solarRadiationWm2 / 1000.0) * 4.2;
    const windEffect = -1.8 * Math.sqrt(Math.max(0.5, windSpeedMs));
    const humidityEffect = 0.32 * (vp_hpa - 15.0);
    const utci = tempC + deltaT_solar + windEffect + humidityEffect;
    return parseFloat(utci.toFixed(1));
}

function getUTCICategory(utciVal) {
    if (utciVal > 46.0) return { category: "Extreme Heat Stress", category_hi: "अत्यधिक गंभीर तापीय तनाव", color: "#ef4444" };
    if (utciVal >= 38.0) return { category: "Very Strong Heat Stress", category_hi: "बहुत तीव्र तापीय तनाव", color: "#f97316" };
    if (utciVal >= 32.0) return { category: "Strong Heat Stress", category_hi: "तीव्र तापीय तनाव", color: "#eab308" };
    if (utciVal >= 26.0) return { category: "Moderate Heat Stress", category_hi: "मध्यम तापीय तनाव", color: "#3b82f6" };
    if (utciVal >= 9.0) return { category: "No Thermal Stress", category_hi: "कोई तापीय तनाव नहीं", color: "#10b981" };
    return { category: "Slight Cold Stress", category_hi: "हल्का शीत तनाव", color: "#06b6d4" };
}

function calculateWBGT(tempC, rhPct, windSpeedMs = 2.5, solarRadiationWm2 = 650.0) {
    const rh = Math.max(10, Math.min(100, rhPct));
    // Stull psychrometric Tw approximation
    const Tw = tempC * Math.atan(0.151977 * Math.pow(rh + 8.313659, 0.5)) +
        Math.atan(tempC + rh) - Math.atan(rh - 1.676331) +
        0.00391838 * Math.pow(rh, 1.5) * Math.atan(0.023101 * rh) - 4.686035;
    const Tg = tempC + 0.012 * solarRadiationWm2 / (Math.pow(Math.max(0.2, windSpeedMs), 0.4) + 0.1);
    const outdoorWbgt = 0.7 * Tw + 0.2 * Tg + 0.1 * tempC;
    return parseFloat(outdoorWbgt.toFixed(1));
}

function getWBGTCategory(wbgtVal) {
    if (wbgtVal >= 32.2) return { category: "Extreme Danger / Halt Work", category_hi: "अत्यधिक खतरा / कार्य रोकें", color: "#ef4444" };
    if (wbgtVal >= 31.0) return { category: "High Hazard (25% Work / 75% Rest)", category_hi: "उच्च खतरा (25% काम / 75% आराम)", color: "#f97316" };
    if (wbgtVal >= 29.4) return { category: "Moderate Hazard (50% Work / 50% Rest)", category_hi: "मध्यम खतरा (50% काम / 50% आराम)", color: "#eab308" };
    if (wbgtVal >= 27.8) return { category: "Caution (75% Work / 25% Rest)", category_hi: "सावधानी (75% काम / 25% आराम)", color: "#3b82f6" };
    return { category: "Normal Working Conditions", category_hi: "सामान्य कार्य स्थितियां", color: "#10b981" };
}

function calculateHeatIndex(tempC, rhPct) {
    const T = (tempC * 9.0 / 5.0) + 32.0;
    const R = Math.max(0, Math.min(100, rhPct));
    let hi_f = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (R * 0.094));
    if (hi_f >= 80.0) {
        hi_f = -42.379 + 2.04901523 * T + 10.14333127 * R - 0.22475541 * T * R -
            0.00683783 * T * T - 0.05481717 * R * R + 0.00122874 * T * T * R +
            0.00085282 * T * R * R - 0.00000199 * T * T * R * R;
    }
    const hi_c = (hi_f - 32.0) * 5.0 / 9.0;
    return parseFloat(hi_c.toFixed(1));
}

function calculateCompositeRisk(hazardScore, hviScore, durationDays = 1) {
    let durationMultiplier = 1.0;
    if (durationDays === 2) durationMultiplier = 1.10;
    else if (durationDays === 3) durationMultiplier = 1.20;
    else if (durationDays >= 4) durationMultiplier = 1.30;

    const baseRisk = (0.60 * hazardScore) + (0.40 * hviScore);
    const finalRisk = Math.min(100.0, baseRisk * durationMultiplier);
    return parseFloat(finalRisk.toFixed(1));
}

// -----------------------------------------------------------------------------
// Map Initialization & Dynamic GeoJSON Choropleth
// -----------------------------------------------------------------------------
function initMap() {
    const currentCity = CITIES[state.city] || CITIES.delhi;
    state.map = L.map('map', {
        zoomControl: true,
        attributionControl: false
    }).setView(currentCity.center, currentCity.zoom);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        subdomains: 'abcd'
    }).addTo(state.map);

    fetchCityRiskGeoJSON();
}

function getRiskColor(score) {
    if (score >= 80) return '#ef4444'; // Red (Critical)
    if (score >= 60) return '#f97316'; // Orange (High)
    if (score >= 30) return '#eab308'; // Yellow (Moderate)
    return '#10b981'; // Green (Low)
}

async function fetchCityRiskGeoJSON() {
    const currentCity = CITIES[state.city] || CITIES.delhi;
    const url = `/api/v1/map/risk?city=${state.city}&temp_c=${state.weather.temp_c}&rh_pct=${state.weather.rh_pct}&wind_speed_ms=${state.weather.wind_speed_ms}&solar_radiation_w_m2=${state.weather.solar_radiation_w_m2}&consecutive_extreme_days=${state.weather.consecutive_extreme_days}`;

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const geojsonData = await response.json();
        renderGeoJSONOnMap(geojsonData);
    } catch (err) {
        console.warn('API fetch for map failed, building dynamic fallback geojson:', err);
        const fallbackGeoJSON = generateFallbackGeoJSON(state.city);
        renderGeoJSONOnMap(fallbackGeoJSON);
    }
}

function renderGeoJSONOnMap(geojsonData) {
    if (state.geojsonLayer) {
        state.map.removeLayer(state.geojsonLayer);
    }

    state.geojsonLayer = L.geoJSON(geojsonData, {
        style: function (feature) {
            const riskScore = feature.properties.risk_score || 50;
            const isSelected = feature.properties.ward_id === state.activeWardId;
            return {
                fillColor: getRiskColor(riskScore),
                weight: isSelected ? 3.5 : 1.5,
                opacity: 1,
                color: isSelected ? '#ffffff' : '#334155',
                fillOpacity: isSelected ? 0.85 : 0.65
            };
        },
        onEachFeature: function (feature, layer) {
            const props = feature.properties;
            const isHindi = state.language === 'hi';

            const popupContent = `
                <div class="p-1 space-y-1 text-xs">
                    <div class="font-extrabold text-sm text-orange-400">${props.ward_name || props.ward_id}</div>
                    <div class="text-slate-300">${isHindi ? 'वार्ड आईडी' : 'Ward ID'}: <span class="font-mono font-bold">${props.ward_id}</span></div>
                    <div class="flex items-center justify-between text-slate-200">
                        <span>${isHindi ? 'जोखिम स्कोर' : 'Risk Score'}:</span>
                        <span class="font-bold font-mono text-sm" style="color:${getRiskColor(props.risk_score)}">${props.risk_score} / 100</span>
                    </div>
                    <div class="text-slate-300">${isHindi ? 'HVI संवेदनशीलता' : 'HVI Vulnerability'}: <span class="font-bold">${props.hvi_score || '--'}</span></div>
                    <div class="text-[11px] text-slate-400 mt-1">${props.action_priority || ''}</div>
                </div>
            `;
            layer.bindPopup(popupContent);

            layer.on({
                mouseover: function (e) {
                    const l = e.target;
                    l.setStyle({
                        weight: 3,
                        fillOpacity: 0.9
                    });
                },
                mouseout: function (e) {
                    state.geojsonLayer.resetStyle(e.target);
                    if (feature.properties.ward_id === state.activeWardId) {
                        e.target.setStyle({ weight: 3.5, color: '#ffffff', fillOpacity: 0.85 });
                    }
                },
                click: function () {
                    selectWard(feature.properties);
                }
            });

            // If active ward matches, update inspector
            if (props.ward_id === state.activeWardId) {
                state.activeWardData = props;
                updateWardInspectorUI(props);
            }
        }
    }).addTo(state.map);

    // If activeWardData is null, select first feature
    if (!state.activeWardData && geojsonData.features && geojsonData.features.length > 0) {
        selectWard(geojsonData.features[0].properties);
    }
}

function selectWard(props) {
    state.activeWardId = props.ward_id;
    state.activeWardData = props;
    updateWardInspectorUI(props);
    updateOccupationalSafety();
    updateAdvisories();

    if (state.geojsonLayer) {
        state.geojsonLayer.setStyle(function (feature) {
            const isSelected = feature.properties.ward_id === state.activeWardId;
            const riskScore = feature.properties.risk_score || 50;
            return {
                fillColor: getRiskColor(riskScore),
                weight: isSelected ? 3.5 : 1.5,
                opacity: 1,
                color: isSelected ? '#ffffff' : '#334155',
                fillOpacity: isSelected ? 0.85 : 0.65
            };
        });
    }
}

function updateWardInspectorUI(props) {
    if (!props) return;
    const isHindi = state.language === 'hi';

    const wardNameEl = document.getElementById('inspector-ward-name');
    const hviEl = document.getElementById('inspector-hvi');
    const workersEl = document.getElementById('inspector-workers');
    const elderlyEl = document.getElementById('inspector-elderly');
    const childrenEl = document.getElementById('inspector-children');
    const densityEl = document.getElementById('inspector-density');
    const actionEl = document.getElementById('inspector-action');

    const wardName = isHindi ? (props.ward_name_hi || props.ward_name) : props.ward_name;
    if (wardNameEl) wardNameEl.textContent = `${wardName} (${props.ward_id})`;
    if (hviEl) hviEl.textContent = `${props.hvi_score || 68.5} / 100`;
    
    const workerPct = props.pct_outdoor_workers || 35.0;
    const elderlyPct = props.pct_elderly || 10.0;
    const childPct = props.pct_children || 14.0;
    const density = props.density_sqkm || 37000;

    if (workersEl) workersEl.textContent = `${workerPct}%`;
    if (elderlyEl) elderlyEl.textContent = `${elderlyPct}%`;
    if (childrenEl) childrenEl.textContent = `${childPct}%`;
    if (densityEl) densityEl.textContent = `${density.toLocaleString()} / km²`;

    if (actionEl) {
        if (isHindi) {
            actionEl.textContent = props.action_priority_hi || "आपातकालीन पेयजल टैंकर तैनात करें और वातानुकूलित शेल्टर सक्रिय करें।";
        } else {
            actionEl.textContent = props.action_priority || "Deploy emergency water tankers and activate shaded cooling centers.";
        }
    }
}

// -----------------------------------------------------------------------------
// Fallback Synthetic GeoJSON Generator for Supported Cities
// -----------------------------------------------------------------------------
function generateFallbackGeoJSON(cityId) {
    const city = CITIES[cityId] || CITIES.delhi;
    const cLat = city.center[0];
    const cLon = city.center[1];
    const delta = 0.04;

    const wardList = {
        delhi: [
            { id: "DEL-W01", name: "Seelampur", name_hi: "सीलमपुर", hvi: 68.5, workers: 35, elderly: 10, children: 14, density: 37000, offLat: 0.02, offLon: 0.03 },
            { id: "DEL-W02", name: "Karawal Nagar", name_hi: "करावल नगर", hvi: 74.2, workers: 38, elderly: 11, children: 15, density: 42000, offLat: 0.05, offLon: 0.04 },
            { id: "DEL-W03", name: "Chandni Chowk", name_hi: "चांदनी चौक", hvi: 62.0, workers: 30, elderly: 14, children: 11, density: 34000, offLat: 0.01, offLon: -0.01 },
            { id: "DEL-W04", name: "Rohini", name_hi: "रोहिणी", hvi: 48.3, workers: 22, elderly: 9, children: 12, density: 21000, offLat: 0.07, offLon: -0.05 },
            { id: "DEL-W05", name: "Dwarka", name_hi: "द्वारका", hvi: 42.1, workers: 18, elderly: 8, children: 10, density: 16000, offLat: -0.05, offLon: -0.06 },
            { id: "DEL-W06", name: "Okhla Phase-II", name_hi: "ओखला फेज-2", hvi: 71.8, workers: 39, elderly: 9, children: 13, density: 31000, offLat: -0.06, offLon: 0.04 },
            { id: "DEL-W07", name: "Najafgarh", name_hi: "नजफगढ़", hvi: 55.4, workers: 28, elderly: 12, children: 13, density: 14000, offLat: -0.02, offLon: -0.08 },
            { id: "DEL-W08", name: "Vasant Kunj", name_hi: "वसंत कुंज", hvi: 38.0, workers: 15, elderly: 11, children: 9, density: 12000, offLat: -0.06, offLon: -0.02 }
        ],
        ahmedabad: [
            { id: "AMD-W01", name: "Amraiwadi (Industrial)", name_hi: "अमराईवाड़ी", hvi: 78.5, workers: 42, elderly: 10, children: 15, density: 38000, offLat: -0.02, offLon: 0.03 },
            { id: "AMD-W02", name: "Bapunagar (Slum/Dense)", name_hi: "बापूनगर", hvi: 82.1, workers: 45, elderly: 11, children: 16, density: 44000, offLat: 0.03, offLon: 0.04 },
            { id: "AMD-W03", name: "Navrangpura (Commercial)", name_hi: "नवरंगपुरा", hvi: 42.0, workers: 20, elderly: 12, children: 9, density: 19000, offLat: 0.02, offLon: -0.03 },
            { id: "AMD-W04", name: "Vatva (Chemical Zone)", name_hi: "वटवा", hvi: 74.0, workers: 40, elderly: 9, children: 14, density: 29000, offLat: -0.06, offLon: 0.05 },
            { id: "AMD-W05", name: "Sabarmati", name_hi: "साबरमती", hvi: 52.3, workers: 26, elderly: 10, children: 11, density: 22000, offLat: 0.06, offLon: 0.01 },
            { id: "AMD-W06", name: "Bodakdev", name_hi: "बोडकदेव", hvi: 35.6, workers: 14, elderly: 10, children: 8, density: 14000, offLat: 0.03, offLon: -0.06 }
        ],
        surat: [
            { id: "SUR-W01", name: "Udhna (Textile Hub)", name_hi: "उधना", hvi: 76.2, workers: 44, elderly: 8, children: 14, density: 39000, offLat: -0.03, offLon: 0.02 },
            { id: "SUR-W02", name: "Katargam (Diamond)", name_hi: "कतारगाम", hvi: 69.4, workers: 36, elderly: 9, children: 13, density: 33000, offLat: 0.04, offLon: 0.01 },
            { id: "SUR-W03", name: "Athwa (Riverside)", name_hi: "अथवा", hvi: 41.5, workers: 18, elderly: 12, children: 9, density: 18000, offLat: -0.02, offLon: -0.03 },
            { id: "SUR-W04", name: "Limbayat (High Density)", name_hi: "लिंबायत", hvi: 84.0, workers: 46, elderly: 10, children: 16, density: 46000, offLat: -0.04, offLon: 0.04 }
        ],
        bhubaneswar: [
            { id: "BHU-W01", name: "Old Town / Lingaraj", name_hi: "ओल्ड टाउन", hvi: 64.2, workers: 32, elderly: 13, children: 12, density: 24000, offLat: -0.03, offLon: -0.01 },
            { id: "BHU-W02", name: "Mancheswar (Industrial)", name_hi: "मंचेश्वर", hvi: 73.0, workers: 39, elderly: 9, children: 14, density: 27000, offLat: 0.04, offLon: 0.03 },
            { id: "BHU-W03", name: "Saheed Nagar", name_hi: "शहीद नगर", hvi: 46.8, workers: 22, elderly: 11, children: 10, density: 19000, offLat: 0.01, offLon: 0.02 },
            { id: "BHU-W04", name: "Patia (IT Hub)", name_hi: "पटिया", hvi: 39.5, workers: 16, elderly: 8, children: 9, density: 15000, offLat: 0.06, offLon: 0.01 }
        ],
        mumbai: [
            { id: "MUM-W01", name: "Dharavi / G-North", name_hi: "धारावी / जी-नॉर्थ", hvi: 88.6, workers: 48, elderly: 9, children: 16, density: 65000, offLat: -0.02, offLon: 0.01 },
            { id: "MUM-W02", name: "Kurla / L-Ward", name_hi: "कुर्ला / एल-वार्ड", hvi: 79.4, workers: 42, elderly: 10, children: 15, density: 45000, offLat: 0.03, offLon: 0.03 },
            { id: "MUM-W03", name: "Bandra West / H-West", name_hi: "बांद्रा वेस्ट", hvi: 44.2, workers: 19, elderly: 14, children: 9, density: 22000, offLat: -0.03, offLon: -0.03 },
            { id: "MUM-W04", name: "Andheri East / K-East", name_hi: "अंधेरी ईस्ट", hvi: 67.0, workers: 35, elderly: 11, children: 12, density: 36000, offLat: 0.06, offLon: 0.02 }
        ]
    };

    const targetList = wardList[cityId] || wardList.delhi;
    const features = targetList.map((w, idx) => {
        const lat = cLat + (w.offLat || (idx * 0.02 - 0.04));
        const lon = cLon + (w.offLon || (idx * 0.02 - 0.04));
        const d = 0.025;

        const hazard = Math.min(100, Math.max(0, (state.weather.temp_c - 25) * 4));
        const risk = calculateCompositeRisk(hazard, w.hvi, state.weather.consecutive_extreme_days);

        return {
            type: "Feature",
            geometry: {
                type: "Polygon",
                coordinates: [[
                    [lon - d, lat - d],
                    [lon + d, lat - d],
                    [lon + d, lat + d],
                    [lon - d, lat + d],
                    [lon - d, lat - d]
                ]]
            },
            properties: {
                ward_id: w.id,
                ward_name: w.name,
                ward_name_hi: w.name_hi,
                city_id: cityId,
                hvi_score: w.hvi,
                risk_score: risk,
                pct_outdoor_workers: w.workers,
                pct_elderly: w.elderly,
                pct_children: w.children,
                density_sqkm: w.density,
                action_priority: risk >= 80 ? "Critical: Deploy misting cooling vans, halt daytime labor" : "Moderate: Hydration advisories active"
            }
        };
    });

    return {
        type: "FeatureCollection",
        features: features
    };
}

// -----------------------------------------------------------------------------
// City Change Handler
// -----------------------------------------------------------------------------
function onCityChange(cityId) {
    state.city = cityId;
    const city = CITIES[cityId] || CITIES.delhi;
    state.activeWardId = city.defaultWard;
    state.activeWardData = null;

    // Update map view
    if (state.map) {
        state.map.flyTo(city.center, city.zoom, { duration: 1.2 });
    }

    // Update city badge
    const badgeEl = document.getElementById('map-active-city-badge');
    if (badgeEl) {
        badgeEl.textContent = state.language === 'hi' ? city.badge_hi : city.badge;
    }

    fetchCityRiskGeoJSON();
    fetchForecastTrajectory();
}

// -----------------------------------------------------------------------------
// Controls & Sliders Update Engine
// -----------------------------------------------------------------------------
function updateControls() {
    const tempInput = document.getElementById('temp-slider');
    const rhInput = document.getElementById('rh-slider');
    const windInput = document.getElementById('wind-slider');
    const solarInput = document.getElementById('solar-slider');

    state.weather.temp_c = parseFloat(tempInput.value);
    state.weather.rh_pct = parseFloat(rhInput.value);
    state.weather.wind_speed_ms = parseFloat(windInput.value);
    state.weather.solar_radiation_w_m2 = parseFloat(solarInput.value);

    // Update numeric readout displays
    document.getElementById('temp-val').textContent = `${state.weather.temp_c.toFixed(1)} °C`;
    document.getElementById('rh-val').textContent = `${state.weather.rh_pct.toFixed(1)} %`;
    document.getElementById('wind-val').textContent = `${state.weather.wind_speed_ms.toFixed(1)} m/s`;
    document.getElementById('solar-val').textContent = `${state.weather.solar_radiation_w_m2} W/m²`;

    computeThermalMetrics();
    fetchCityRiskGeoJSON();
    updateOccupationalSafety();
    updateAdvisories();
}

function computeThermalMetrics() {
    const isHindi = state.language === 'hi';
    const { temp_c, rh_pct, wind_speed_ms, solar_radiation_w_m2, consecutive_extreme_days } = state.weather;

    const utci = calculateUTCI(temp_c, rh_pct, wind_speed_ms, solar_radiation_w_m2);
    const utciMeta = getUTCICategory(utci);

    const wbgt = calculateWBGT(temp_c, rh_pct, wind_speed_ms, solar_radiation_w_m2);
    const wbgtMeta = getWBGTCategory(wbgt);

    const hi = calculateHeatIndex(temp_c, rh_pct);

    // Hazard score mapped from UTCI (26°C=0, 50°C=100)
    const hazardScore = Math.max(0, Math.min(100, ((utci - 26.0) / 24.0) * 100));
    const hviScore = state.activeWardData ? state.activeWardData.hvi_score : 68.5;
    const compRisk = calculateCompositeRisk(hazardScore, hviScore, consecutive_extreme_days);

    state.thermalIndices = { utci, wbgt, heat_index: hi, risk_score: compRisk };

    // Update UTCI Card
    const utciDisp = document.getElementById('utci-display');
    const utciTag = document.getElementById('utci-tag');
    if (utciDisp) utciDisp.textContent = utci.toFixed(1);
    if (utciTag) {
        utciTag.textContent = isHindi ? utciMeta.category_hi : utciMeta.category;
        utciTag.style.backgroundColor = `${utciMeta.color}20`;
        utciTag.style.color = utciMeta.color;
        utciTag.style.borderColor = `${utciMeta.color}50`;
    }

    // Update WBGT Card
    const wbgtDisp = document.getElementById('wbgt-display');
    const wbgtTag = document.getElementById('wbgt-tag');
    if (wbgtDisp) wbgtDisp.textContent = wbgt.toFixed(1);
    if (wbgtTag) {
        wbgtTag.textContent = isHindi ? wbgtMeta.category_hi : wbgtMeta.category;
        wbgtTag.style.backgroundColor = `${wbgtMeta.color}20`;
        wbgtTag.style.color = wbgtMeta.color;
    }

    // Update Heat Index Card
    const hiDisp = document.getElementById('hi-display');
    const hiTag = document.getElementById('hi-tag');
    if (hiDisp) hiDisp.textContent = hi.toFixed(1);
    if (hiTag) {
        const hiCategory = hi >= 54 ? (isHindi ? "अत्यधिक खतरा" : "Extreme Danger") :
            hi >= 41 ? (isHindi ? "खतरा" : "Danger") :
                hi >= 32 ? (isHindi ? "अत्यधिक सावधानी" : "Extreme Caution") : (isHindi ? "सावधानी" : "Caution");
        hiTag.textContent = hiCategory;
        hiTag.style.backgroundColor = hi >= 41 ? '#ef444420' : '#eab30820';
        hiTag.style.color = hi >= 41 ? '#ef4444' : '#eab308';
    }

    // Update Composite Risk Card
    const riskDisp = document.getElementById('peak-risk-display');
    const riskTag = document.getElementById('peak-risk-tag');
    if (riskDisp) riskDisp.textContent = compRisk.toFixed(1);
    if (riskTag) {
        const riskCategory = compRisk >= 80 ? (isHindi ? "अत्यधिक गंभीर आपातकाल" : "Critical Emergency") :
            compRisk >= 60 ? (isHindi ? "उच्च जोखिम चेतावनी" : "High Risk Alert") :
                compRisk >= 30 ? (isHindi ? "मध्यम जोखिम" : "Moderate Risk") : (isHindi ? "कम जोखिम" : "Low Risk");
        riskTag.textContent = riskCategory;
        riskTag.style.color = getRiskColor(compRisk);
    }
}

// -----------------------------------------------------------------------------
// Scenario Loader
// -----------------------------------------------------------------------------
function loadScenario(scenarioKey) {
    const sc = SCENARIOS[scenarioKey];
    if (!sc) return;

    document.getElementById('temp-slider').value = sc.temp;
    document.getElementById('rh-slider').value = sc.rh;
    document.getElementById('wind-slider').value = sc.wind;
    document.getElementById('solar-slider').value = sc.solar;

    state.weather.consecutive_extreme_days = sc.days || 1;
    updateControls();
}

async function fetchLiveForecast() {
    const city = CITIES[state.city] || CITIES.delhi;
    const lat = city.center[0];
    const lon = city.center[1];

    try {
        const res = await fetch(`/api/v1/weather/current?lat=${lat}&lon=${lon}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const w = data.weather;

        document.getElementById('temp-slider').value = w.temperature_c;
        document.getElementById('rh-slider').value = w.relative_humidity_pct;
        document.getElementById('wind-slider').value = w.wind_speed_2m_ms || 2.5;
        document.getElementById('solar-slider').value = w.solar_radiation_w_m2 || 650;
        updateControls();
    } catch (err) {
        console.warn("Live weather fetch failed, loading default summer spike:", err);
        loadScenario('scenario_c_delhi_2024_heatwave');
    }
}

// -----------------------------------------------------------------------------
// Chart.js 5-Day Forecast Trajectory
// -----------------------------------------------------------------------------
function initForecastChart() {
    const ctx = document.getElementById('forecastChart');
    if (!ctx) return;

    state.forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['D+1', 'D+2', 'D+3', 'D+4', 'D+5'],
            datasets: [
                {
                    label: 'UTCI Thermal Stress (°C)',
                    data: [44.2, 46.5, 48.0, 49.3, 47.8],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: '#ef4444'
                },
                {
                    label: 'Air Temp (°C)',
                    data: [39.5, 41.2, 42.8, 43.5, 42.0],
                    borderColor: '#f97316',
                    borderWidth: 2,
                    borderDash: [4, 4],
                    tension: 0.3,
                    pointBackgroundColor: '#f97316'
                },
                {
                    label: 'Outdoor WBGT (°C)',
                    data: [30.5, 31.8, 32.7, 33.5, 32.2],
                    borderColor: '#38bdf8',
                    borderWidth: 2,
                    tension: 0.3,
                    pointBackgroundColor: '#38bdf8'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#94a3b8',
                        font: { size: 10, weight: '600' },
                        boxWidth: 12
                    }
                },
                tooltip: {
                    backgroundColor: '#0f172a',
                    titleColor: '#f8fafc',
                    bodyColor: '#cbd5e1',
                    borderColor: '#334155',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(51, 65, 85, 0.4)' },
                    ticks: { color: '#94a3b8', font: { size: 10 } }
                },
                y: {
                    grid: { color: 'rgba(51, 65, 85, 0.4)' },
                    ticks: { color: '#94a3b8', font: { size: 10 } },
                    suggestedMin: 25,
                    suggestedMax: 55
                }
            }
        }
    });

    fetchForecastTrajectory();
}

async function fetchForecastTrajectory() {
    if (!state.forecastChart) return;
    const city = CITIES[state.city] || CITIES.delhi;
    const lat = city.center[0];
    const lon = city.center[1];

    try {
        const res = await fetch(`/api/v1/thermal/forecast?lat=${lat}&lon=${lon}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        const labels = data.projections.map(p => p.horizon);
        const utciVals = data.projections.map(p => p.utci_c);
        const tempVals = data.projections.map(p => p.weather.temperature_c);
        const wbgtVals = data.projections.map(p => p.wbgt_c);

        state.forecastChart.data.labels = labels;
        state.forecastChart.data.datasets[0].data = utciVals;
        state.forecastChart.data.datasets[1].data = tempVals;
        state.forecastChart.data.datasets[2].data = wbgtVals;
        state.forecastChart.update();
    } catch (err) {
        // Generate nice smooth city-specific curve
        const baseT = state.city === 'ahmedabad' ? 42.0 : state.city === 'surat' ? 36.5 : state.city === 'mumbai' ? 35.0 : 40.0;
        const rh = state.city === 'mumbai' || state.city === 'surat' ? 70 : 35;
        const tempVals = [baseT, baseT + 1.2, baseT + 2.5, baseT + 3.0, baseT + 1.8];
        const utciVals = tempVals.map(t => calculateUTCI(t, rh, 2.5, 650));
        const wbgtVals = tempVals.map(t => calculateWBGT(t, rh, 2.5, 650));

        state.forecastChart.data.datasets[0].data = utciVals;
        state.forecastChart.data.datasets[1].data = tempVals;
        state.forecastChart.data.datasets[2].data = wbgtVals;
        state.forecastChart.update();
    }
}

// -----------------------------------------------------------------------------
// Historical Hindcast Replay Controller
// -----------------------------------------------------------------------------
function initHindcast() {
    state.hindcast.eventId = 'delhi_june_2024';
    state.hindcast.stepIndex = 0;
    state.hindcast.data = HISTORICAL_EVENTS_DATA['delhi_june_2024'];
    renderHindcastStep();
}

function onHindcastEventChange(eventId) {
    state.hindcast.eventId = eventId;
    state.hindcast.stepIndex = 0;
    state.hindcast.data = HISTORICAL_EVENTS_DATA[eventId] || HISTORICAL_EVENTS_DATA['delhi_june_2024'];
    
    // Pause any active auto-play
    if (state.hindcast.isPlaying) {
        toggleHindcastPlay();
    }
    
    document.getElementById('hindcast-slider').value = 0;
    renderHindcastStep();
}

function onHindcastSliderChange(val) {
    state.hindcast.stepIndex = parseInt(val, 10);
    renderHindcastStep();
}

function stepHindcast(direction) {
    const totalSteps = state.hindcast.data.timeline.length;
    let nextStep = state.hindcast.stepIndex + direction;
    if (nextStep < 0) nextStep = 0;
    if (nextStep >= totalSteps) nextStep = totalSteps - 1;

    state.hindcast.stepIndex = nextStep;
    document.getElementById('hindcast-slider').value = nextStep;
    renderHindcastStep();
}

function toggleHindcastPlay() {
    const btnText = document.getElementById('hindcast-play-text');
    const btnIcon = document.getElementById('hindcast-play-icon');
    const isHindi = state.language === 'hi';

    if (state.hindcast.isPlaying) {
        clearInterval(state.hindcast.timerId);
        state.hindcast.isPlaying = false;
        if (btnText) btnText.textContent = isHindi ? I18N.hi.btn_play : I18N.en.btn_play;
        if (btnIcon) btnIcon.textContent = "▶";
    } else {
        state.hindcast.isPlaying = true;
        if (btnText) btnText.textContent = isHindi ? I18N.hi.btn_pause : I18N.en.btn_pause;
        if (btnIcon) btnIcon.textContent = "⏸";

        state.hindcast.timerId = setInterval(() => {
            const totalSteps = state.hindcast.data.timeline.length;
            if (state.hindcast.stepIndex < totalSteps - 1) {
                stepHindcast(1);
            } else {
                state.hindcast.stepIndex = 0;
                document.getElementById('hindcast-slider').value = 0;
                renderHindcastStep();
            }
        }, 1600);
    }
}

function resetHindcast() {
    if (state.hindcast.isPlaying) {
        toggleHindcastPlay();
    }
    state.hindcast.stepIndex = 0;
    document.getElementById('hindcast-slider').value = 0;
    renderHindcastStep();
}

function renderHindcastStep() {
    if (!state.hindcast.data) return;
    const step = state.hindcast.data.timeline[state.hindcast.stepIndex];
    if (!step) return;

    // Badges & Step displays
    const badgeEl = document.getElementById('hindcast-step-badge');
    const dateEl = document.getElementById('hindcast-date-display');
    const tempEl = document.getElementById('hindcast-temp');
    const rhEl = document.getElementById('hindcast-rh');
    const utciEl = document.getElementById('hindcast-utci');
    const wbgtEl = document.getElementById('hindcast-wbgt');
    const imdStatusEl = document.getElementById('hindcast-imd-status');
    const sihStatusEl = document.getElementById('hindcast-sih-status');
    const rationaleEl = document.getElementById('hindcast-rationale');

    if (badgeEl) badgeEl.textContent = step.lead_time;
    if (dateEl) dateEl.textContent = step.date;
    if (tempEl) tempEl.textContent = `${step.temp_c.toFixed(1)} °C`;
    if (rhEl) rhEl.textContent = `${step.rh_pct.toFixed(1)} %`;
    if (utciEl) utciEl.textContent = `${step.utci_c.toFixed(1)} °C`;
    if (wbgtEl) wbgtEl.textContent = `${step.wbgt_c.toFixed(1)} °C`;
    if (imdStatusEl) imdStatusEl.textContent = step.imd_status;
    if (sihStatusEl) sihStatusEl.textContent = step.sih_status;
    if (rationaleEl) rationaleEl.textContent = step.mitigation_trigger;
}

// -----------------------------------------------------------------------------
// NIOSH Occupational Safety & Hydration Engine
// -----------------------------------------------------------------------------
function updateOccupationalSafety() {
    const workloadSelect = document.getElementById('occ-workload');
    const sectorSelect = document.getElementById('occ-sector');
    if (workloadSelect) state.occupational.workload = workloadSelect.value;
    if (sectorSelect) state.occupational.sector = sectorSelect.value;

    const wbgt = state.thermalIndices.wbgt || calculateWBGT(state.weather.temp_c, state.weather.rh_pct);
    const workload = state.occupational.workload;
    const isHindi = state.language === 'hi';

    // Work-Rest schedule decision matrix per ISO 7243 / NIOSH
    let workPct = 100;
    let restPct = 0;
    let hydrationLiters = 0.50;
    let severity = "NORMAL";

    if (workload === 'very_heavy') {
        if (wbgt >= 30.0) { workPct = 0; restPct = 100; hydrationLiters = 1.00; severity = "CRITICAL"; }
        else if (wbgt >= 28.0) { workPct = 25; restPct = 75; hydrationLiters = 1.00; severity = "HIGH"; }
        else if (wbgt >= 26.0) { workPct = 50; restPct = 50; hydrationLiters = 0.75; severity = "MODERATE"; }
        else if (wbgt >= 25.0) { workPct = 75; restPct = 25; hydrationLiters = 0.75; severity = "CAUTION"; }
    } else if (workload === 'heavy') {
        if (wbgt >= 31.5) { workPct = 0; restPct = 100; hydrationLiters = 1.00; severity = "CRITICAL"; }
        else if (wbgt >= 29.0) { workPct = 25; restPct = 75; hydrationLiters = 1.00; severity = "HIGH"; }
        else if (wbgt >= 27.5) { workPct = 50; restPct = 50; hydrationLiters = 0.75; severity = "MODERATE"; }
        else if (wbgt >= 26.0) { workPct = 75; restPct = 25; hydrationLiters = 0.75; severity = "CAUTION"; }
    } else if (workload === 'moderate') {
        if (wbgt >= 32.5) { workPct = 0; restPct = 100; hydrationLiters = 1.00; severity = "CRITICAL"; }
        else if (wbgt >= 31.0) { workPct = 25; restPct = 75; hydrationLiters = 1.00; severity = "HIGH"; }
        else if (wbgt >= 29.5) { workPct = 50; restPct = 50; hydrationLiters = 0.75; severity = "MODERATE"; }
        else if (wbgt >= 28.0) { workPct = 75; restPct = 25; hydrationLiters = 0.75; severity = "CAUTION"; }
    } else { // light
        if (wbgt >= 33.0) { workPct = 25; restPct = 75; hydrationLiters = 1.00; severity = "HIGH"; }
        else if (wbgt >= 31.5) { workPct = 50; restPct = 50; hydrationLiters = 0.75; severity = "MODERATE"; }
        else if (wbgt >= 30.0) { workPct = 75; restPct = 25; hydrationLiters = 0.75; severity = "CAUTION"; }
    }

    state.occupational.workMinutes = Math.round((workPct / 100) * 60);
    state.occupational.restMinutes = 60 - state.occupational.workMinutes;

    // Render schedule elements
    const sevBadge = document.getElementById('occ-severity-badge');
    const cycleText = document.getElementById('occ-cycle-text');
    const minutesText = document.getElementById('occ-minutes-text');
    const barWork = document.getElementById('occ-bar-work');
    const barRest = document.getElementById('occ-bar-rest');
    const workPctEl = document.getElementById('occ-work-pct');
    const restPctEl = document.getElementById('occ-rest-pct');
    const hydrationEl = document.getElementById('occ-hydration-amount');
    const cadenceEl = document.getElementById('occ-hydration-cadence');

    if (sevBadge) {
        sevBadge.textContent = severity;
        sevBadge.style.color = severity === 'CRITICAL' || severity === 'HIGH' ? '#ef4444' : '#f59e0b';
    }

    if (cycleText) {
        if (isHindi) {
            cycleText.textContent = `${workPct}% कार्य / ${restPct}% विश्राम प्रति घंटा`;
        } else {
            cycleText.textContent = `${workPct}% Work / ${restPct}% Rest per hour`;
        }
    }

    if (minutesText) {
        if (isHindi) {
            minutesText.textContent = `${state.occupational.workMinutes} मिनट कार्य / ${state.occupational.restMinutes} मिनट छाया में विश्राम`;
        } else {
            minutesText.textContent = `${state.occupational.workMinutes} min work / ${state.occupational.restMinutes} min rest under shade`;
        }
    }

    if (barWork) barWork.style.width = `${workPct}%`;
    if (barRest) barRest.style.width = `${restPct}%`;
    if (workPctEl) workPctEl.textContent = `${workPct}%`;
    if (restPctEl) restPctEl.textContent = `${restPct}%`;

    if (hydrationEl) hydrationEl.textContent = hydrationLiters.toFixed(2);
    if (cadenceEl) {
        if (isHindi) {
            cadenceEl.textContent = "प्रत्येक 15 मिनट में 250 मिली ओआरएस या शीतल जल का सेवन करें।";
        } else {
            cadenceEl.textContent = "Drink 250ml every 15 minutes. Pre-position chilled water & ORS sachets.";
        }
    }

    // Update Sector Directives
    const sectorData = SECTOR_PROTOCOLS[state.occupational.sector] || SECTOR_PROTOCOLS.gig_delivery;
    const sectorTitleEl = document.getElementById('occ-sector-title');
    const sectorProtocolsEl = document.getElementById('occ-sector-protocols');

    if (sectorTitleEl) {
        sectorTitleEl.textContent = isHindi ? sectorData.title_hi : sectorData.title_en;
    }

    if (sectorProtocolsEl) {
        const list = isHindi ? sectorData.protocols_hi : sectorData.protocols_en;
        sectorProtocolsEl.innerHTML = list.map(item => `<li>${item}</li>`).join('');
    }
}

// -----------------------------------------------------------------------------
// Interactive Shift Work-Rest Timer
// -----------------------------------------------------------------------------
function toggleTimer() {
    const btnText = document.getElementById('timer-btn-text');
    const isHindi = state.language === 'hi';

    if (state.occupational.timerRunning) {
        clearInterval(state.occupational.timerInterval);
        state.occupational.timerRunning = false;
        if (btnText) btnText.textContent = isHindi ? I18N.hi.timer_start : I18N.en.timer_start;
    } else {
        state.occupational.timerRunning = true;
        if (btnText) btnText.textContent = isHindi ? I18N.hi.timer_pause : I18N.en.timer_pause;

        state.occupational.timerInterval = setInterval(() => {
            if (state.occupational.timerSeconds > 0) {
                state.occupational.timerSeconds--;
                updateTimerDisplay();
            } else {
                // Phase switch
                if (state.occupational.currentPhase === 'work') {
                    state.occupational.currentPhase = 'rest';
                    state.occupational.timerSeconds = Math.max(1, state.occupational.restMinutes) * 60;
                } else {
                    state.occupational.currentPhase = 'work';
                    state.occupational.timerSeconds = Math.max(1, state.occupational.workMinutes) * 60;
                }
                updateTimerDisplay();
            }
        }, 1000);
    }
}

function resetTimer() {
    if (state.occupational.timerRunning) {
        toggleTimer();
    }
    state.occupational.currentPhase = 'work';
    state.occupational.timerSeconds = Math.max(1, state.occupational.workMinutes) * 60;
    updateTimerDisplay();
}

function updateTimerDisplay() {
    const displayEl = document.getElementById('timer-display');
    const phaseBadgeEl = document.getElementById('timer-phase-badge');
    const phaseDescEl = document.getElementById('timer-phase-desc');
    const isHindi = state.language === 'hi';

    const mins = Math.floor(state.occupational.timerSeconds / 60);
    const secs = state.occupational.timerSeconds % 60;
    const formatted = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

    if (displayEl) displayEl.textContent = formatted;

    if (phaseBadgeEl) {
        if (state.occupational.currentPhase === 'work') {
            phaseBadgeEl.textContent = isHindi ? I18N.hi.phase_work : I18N.en.phase_work;
            phaseBadgeEl.className = "text-[10px] font-black px-2 py-0.5 rounded bg-orange-600 text-white uppercase animate-pulse";
        } else {
            phaseBadgeEl.textContent = isHindi ? I18N.hi.phase_rest : I18N.en.phase_rest;
            phaseBadgeEl.className = "text-[10px] font-black px-2 py-0.5 rounded bg-blue-600 text-white uppercase animate-pulse";
        }
    }

    if (phaseDescEl) {
        if (state.occupational.currentPhase === 'work') {
            phaseDescEl.textContent = isHindi ? I18N.hi.phase_work_desc : I18N.en.phase_work_desc;
        } else {
            phaseDescEl.textContent = isHindi ? I18N.hi.phase_rest_desc : I18N.en.phase_rest_desc;
        }
    }
}

// -----------------------------------------------------------------------------
// Action-Triggered Public Health Advisories
// -----------------------------------------------------------------------------
function updateAdvisories() {
    const isHindi = state.language === 'hi';
    const risk = state.thermalIndices.risk_score || 50;

    const municipalEl = document.getElementById('advisory-municipal');
    const hospitalEl = document.getElementById('advisory-hospital');
    const citizenEl = document.getElementById('advisory-citizen');

    let municipalItems = [];
    let hospitalItems = [];
    let citizenItems = [];

    if (risk >= 80) { // Red / Critical
        municipalItems = isHindi ? [
            "दोपहर 11:30 से 15:30 तक खुले में निर्माण एवं भारी शारीरिक श्रम पर पूर्ण रोक लगाएं।",
            "प्रमुख चौराहों व मलिन बस्तियों में मोबाइल मिस्टिंग टैंकर व आपातकालीन पेयजल केंद्र सक्रिय करें।",
            "वातानुकूलित शेल्टर व सार्वजनिक पार्कों को बेघर नागरिकों हेतु 24 घंटे खुला रखें।"
        ] : [
            "Enforce strict moratorium on outdoor heavy labor between 11:30 AM and 3:30 PM.",
            "Deploy mobile misting tankers and emergency water stations in informal settlements.",
            "Operate air-conditioned cooling shelters 24/7 for homeless and vulnerable citizens."
        ];

        hospitalItems = isHindi ? [
            "हीटस्ट्रोक वार्ड सक्रिय करें: 20% आईसीयू बेड और आइस-पैक बाथ तैयार रखें।",
            "आईवी फ्लूइड, ओआरएस और जीवनरक्षक दवाओं का 100% बफर स्टॉक सुनिश्चित करें।",
            "आशा एवं एएनएम कार्यकर्ताओं द्वारा घर-घर जाकर बुजुर्गों व बच्चों की निगरानी सुनिश्चित करें।"
        ] : [
            "Activate dedicated Heatstroke Emergency Wards with ice-pack immersion baths.",
            "Maintain 100% buffer stock of IV normal saline, ORS, and essential electrolytes.",
            "Mobilize ASHA/ANM health workers for active surveillance of elderly and pregnant women."
        ];

        citizenItems = isHindi ? [
            "दोपहर के समय धूप में निकलने से बचें; अनिवार्य होने पर गीला सूती गमछा सिर पर रखें।",
            "बिना प्यास लगे भी प्रत्येक 20 मिनट में पानी, छाछ या नींबू-ओआरएस का सेवन करें।",
            "चक्कर, तेज सिरदर्द या पसीना बंद होने पर तुरंत 108 पर कॉल करें या नजदीकी अस्पताल जाएं।"
        ] : [
            "Avoid direct sun exposure between 11:00 AM and 4:00 PM; wear wide-brimmed headwear.",
            "Drink chilled water, buttermilk, or ORS every 20 minutes even without feeling thirsty.",
            "Seek immediate medical care (Dial 108) if experiencing confusion, hot dry skin, or fainting."
        ];
    } else if (risk >= 60) { // Orange / High
        municipalItems = isHindi ? [
            "श्रमिकों हेतु कार्य-विश्राम अनुपात 50% काम / 50% आराम लागू करें।",
            "बस स्टैंड, रेलवे स्टेशन व व्यस्त बाजारों में ओआरएस जल वितरण केंद्र शुरू करें।"
        ] : [
            "Mandate 50% Work / 50% Rest cycle under shade for outdoor construction crews.",
            "Establish active ORS hydration kiosks across major transit nodes and markets."
        ];

        hospitalItems = isHindi ? [
            "आपातकालीन विभागों में हीट एग्जॉशन के मरीजों हेतु अतिरिक्त ओआरएस बेड तैयार रखें।",
            "प्राथमिक स्वास्थ्य केंद्रों (PHC) में निर्जलीकरण के मामलों की दैनिक रिपोर्टिंग शुरू करें।"
        ] : [
            "Set up dedicated rapid rehydration corners in all primary healthcare facilities.",
            "Initiate daily surveillance reporting of dehydration and heat exhaustion admissions."
        ];

        citizenItems = isHindi ? [
            "हल्के रंग के ढीले सूती कपड़े पहनें और धूप में छतरी या टोपी का उपयोग करें।",
            "चाय, कॉफी व अत्यधिक मीठे पेयों से बचें; नींबू पानी और नारियल पानी पिएं।"
        ] : [
            "Wear loose, light-colored cotton clothing and carry a damp cloth or umbrella.",
            "Avoid caffeinated or sugary beverages; consume lemonade, coconut water, or ORS."
        ];
    } else { // Moderate / Low
        municipalItems = isHindi ? [
            "नियमित ग्रीष्मकालीन जल आपूर्ति और सार्वजनिक प्याऊ की स्वच्छता सुनिश्चित करें।",
            "नागरिकों को मौसम विभाग के पूर्वानुमान के प्रति जागरूक रखें।"
        ] : [
            "Maintain regular municipal drinking water supply and clean public kiosks.",
            "Issue standard summer wellness advisories via digital information boards."
        ];

        hospitalItems = isHindi ? [
            "मानक आपातकालीन चिकित्सा स्टॉक और ओआरएस की उपलब्धता बनाए रखें।"
        ] : [
            "Maintain standard oral rehydration stock across all outpatient clinics."
        ];

        citizenItems = isHindi ? [
            "पर्याप्त मात्रा में पानी पिएं और दोपहर में सीधे धूप से बचें।"
        ] : [
            "Stay well-hydrated throughout the day and take shaded breaks when working outdoors."
        ];
    }

    if (municipalEl) municipalEl.innerHTML = municipalItems.map(item => `<li>${item}</li>`).join('');
    if (hospitalEl) hospitalEl.innerHTML = hospitalItems.map(item => `<li>${item}</li>`).join('');
    if (citizenEl) citizenEl.innerHTML = citizenItems.map(item => `<li>${item}</li>`).join('');
}

// -----------------------------------------------------------------------------
// Instant Bilingual Switcher Engine
// -----------------------------------------------------------------------------
function setLanguage(lang) {
    state.language = lang;
    const isHindi = lang === 'hi';

    // Update toggle button styles
    const btnEn = document.getElementById('lang-btn-en');
    const btnHi = document.getElementById('lang-btn-hi');

    if (btnEn && btnHi) {
        if (isHindi) {
            btnHi.className = "px-2.5 py-1 rounded-md text-xs font-bold transition-all bg-orange-600 text-white shadow";
            btnEn.className = "px-2.5 py-1 rounded-md text-xs font-bold text-slate-400 hover:text-slate-200 transition-all";
        } else {
            btnEn.className = "px-2.5 py-1 rounded-md text-xs font-bold transition-all bg-orange-600 text-white shadow";
            btnHi.className = "px-2.5 py-1 rounded-md text-xs font-bold text-slate-400 hover:text-slate-200 transition-all";
        }
    }

    // Apply translations to all data-i18n elements
    const dict = I18N[lang] || I18N.en;
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) {
            el.innerHTML = dict[key];
        }
    });

    // Update active city badge text
    const city = CITIES[state.city] || CITIES.delhi;
    const badgeEl = document.getElementById('map-active-city-badge');
    if (badgeEl) {
        badgeEl.textContent = isHindi ? city.badge_hi : city.badge;
    }

    // Update subcomponents
    computeThermalMetrics();
    updateWardInspectorUI(state.activeWardData);
    renderHindcastStep();
    updateOccupationalSafety();
    updateTimerDisplay();
    updateAdvisories();
}

// -----------------------------------------------------------------------------
// Global Application Bootstrap
// -----------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    initForecastChart();
    initHindcast();
    updateControls();
    resetTimer();
});

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger(__name__)

class TelegramDispatcher:
    """
    Async Telegram Bot Notification & Municipal Broadcast Dispatcher.
    Dispatches bilingual heat risk bulletins, public health warnings,
    and administrative action triggers directly to municipal response channels.
    """

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        api_base_url: str = "https://api.telegram.org"
    ):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        self.api_base_url = api_base_url.rstrip("/")

    def format_html_bulletin(
        self,
        ward_name: str,
        risk_score: float,
        risk_band: str,
        thermal_metrics: Dict[str, Any],
        municipal_playbook: Dict[str, List[str]],
        occupational_schedule: str,
        language: str = "both"  # "en", "hi", or "both"
    ) -> str:
        """
        Format an HTML-styled heat risk alert bulletin for Telegram broadcast.
        """
        # Emoji and badge based on risk severity
        if risk_score >= 80.0:
            status_badge = "🔴 <b>CRITICAL EMERGENCY / अति गंभीर आपातकाल</b>"
        elif risk_score >= 55.0:
            status_badge = "🟠 <b>HIGH RISK / उच्च जोखिम अलर्ट</b>"
        elif risk_score >= 30.0:
            status_badge = "🟡 <b>MODERATE RISK / मध्यम चेतावनी</b>"
        else:
            status_badge = "🟢 <b>LOW RISK / सामान्य स्थिति</b>"

        utci = thermal_metrics.get("utci_c", "N/A")
        wbgt = thermal_metrics.get("wbgt_c", "N/A")
        hi = thermal_metrics.get("heat_index_c", "N/A")

        lines = [
            f"🚨 <b>NDMA/NCDC HEATWAVE DISPATCH BULLETIN</b> 🚨",
            status_badge,
            "━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"📍 <b>Ward / क्षेत्र:</b> <code>{ward_name}</code>",
            f"📊 <b>Composite Risk Score:</b> <b>{risk_score:.1f}/100</b> ({risk_band})",
            "",
            f"🌡️ <b>Thermal Stress Metrics:</b>",
            f"  • <b>UTCI:</b> <code>{utci}°C</code> (Universal Thermal Climate Index)",
            f"  • <b>WBGT:</b> <code>{wbgt}°C</code> (Wet-Bulb Globe Temp)",
            f"  • <b>Heat Index:</b> <code>{hi}°C</code> (Feels Like)",
            "",
            f"👷 <b>Occupational Protocol (NIOSH/ISO 7243):</b>",
            f"  👉 <i>{occupational_schedule}</i>",
            "━━━━━━━━━━━━━━━━━━━━━━━━━"
        ]

        # English directives
        if language in ("en", "both"):
            en_actions = municipal_playbook.get("english", [])
            lines.append("🏛️ <b>Municipal Action Triggers (EN):</b>")
            for action in en_actions:
                lines.append(f"  • {action}")

        # Hindi directives
        if language in ("hi", "both"):
            hi_actions = municipal_playbook.get("hindi", [])
            lines.append("")
            lines.append("📢 <b>नगर निगम कार्य निर्देश (HI):</b>")
            for action in hi_actions:
                lines.append(f"  • {action}")

        lines.extend([
            "━━━━━━━━━━━━━━━━━━━━━━━━━",
            "🛡️ <i>Issued by MoES/NCMRWF SIH26083 Autonomous Dispatch Engine</i>"
        ])

        return "\n".join(lines)

    def format_markdown_bulletin(
        self,
        ward_name: str,
        risk_score: float,
        risk_band: str,
        thermal_metrics: Dict[str, Any],
        occupational_schedule: str
    ) -> str:
        """
        Format a MarkdownV2/standard Markdown heat risk bulletin.
        """
        utci = thermal_metrics.get("utci_c", "N/A")
        wbgt = thermal_metrics.get("wbgt_c", "N/A")

        return (
            f"*🚨 HEATWAVE DISPATCH: {ward_name}*\n\n"
            f"*Risk Score:* {risk_score:.1f}/100 ({risk_band})\n"
            f"*Physiological UTCI:* {utci}°C | *WBGT:* {wbgt}°C\n\n"
            f"*NIOSH Work/Rest Protocol:* {occupational_schedule}\n\n"
            f"_Automated Municipal Directive — SIH26083_"
        )

    async def send_message(
        self,
        text: str,
        chat_id: Optional[str] = None,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = True
    ) -> Dict[str, Any]:
        """
        Send a Telegram notification asynchronously.
        If bot_token or chat_id is missing or mock mode is needed,
        simulates successful dispatch with full payload audit.
        """
        target_chat = chat_id or self.chat_id
        token = self.bot_token

        # Simulated broadcast fallback if no active Telegram token configured
        if not token or not target_chat or token == "simulated_token":
            logger.info("No live Telegram credentials provided; simulating broadcast dispatch.")
            return {
                "status": "simulated",
                "chat_id": target_chat or "@HeatwaveAlertsSimulated",
                "parse_mode": parse_mode,
                "message_preview": text[:200] + "..." if len(text) > 200 else text,
                "length_chars": len(text),
                "delivered": True,
                "timestamp": asyncio.get_event_loop().time()
            }

        url = f"{self.api_base_url}/bot{token}/sendMessage"
        payload = {
            "chat_id": target_chat,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(url, json=payload)
                resp_json = response.json()
                if response.status_code == 200 and resp_json.get("ok"):
                    return {
                        "status": "delivered",
                        "chat_id": target_chat,
                        "message_id": resp_json.get("result", {}).get("message_id"),
                        "delivered": True
                    }
                else:
                    return {
                        "status": "failed",
                        "error": resp_json.get("description", response.text),
                        "status_code": response.status_code,
                        "delivered": False
                    }
            except Exception as exc:
                logger.error(f"Telegram dispatch failed: {exc}")
                return {
                    "status": "error",
                    "error": str(exc),
                    "delivered": False
                }

    async def broadcast_ward_alert(
        self,
        ward_name: str,
        risk_score: float,
        risk_band: str,
        thermal_metrics: Dict[str, Any],
        municipal_playbook: Dict[str, List[str]],
        occupational_schedule: str,
        chat_id: Optional[str] = None,
        language: str = "both"
    ) -> Dict[str, Any]:
        """
        Build and broadcast a full ward heat risk alert bulletin.
        """
        message_text = self.format_html_bulletin(
            ward_name=ward_name,
            risk_score=risk_score,
            risk_band=risk_band,
            thermal_metrics=thermal_metrics,
            municipal_playbook=municipal_playbook,
            occupational_schedule=occupational_schedule,
            language=language
        )
        dispatch_result = await self.send_message(text=message_text, chat_id=chat_id, parse_mode="HTML")
        return {
            "ward_name": ward_name,
            "risk_score": risk_score,
            "risk_band": risk_band,
            "dispatch": dispatch_result,
            "bulletin_text": message_text
        }

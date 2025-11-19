import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class MeetingMinutesGenerator:
    """Generate professional meeting minutes from transcripts using LLMs in structured JSON format."""

    # Available models on Groq
    MODELS = {
        "llama-3.3-70b": "llama-3.3-70b-versatile",
        "llama-3.1-8b": "llama-3.1-8b-instant",
        "mixtral-8x7b": "mixtral-8x7b-32768",
        "gemma-2-9b": "gemma2-9b-it",
    }

    def __init__(self, api_key=None, model="llama-3.3-70b", concise=True):
        """
        Initialize the meeting minutes generator.

        Args:
            api_key: Groq API key.
            model: Model to use (see MODELS dict for options)
            concise: If True, generates brief 2-3 sentence summaries per topic
        """
        self.client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
        self.model = self.MODELS.get(model, self.MODELS["llama-3.3-70b"])
        self.concise = concise

    def generate_minutes(self, transcript, include_action_items=True):
        """
        Generate professional meeting minutes from a transcript in structured JSON.

        Args:
            transcript: Full meeting transcript
            include_action_items: Highlight action items if True

        Returns:
            Dict with structured meeting minutes
        """
        prompt = self._build_prompt(transcript, include_action_items)

        try:
            system_prompt = "You are an executive assistant generating professional meeting minutes in structured JSON."
            if self.concise:
                system_prompt += " Summarize key points in 2-3 sentences per topic."

            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1024 if self.concise else 2048,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )

            # Attempt to parse the output as JSON
            raw_minutes = response.choices[0].message.content
            try:
                minutes_json = json.loads(raw_minutes)
            except json.JSONDecodeError:
                # If parsing fails, return raw string
                minutes_json = {"raw_minutes": raw_minutes}

            return {
                "minutes": minutes_json,
                "model": self.model,
                "tokens": response.usage.total_tokens,
            }

        except Exception as e:
            return {"error": str(e)}

    def _build_prompt(self, transcript, include_action_items):
        """
        Build the prompt instructing the LLM to produce structured JSON meeting minutes.
        """
        prompt = f"Here is the transcript of a meeting:\n\n{transcript}\n\n"
        prompt += "Generate professional meeting minutes in JSON format with the following fields:\n"
        prompt += """{
                        "title": string,
                        "date": string,
                        "attendees": string,
                        "summary": string,
                        "topics": [
                            {
                            "topic": string,
                            "points": [string, string, ...]
                            }
                        ],
                        "action_items": [
                            {
                            "task": string,
                            "responsible": string,
                            "deadline": string
                            }
                        ],
                        "recommendations": [string, ...],
                        "next_meeting": {
                            "date_time": string,
                            "location": string
                        },
                        "approved_by": string,
                        "approval_date": string
                        }\n"""
        prompt += "Include 2-3 sentence summaries per topic."
        if include_action_items:
            prompt += (
                " Highlight any action items with responsible parties and deadlines."
            )
        prompt += " Output valid JSON only, no Markdown or extra text."
        return prompt

    def generate_batch(self, transcripts, include_action_items=True):
        """
        Generate structured meeting minutes for multiple transcripts.

        Args:
            transcripts: List of transcript strings
            include_action_items: Whether to highlight action items

        Returns:
            List of dicts containing generated minutes
        """
        all_minutes = []
        for transcript in transcripts:
            minutes = self.generate_minutes(transcript, include_action_items)
            all_minutes.append(minutes)

        return all_minutes
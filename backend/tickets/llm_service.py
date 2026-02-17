"""
LLM Classification Service for Support Tickets.
Integrates with OpenAI API to suggest ticket categories and priorities.
"""
import os
import json
from openai import OpenAI


class LLMClassifier:
    """
    Classifier that uses LLM to suggest ticket category and priority.
    Handles API errors gracefully and returns None on failure.
    """
    
    def __init__(self):
        """
        Initialize with API key from environment variable.
        If OPENAI_API_KEY is not set or invalid, client will be None
        and classify_ticket will return None (graceful degradation).
        """
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.client = None
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                # Log error but don't fail - allows system to work without LLM
                print(f"OpenAI client initialization error: {e}")
                self.client = None
    
    def classify_ticket(self, description):
        """
        Classify a ticket description and suggest category and priority.
        
        Args:
            description (str): The ticket description to classify
            
        Returns:
            dict: Dictionary with 'suggested_category' and 'suggested_priority' keys,
                  or None if classification fails
        """
        if not self.client:
            return None
        
        prompt = f"""Analyze this support ticket description and suggest:
1. Category (billing, technical, account, or general)
2. Priority (low, medium, high, or critical)

Description: {description}

Respond in JSON format:
{{"category": "...", "priority": "..."}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a support ticket classifier."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            # Parse the response content
            content = response.choices[0].message.content
            result = json.loads(content)
            
            return {
                'suggested_category': result['category'],
                'suggested_priority': result['priority']
            }
        except json.JSONDecodeError as e:
            # Log JSON parsing errors - LLM may have returned invalid format
            print(f"LLM classification JSON parsing error: {e}")
            return None
        except Exception as e:
            # Log network errors and other exceptions - allows graceful degradation
            print(f"LLM classification error: {e}")
            return None

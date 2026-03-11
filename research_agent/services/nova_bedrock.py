import json
from typing import Any

import boto3
from botocore.exceptions import ClientError


class NovaLiteClient:
    def __init__(self, region_name: str = "us-east-1") -> None:
        """
        Initialize the Nova Lite client for Amazon Bedrock.

        Args:
            region_name: AWS region name
        """
        self.region_name: str = region_name
        self.bedrock_runtime: Any = boto3.client(
            service_name="bedrock-runtime", region_name=region_name
        )

    def complete(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate completion using Nova model via Bedrock.

        Args:
            prompt: Input prompt
            max_tokens: Maximum number of tokens to generate

        Returns:
            Generated text completion
        """
        # Prepare the request for Nova model
        body = json.dumps(
            {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": max_tokens,
                    "temperature": 0.7,
                    "topP": 0.9,
                },
            }
        )

        try:
            response = self.bedrock_runtime.invoke_model(
                modelId="amazon.nova-lite-v1:0",  # Using Nova Lite model
                contentType="application/json",
                accept="application/json",
                body=body,
            )

            response_body = json.loads(response.get("body").read())
            return response_body["results"][0]["outputText"]

        except ClientError as e:
            raise Exception(f"Error calling Bedrock API: {str(e)}")

    def score_relevance(self, query: str, documents: list[str]) -> list[float]:
        """
        Score document relevance to a query using Nova embeddings.

        Args:
            query: Query string
            documents: List of document strings to score

        Returns:
            List of relevance scores
        """
        scores = []

        # For each document, create a prompt to get relevance score
        for doc in documents:
            prompt = f"""
            Query: {query}
            Document: {doc}

            On a scale of 0.0 to 1.0, how relevant is the document to the query?
            Respond with only the numeric score.
            """

            try:
                response = self.complete(prompt, max_tokens=10)
                # Try to parse the response as float
                try:
                    score = float(response.strip())
                except ValueError:
                    # If parsing fails, default to 0.0
                    score = 0.0
                scores.append(min(1.0, max(0.0, score)))  # Clamp between 0 and 1
            except Exception:
                scores.append(0.0)  # Default score if error occurs

        return scores

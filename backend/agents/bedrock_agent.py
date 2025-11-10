"""
AWS Bedrock Agent implementation.
Handles AI conversation using Claude via AWS Bedrock with boto3.
"""

import json
import boto3
from typing import List, Dict, AsyncGenerator, Optional
from config import get_settings
from models import Message
import logging

logger = logging.getLogger(__name__)


class BedrockAgent:
    """AI Agent using AWS Bedrock runtime with Claude."""

    def __init__(self):
        """Initialize the Bedrock agent with AWS credentials."""
        self.settings = get_settings()
        self._initialize_bedrock_client()

    def _initialize_bedrock_client(self):
        """Initialize AWS Bedrock runtime and agent runtime clients."""
        try:
            # Create boto3 session with credentials
            session_kwargs = {
                "region_name": self.settings.aws_region
            }

            # Add credentials if provided
            if self.settings.aws_access_key_id and self.settings.aws_secret_access_key:
                session_kwargs["aws_access_key_id"] = self.settings.aws_access_key_id
                session_kwargs["aws_secret_access_key"] = self.settings.aws_secret_access_key

            # Create Bedrock runtime client
            self.bedrock_runtime = boto3.client(
                service_name="bedrock-runtime",
                **session_kwargs
            )

            # Create Bedrock Agent runtime client for Knowledge Bases
            self.bedrock_agent_runtime = boto3.client(
                service_name="bedrock-agent-runtime",
                **session_kwargs
            )

            logger.info(f"Bedrock clients initialized in region: {self.settings.aws_region}")

        except Exception as e:
            logger.error(f"Failed to initialize Bedrock clients: {e}")
            raise

    def _format_conversation_history(self, messages: List[Message]) -> List[Dict[str, str]]:
        """
        Format conversation history for Claude API.

        Args:
            messages: List of Message objects

        Returns:
            List of message dictionaries for Claude API
        """
        formatted = []
        for msg in messages:
            # Claude API only accepts 'user' and 'assistant' roles
            if msg.role in ["user", "assistant"]:
                formatted.append({
                    "role": msg.role,
                    "content": msg.content
                })
        return formatted

    async def stream_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream AI response using AWS Bedrock.

        Args:
            user_message: The user's message
            conversation_history: Previous messages in the conversation
            system_prompt: Optional system prompt to guide AI behavior

        Yields:
            Chunks of the AI response as they're generated
        """
        try:
            # Build messages list
            messages = []

            # Add conversation history
            if conversation_history:
                history = self._format_conversation_history(conversation_history)
                messages.extend(history)

            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })

            # Prepare request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": messages,
                "max_tokens": self.settings.max_tokens,
                "temperature": self.settings.temperature,
                "top_p": self.settings.top_p,
            }

            # Add system prompt if provided
            if system_prompt:
                request_body["system"] = system_prompt

            # Log request
            logger.info(f"Streaming response for message: {user_message[:50]}...")

            # Invoke model with streaming
            response = self.bedrock_runtime.invoke_model_with_response_stream(
                modelId=self.settings.bedrock_model_id,
                body=json.dumps(request_body)
            )

            # Process the streaming response
            stream = response.get('body')
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        # Parse the chunk data
                        chunk_data = json.loads(chunk.get('bytes').decode())

                        # Handle different event types
                        if chunk_data.get('type') == 'content_block_delta':
                            delta = chunk_data.get('delta', {})
                            if delta.get('type') == 'text_delta':
                                text = delta.get('text', '')
                                if text:
                                    yield text

                        elif chunk_data.get('type') == 'message_delta':
                            # Message metadata (usage stats, etc.)
                            continue

                        elif chunk_data.get('type') == 'message_stop':
                            # End of message
                            break

        except Exception as e:
            logger.error(f"Error streaming response: {e}")
            error_msg = str(e)

            # Provide more helpful error messages
            if "ValidationException" in error_msg:
                yield "[ERROR] Invalid request to AWS Bedrock. Please check your configuration."
            elif "AccessDeniedException" in error_msg:
                yield "[ERROR] Access denied. Please verify your AWS credentials and Bedrock permissions."
            elif "ResourceNotFoundException" in error_msg:
                yield "[ERROR] Model not found. Please ensure Claude 3.5 Sonnet is enabled in your AWS region."
            elif "ThrottlingException" in error_msg:
                yield "[ERROR] Rate limit exceeded. Please try again in a moment."
            else:
                yield f"[ERROR] Failed to generate response: {error_msg}"

    async def get_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Get complete AI response (non-streaming).

        Args:
            user_message: The user's message
            conversation_history: Previous messages in the conversation
            system_prompt: Optional system prompt to guide AI behavior

        Returns:
            Complete AI response as a string
        """
        try:
            # Build messages list
            messages = []

            # Add conversation history
            if conversation_history:
                history = self._format_conversation_history(conversation_history)
                messages.extend(history)

            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })

            # Prepare request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": messages,
                "max_tokens": self.settings.max_tokens,
                "temperature": self.settings.temperature,
                "top_p": self.settings.top_p,
            }

            # Add system prompt if provided
            if system_prompt:
                request_body["system"] = system_prompt

            # Log request
            logger.info(f"Getting response for message: {user_message[:50]}...")

            # Invoke model
            response = self.bedrock_runtime.invoke_model(
                modelId=self.settings.bedrock_model_id,
                body=json.dumps(request_body)
            )

            # Parse response
            response_body = json.loads(response.get('body').read())

            # Extract text from content blocks
            content_blocks = response_body.get('content', [])
            response_text = ""

            for block in content_blocks:
                if block.get('type') == 'text':
                    response_text += block.get('text', '')

            return response_text

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            error_msg = str(e)

            # Provide more helpful error messages
            if "ValidationException" in error_msg:
                return "[ERROR] Invalid request to AWS Bedrock. Please check your configuration."
            elif "AccessDeniedException" in error_msg:
                return "[ERROR] Access denied. Please verify your AWS credentials and Bedrock permissions."
            elif "ResourceNotFoundException" in error_msg:
                return "[ERROR] Model not found. Please ensure Claude 3.5 Sonnet is enabled in your AWS region."
            elif "ThrottlingException" in error_msg:
                return "[ERROR] Rate limit exceeded. Please try again in a moment."
            else:
                return f"[ERROR] Failed to generate response: {error_msg}"

    def retrieve_from_knowledge_base(
        self,
        query: str,
        knowledge_base_id: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict]:
        """
        Retrieve relevant information from AWS Bedrock Knowledge Base.

        Args:
            query: The search query
            knowledge_base_id: Knowledge base ID (uses default from settings if not provided)
            max_results: Maximum number of results to retrieve

        Returns:
            List of retrieved documents with content and metadata
        """
        try:
            kb_id = knowledge_base_id or self.settings.knowledge_base_id

            if not kb_id:
                logger.warning("No knowledge base ID configured")
                return []

            logger.info(f"Retrieving from knowledge base {kb_id} for query: {query[:50]}...")

            # Retrieve from knowledge base
            response = self.bedrock_agent_runtime.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={
                    'text': query
                },
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': max_results
                    }
                }
            )

            # Extract retrieved results
            results = []
            for item in response.get('retrievalResults', []):
                results.append({
                    'content': item.get('content', {}).get('text', ''),
                    'score': item.get('score', 0.0),
                    'location': item.get('location', {}),
                    'metadata': item.get('metadata', {})
                })

            logger.info(f"Retrieved {len(results)} results from knowledge base")
            return results

        except Exception as e:
            logger.error(f"Error retrieving from knowledge base: {e}")
            return []

    async def retrieve_and_generate(
        self,
        user_message: str,
        knowledge_base_id: Optional[str] = None,
        conversation_history: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Retrieve from knowledge base and generate response with context.
        This uses AWS Bedrock's RetrieveAndGenerate API.

        Args:
            user_message: The user's message
            knowledge_base_id: Knowledge base ID (uses default from settings if not provided)
            conversation_history: Previous messages in the conversation
            system_prompt: Optional system prompt to guide AI behavior

        Yields:
            Chunks of the AI response as they're generated
        """
        try:
            kb_id = knowledge_base_id or self.settings.knowledge_base_id

            if not kb_id:
                logger.warning("No knowledge base ID configured, falling back to regular chat")
                async for chunk in self.stream_response(user_message, conversation_history, system_prompt):
                    yield chunk
                return

            logger.info(f"Using RetrieveAndGenerate with KB {kb_id}")

            # Build the input configuration
            input_config = {
                'text': user_message
            }

            # Prepare the request
            request_params = {
                'input': input_config,
                'retrieveAndGenerateConfiguration': {
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': kb_id,
                        'modelArn': f'arn:aws:bedrock:{self.settings.aws_region}::foundation-model/{self.settings.bedrock_model_id}',
                        'generationConfiguration': {
                            'inferenceConfig': {
                                'textInferenceConfig': {
                                    'maxTokens': self.settings.max_tokens,
                                    'temperature': self.settings.temperature,
                                    'topP': self.settings.top_p
                                }
                            }
                        }
                    }
                }
            }

            # Add session ID if there's conversation history
            if conversation_history and len(conversation_history) > 0:
                # For now, we'll use a simple session approach
                # In production, you'd want to manage session IDs properly
                import hashlib
                import time
                session_id = hashlib.md5(f"{time.time()}".encode()).hexdigest()
                request_params['sessionId'] = session_id

            # Call RetrieveAndGenerate (non-streaming for now)
            response = self.bedrock_agent_runtime.retrieve_and_generate(**request_params)

            # Extract the generated text
            output = response.get('output', {}).get('text', '')

            # Yield the response in chunks to simulate streaming
            chunk_size = 10
            for i in range(0, len(output), chunk_size):
                yield output[i:i + chunk_size]

            # Log citations if available
            citations = response.get('citations', [])
            if citations:
                logger.info(f"Response includes {len(citations)} citations from knowledge base")

        except Exception as e:
            logger.error(f"Error in retrieve_and_generate: {e}")
            error_msg = str(e)
            if "ResourceNotFoundException" in error_msg:
                yield f"[ERROR] Knowledge base not found. Please verify the knowledge base ID."
            elif "AccessDeniedException" in error_msg:
                yield f"[ERROR] Access denied to knowledge base. Please check IAM permissions."
            else:
                yield f"[ERROR] Failed to retrieve and generate: {error_msg}"

    async def stream_response_with_knowledge(
        self,
        user_message: str,
        knowledge_base_id: Optional[str] = None,
        conversation_history: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None,
        max_kb_results: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream AI response enhanced with knowledge base retrieval.
        First retrieves relevant context, then streams response.

        Args:
            user_message: The user's message
            knowledge_base_id: Knowledge base ID (uses default from settings if not provided)
            conversation_history: Previous messages in the conversation
            system_prompt: Optional system prompt to guide AI behavior
            max_kb_results: Maximum number of knowledge base results to include

        Yields:
            Chunks of the AI response as they're generated
        """
        try:
            # Use configured max results if not specified
            if max_kb_results is None:
                max_kb_results = self.settings.kb_max_results

            # First, retrieve relevant context from knowledge base
            kb_results = self.retrieve_from_knowledge_base(
                query=user_message,
                knowledge_base_id=knowledge_base_id,
                max_results=max_kb_results
            )

            # Build enhanced system prompt with retrieved context
            enhanced_system_prompt = system_prompt or ""

            if kb_results:
                context_text = "\n\n=== RETRIEVED MATCH DATA FROM KNOWLEDGE BASE ===\n"
                context_text += f"You have access to {len(kb_results)} League of Legends match records.\n"
                context_text += "Each record is JSON data containing: championName, kills, deaths, assists, gameMode, win, items, gold, damage, etc.\n\n"

                for idx, result in enumerate(kb_results, 1):
                    context_text += f"\n[Match {idx}] (Relevance: {result['score']:.2f})\n"
                    context_text += f"{result['content']}\n"

                context_text += "\n=== END OF MATCH DATA ===\n\n"
                context_text += "INSTRUCTIONS:\n"
                context_text += "- Analyze ALL the match data provided above\n"
                context_text += "- Count champion occurrences to determine most played\n"
                context_text += "- Calculate win rates, KDA, and other statistics\n"
                context_text += "- Provide specific numbers and examples from the data\n"
                context_text += "- If asked about 'most played', count all instances of each champion\n"

                enhanced_system_prompt = context_text + "\n\n" + enhanced_system_prompt

            # Stream response with enhanced context
            async for chunk in self.stream_response(
                user_message=user_message,
                conversation_history=conversation_history,
                system_prompt=enhanced_system_prompt
            ):
                yield chunk

        except Exception as e:
            logger.error(f"Error in stream_response_with_knowledge: {e}")
            yield f"[ERROR] Failed to generate response with knowledge: {str(e)}"

    def check_health(self) -> bool:
        """
        Check if Bedrock connection is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Create a simple bedrock client to list models
            bedrock_client = boto3.client(
                service_name="bedrock",
                region_name=self.settings.aws_region,
                aws_access_key_id=self.settings.aws_access_key_id,
                aws_secret_access_key=self.settings.aws_secret_access_key
            )

            # Try to list foundation models to verify connection
            response = bedrock_client.list_foundation_models(
                byProvider="Anthropic"
            )

            # Check if Claude 3.5 Sonnet is available
            models = response.get('modelSummaries', [])
            model_ids = [model.get('modelId') for model in models]

            # Verify our specific model is available
            if self.settings.bedrock_model_id in model_ids:
                logger.info("Bedrock health check: OK")
                return True
            else:
                logger.warning(f"Model {self.settings.bedrock_model_id} not found in available models")
                # Return True anyway if we can connect, just log the warning
                return True

        except Exception as e:
            logger.error(f"Bedrock health check failed: {e}")
            return False

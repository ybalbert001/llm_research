import json
import boto3
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterator,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
)
from langchain_core.outputs import GenerationChunk
import sys

AMAZON_BEDROCK_TRACE_KEY = "amazon-bedrock-trace"
GUARDRAILS_BODY_KEY = "amazon-bedrock-guardrailAssessment"
HUMAN_PROMPT = "\n\nHuman:"
ASSISTANT_PROMPT = "\n\nAssistant:"
ALTERNATION_ERROR = (
    "Error: Prompt must alternate between '\n\nHuman:' and '\n\nAssistant:'."
)

def _add_newlines_before_ha(input_text: str) -> str:
    new_text = input_text
    for word in ["Human:", "Assistant:"]:
        new_text = new_text.replace(word, "\n\n" + word)
        for i in range(2):
            new_text = new_text.replace("\n\n\n" + word, "\n\n" + word)
    return new_text

def _human_assistant_format(input_text: str) -> str:
    if input_text.count("Human:") == 0 or (
        input_text.find("Human:") > input_text.find("Assistant:")
        and "Assistant:" in input_text
    ):
        input_text = HUMAN_PROMPT + " " + input_text  # SILENT CORRECTION
    if input_text.count("Assistant:") == 0:
        input_text = input_text + ASSISTANT_PROMPT  # SILENT CORRECTION
    if input_text[: len("Human:")] == "Human:":
        input_text = "\n\n" + input_text
    input_text = _add_newlines_before_ha(input_text)
    count = 0
    # track alternation
    for i in range(len(input_text)):
        if input_text[i : i + len(HUMAN_PROMPT)] == HUMAN_PROMPT:
            if count % 2 == 0:
                count += 1
            else:
                warnings.warn(ALTERNATION_ERROR + f" Received {input_text}")
        if input_text[i : i + len(ASSISTANT_PROMPT)] == ASSISTANT_PROMPT:
            if count % 2 == 1:
                count += 1
            else:
                warnings.warn(ALTERNATION_ERROR + f" Received {input_text}")

    if count % 2 == 1:  # Only saw Human, no Assistant
        input_text = input_text + ASSISTANT_PROMPT  # SILENT CORRECTION

    return input_text

def _stream_response_to_generation_chunk(
    stream_response: Dict[str, Any],
) -> GenerationChunk:
    """Convert a stream response to a generation chunk."""
    if not stream_response["delta"]:
        return GenerationChunk(text="")
    return GenerationChunk(
        text=stream_response["delta"]["text"],
        generation_info=dict(
            finish_reason=stream_response.get("stop_reason", None),
        ),
    )

class LLMInputOutputAdapter:
    """Adapter class to prepare the inputs from Langchain to a format
    that LLM model expects.

    It also provides helper function to extract
    the generated text from the model response."""

    provider_to_output_key_map = {
        "anthropic": "completion",
        "amazon": "outputText",
        "cohere": "text",
        "meta": "generation",
        "mistral": "outputs",
    }

    @classmethod
    def prepare_input(
        cls,
        provider: str,
        model_kwargs: Dict[str, Any],
        prompt: Optional[str] = None,
        system: Optional[str] = None,
        messages: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        input_body = {**model_kwargs}
        if provider == "anthropic":
            if messages:
                input_body["anthropic_version"] = "bedrock-2023-05-31"
                input_body["messages"] = messages
                if system:
                    input_body["system"] = system
                if "max_tokens" not in input_body:
                    input_body["max_tokens"] = 1024
            if prompt:
                input_body["prompt"] = _human_assistant_format(prompt)
                if "max_tokens_to_sample" not in input_body:
                    input_body["max_tokens_to_sample"] = 1024
        elif provider in ("ai21", "cohere", "meta", "mistral"):
            input_body["prompt"] = prompt
        elif provider == "amazon":
            input_body = dict()
            input_body["inputText"] = prompt
            input_body["textGenerationConfig"] = {**model_kwargs}
        else:
            input_body["inputText"] = prompt

        return input_body

    @classmethod
    def prepare_output(cls, provider: str, response: Any) -> dict:
        if provider == "anthropic":
            response_body = json.loads(response.get("body").read().decode())
            if "completion" in response_body:
                text = response_body.get("completion")
            elif "content" in response_body:
                content = response_body.get("content")
                text = content[0].get("text")
        else:
            response_body = json.loads(response.get("body").read())

            if provider == "ai21":
                text = response_body.get("completions")[0].get("data").get("text")
            elif provider == "cohere":
                text = response_body.get("generations")[0].get("text")
            elif provider == "meta":
                text = response_body.get("generation")
            elif provider == "mistral":
                text = response_body.get("outputs")[0].get("text")
            else:
                text = response_body.get("results")[0].get("outputText")

        return {
            "text": text,
            "body": response_body,
        }

    @classmethod
    def prepare_output_stream(
        cls,
        provider: str,
        response: Any,
        stop: Optional[List[str]] = None,
        messages_api: bool = False,
    ) -> Iterator[GenerationChunk]:
        stream = response.get("body")

        if not stream:
            return

        if messages_api:
            output_key = "message"
        else:
            output_key = cls.provider_to_output_key_map.get(provider, "")

        if not output_key:
            raise ValueError(
                f"Unknown streaming response output key for provider: {provider}"
            )

        for event in stream:
            chunk = event.get("chunk")
            if not chunk:
                continue

            chunk_obj = json.loads(chunk.get("bytes").decode())

            if provider == "cohere" and (
                chunk_obj["is_finished"] or chunk_obj[output_key] == "<EOS_TOKEN>"
            ):
                return

            elif (
                provider == "mistral"
                and chunk_obj.get(output_key, [{}])[0].get("stop_reason", "") == "stop"
            ):
                return

            elif messages_api and (chunk_obj.get("type") == "content_block_stop"):
                return

            if messages_api and chunk_obj.get("type") in (
                "message_start",
                "content_block_start",
                "content_block_delta",
            ):
                if chunk_obj.get("type") == "content_block_delta":
                    chk = _stream_response_to_generation_chunk(chunk_obj)
                    yield chk
                else:
                    continue
            else:
                # chunk obj format varies with provider
                yield GenerationChunk(
                    text=(
                        chunk_obj[output_key]
                        if provider != "mistral"
                        else chunk_obj[output_key][0]["text"]
                    )
                )

    @classmethod
    async def aprepare_output_stream(
        cls, provider: str, response: Any, stop: Optional[List[str]] = None
    ) -> AsyncIterator[GenerationChunk]:
        stream = response.get("body")

        if not stream:
            return

        output_key = cls.provider_to_output_key_map.get(provider, None)

        if not output_key:
            raise ValueError(
                f"Unknown streaming response output key for provider: {provider}"
            )

        for event in stream:
            chunk = event.get("chunk")
            if not chunk:
                continue

            chunk_obj = json.loads(chunk.get("bytes").decode())

            if provider == "cohere" and (
                chunk_obj["is_finished"] or chunk_obj[output_key] == "<EOS_TOKEN>"
            ):
                return

            if (
                provider == "mistral"
                and chunk_obj.get(output_key, [{}])[0].get("stop_reason", "") == "stop"
            ):
                return

            yield GenerationChunk(
                text=(
                    chunk_obj[output_key]
                    if provider != "mistral"
                    else chunk_obj[output_key][0]["text"]
                )
            )

if __name__ == '__main__':
    provider = 'anthropic'
    prompt = None
    system = 'You are my girlfriend.'
    messages = [{"role": "user", "content": "what's your favorite today?"}]
    region = 'us-west-2'
    STOP = ["user:", "用户：", "用户:", '</response>']
    params = {
        'temperature' : 0.1, 
        'max_tokens' : 1024,
        'top_p' : 0.5,
        'top_k' : 4,
        'stop_sequences' : STOP
    }
    input_body = LLMInputOutputAdapter.prepare_input(
        provider=provider,
        prompt=prompt,
        system=system,
        messages=messages,
        model_kwargs=params,
    )
    body = json.dumps(input_body)

    request_options = {
        "body": body,
        "modelId": 'anthropic.claude-3-sonnet-20240229-v1:0',
        "accept": "application/json",
        "contentType": "application/json",
    }

    boto3_bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name=region
        )

    if len(sys.argv)==2 and sys.argv[1] == 'stream':
        try:
            response = boto3_bedrock.invoke_model_with_response_stream(**request_options)

        except Exception as e:
            raise ValueError(f"Error raised by bedrock service: {e}")

        for chunk in LLMInputOutputAdapter.prepare_output_stream(
            provider, response, STOP, True if messages else False
        ):
            print(chunk.text)
    else:
        try:
            response = boto3_bedrock.invoke_model(**request_options)
        except Exception as e:
            raise ValueError(f"Error raised by bedrock service: {e}")

        output = json.loads(response.get('body').read().decode("utf-8"))

        print(output['content'][0]['text'])
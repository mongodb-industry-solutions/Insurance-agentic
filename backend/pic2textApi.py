from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import boto3
import base64
import json
import os
from tempfile import NamedTemporaryFile
from typing import Optional


def stream_image_to_bedrock(image_path, model_id='anthropic.claude-3-sonnet-20240229-v1:0'):
    """
    Send an image to Amazon Bedrock and stream the response
    
    :param image_path: Path to the image file
    :param model_id: ID of the Bedrock model to use (default is Claude 3 Sonnet)
    :yield: Streamed chunks of the response
    """
    # Create a Bedrock Runtime client
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime', 
        region_name='us-east-1'  # Replace with your preferred AWS region
    )
    
    # Read the image file and encode it to base64
    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    # Get file extension to determine media type
    _, file_extension = os.path.splitext(image_path)
    media_type = "image/jpeg"  # Default
    if file_extension.lower() in ['.png']:
        media_type = "image/png"
    elif file_extension.lower() in ['.jpg', '.jpeg']:
        media_type = "image/jpeg"
    
    # Prepare the request payload
    request_body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": "What do you see in this image? Give a concise description and focus and what happened to vehicles."
                    }
                ]
            }
        ]
    })
    
    try:
        # Use invoke_model_with_response_stream for streaming
        response = bedrock_runtime.invoke_model_with_response_stream(
            modelId=model_id,
            body=request_body
        )
        
        # Stream the response
        for event in response['body']:
            chunk = event.get('chunk')
            if chunk:
                decoded_chunk = json.loads(chunk.get('bytes').decode('utf-8'))
                
                # Check for text in the streamed response
                if decoded_chunk.get('type') == 'content_block_delta':
                    yield decoded_chunk['delta']['text']
                
                # Check for end of stream or completion
                if decoded_chunk.get('type') == 'message_stop':
                    break
    
    except Exception as e:
        print(f"Error streaming image to Bedrock: {e}")
        yield f"Error: {str(e)}"
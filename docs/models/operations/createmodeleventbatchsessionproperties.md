# CreateModelEventBatchSessionProperties


## Fields

| Field                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Type                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Required                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Example                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model_event`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | [Optional[components.SessionPropertiesBatch]](../../models/components/sessionpropertiesbatch.md)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | :heavy_minus_sign:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | N/A                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | {<br/>"source": "playground",<br/>"session_name": "Playground Session",<br/>"session_id": "caf77ace-3417-4da4-944d-f4a0688f3c23",<br/>"inputs": {<br/>"context": "Hello world",<br/>"question": "What is in the context?",<br/>"chat_history": [<br/>{<br/>"role": "system",<br/>"content": "Answer the user's question only using provided context.\n\nContext: Hello world"<br/>},<br/>{<br/>"role": "user",<br/>"content": "What is in the context?"<br/>}<br/>]<br/>},<br/>"outputs": {<br/>"role": "assistant",<br/>"content": "Hello world"<br/>},<br/>"error": null,<br/>"metrics": {},<br/>"feedback": {},<br/>"metadata": {},<br/>"user_properties": {<br/>"user": "google-oauth2\|111840237613341303366"<br/>}<br/>} |
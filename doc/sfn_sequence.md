### Events Sequence

```mermaid
sequenceDiagram
    actor Starter Lambda 
   
    
    Starter Lambda->>Sfn State Machine: stepfunction.start_execution()
    activate Sfn State Machine
    Sfn State Machine->>Starter Lambda: return
    deactivate Sfn State Machine
    
    Sfn State Machine->>sfn_get_instance_id (Lambda): lambda:invoke
    activate sfn_get_instance_id (Lambda)
    sfn_get_instance_id (Lambda)->>Sfn State Machine: Instance Id
    deactivate sfn_get_instance_id (Lambda)

    Sfn State Machine->>sfn_job_execute (Lambda): lambda:invoke
    sfn_job_execute (Lambda)->>Sfn State Machine: return
            
    sfn_job_execute (Lambda)->>SSM RunCommand: ssm.send_command
    SSM RunCommand->>Instance: RunCommand
    activate Instance


    Sfn State Machine->>sfn_receive_callback_token (Lambda): lambda:invoke
    activate Sfn State Machine
    sfn_receive_callback_token (Lambda)->>DynamoDB: Callback Token
    sfn_receive_callback_token (Lambda)->>Sfn State Machine: return
    

    Instance--)(CloudWatch Logs): complete log
    deactivate Instance
    (CloudWatch Logs)--)(Lambda): log event

    Note over Sfn State Machine: Wait Callback Token


    (Lambda)--)DynamoDB: get Callback Token

    (Lambda)--)Sfn State Machine: send Callback Token
    deactivate Sfn State Machine

    Note over Sfn State Machine: ChoiceCallbackResult
    
    Note over Sfn State Machine: SfnSucceedState

        
```


```mermaid
sequenceDiagram
    actor Starter Lambda 
    
    Starter Lambda->>Sfn State Machine: stepfunction.start_execution()
    activate Sfn State Machine
    Sfn State Machine->>Starter Lambda: return
    deactivate Sfn State Machine
    
    Sfn State Machine->>sfn_get_instance_id (Lambda): lambda:invoke
    activate sfn_get_instance_id (Lambda)
    sfn_get_instance_id (Lambda)->>Sfn State Machine: Instance Id
    deactivate sfn_get_instance_id (Lambda)

    Sfn State Machine->>sfn_job_execute (Lambda): lambda:invoke
    sfn_job_execute (Lambda)->>Sfn State Machine: return
        
    
    sfn_job_execute (Lambda)->>SSM RunCommand: ssm.send_command
    SSM RunCommand->>Instance: RunCommand
    activate Instance

    Sfn State Machine->>sfn_receive_callback_token (Lambda): lambda:invoke
    activate Sfn State Machine
    sfn_receive_callback_token (Lambda)->>DynamoDB: Callback Token
    sfn_receive_callback_token (Lambda)->>Sfn State Machine: return
    


    Instance--)(CloudWatch Logs): complete log
    deactivate Instance
    (CloudWatch Logs)--)(Lambda): log event

    Note over Sfn State Machine: Wait Callback Token


    (Lambda)--)DynamoDB: get Callback Token

    (Lambda)--)Sfn State Machine: send Callback Token
    deactivate Sfn State Machine

    Note over Sfn State Machine: ChoiceCallbackResult
    
    Note over Sfn State Machine: SfnSucceedState
        
```

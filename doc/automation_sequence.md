### Events Sequence

```mermaid
sequenceDiagram
    actor Starter Lambda 
    
    %% Start
    Starter Lambda->>SSM Automation: ssm.start_automation_execution()
    activate SSM Automation
    SSM Automation-->>Starter Lambda: return
    deactivate SSM Automation

    %% get_instance_id()
    SSM Automation->>getInstanceId (Lambda): aws:invokeLambdaFunction
    activate getInstanceId (Lambda)
    Note left of SSM Automation: Select Instance<br/>(invoke Lambda function)
    getInstanceId (Lambda)-->>SSM Automation: Instance Id
    deactivate getInstanceId (Lambda)
         
    %% WaitUntilRunning
    SSM Automation->>EC2 Service: DescribeInstances()
    activate EC2 Service
    Note left of SSM Automation: wait for instance running
    EC2 Service-->>SSM Automation: return    
    deactivate EC2 Service

        
    %% SSM RunCommand
    SSM Automation->>Instance: RunCommand()
    activate Instance
    Note left of SSM Automation: Run Command
    Note right of Instance: 同期
    Instance-->>SSM Automation: return output
    deactivate Instance
    
    Note over SSM Automation: Output        
```


```mermaid
sequenceDiagram
    actor Starter Lambda 
    
    Starter Lambda->>SSM Automation: ssm.start_automation_execution()
    activate SSM Automation
    SSM Automation-->>Starter Lambda: return
    deactivate SSM Automation

    SSM Automation->>getInstanceId (Lambda): aws:invokeLambdaFunction
    activate getInstanceId (Lambda)
    getInstanceId (Lambda)-->>SSM Automation: Instance Id
    deactivate getInstanceId (Lambda)
    
    SSM Automation->>WaitUntilRunning: DescribeInstances()
    activate WaitUntilRunning
    Note over SSM Automation,WaitUntilRunning: wait for instance running
    WaitUntilRunning-->>SSM Automation: return
    deactivate WaitUntilRunning
        
    SSM Automation->>Instance: RunCommand()
    activate Instance
    Note right of Instance: 同期
    Instance-->>SSM Automation: return output
    deactivate Instance
    
    Note over SSM Automation: Output
        
```

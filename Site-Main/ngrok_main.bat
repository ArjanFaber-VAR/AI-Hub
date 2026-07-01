@echo off

start cmd /k ngrok http --url=var-ai-tool.ngrok.app 4001  
start cmd /k ngrok http --url=myappf2.ngrok.app 5000   
start cmd /k ngrok http --url=myvarf3agent.ngrok.app 5001 

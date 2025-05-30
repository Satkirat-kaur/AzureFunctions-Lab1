# Azure Functions Lab 1 – Queue and SQL Output Bindings

## Student: Satkirat Kaur  
**Course:** CST8917
**Lab Title:** Lab 1: Building Azure Function Apps with Output Bindings  

---

## Lab Overview

This lab demonstrates two serverless Azure Functions using Python:

- **Part 1:** Azure Queue Storage Output Binding
- **Part 2:** Azure SQL Database Output Binding

Both functions were developed and tested locally using VS Code and deployed to Azure.

---

## Part 1: Azure Queue Output Binding

### Goal

Trigger an HTTP function and send a message to an Azure Storage Queue named `myqueue`.

### Steps Followed

1. **Created a Python (Isolated) Azure Function Project** using VS Code.
2. Added an HTTP-triggered function: `QueueOutputFunction`.
3. Added an **output binding** for Azure Queue Storage using:
```python
   @app.queue_output(arg_name="msg", queue_name="myqueue", connection="AzureWebJobsStorage")
```
4. Implemented logic to capture `name` from the request and push a message to the Azure Queue.

5. Ran and tested the function locally using the following `curl` command:

```bash
   curl http://localhost:7071/api/queueoutput?name=AzureStudent
```
6.	Verified message in Azure Queue via Azure Storage Explorer.
   ![Azure Storage Explorer output](https://github.com/Satkirat-kaur/AzureFunctions-Lab1/blob/main/Screenshots/queue%20output%20in%20azure%20explorer.png)
8.	Deployed to Azure:
```bash
https://queueoutputfunction2.azurewebsites.net/api/queueoutput?name=AzureStudent
```
![Browser Output for Part 1](https://github.com/Satkirat-kaur/AzureFunctions-Lab1/blob/main/Screenshots/Output%201.png)
## Part 2: Azure SQL Output Binding

## Goal of this part of the lab:
Trigger an HTTP Azure Function and insert data into an Azure SQL Database table `dbo.ToDo`.

---

## Steps Followed

1. Created a new Azure SQL Database named `queueoutputdatabase` with a server `queueoutputserver`.

2. Created the `ToDo` table using the following SQL schema:

```sql
   CREATE TABLE dbo.ToDo (
       [Id] UNIQUEIDENTIFIER PRIMARY KEY,
       [order] INT NULL,
       [title] NVARCHAR(200) NOT NULL,
       [url] NVARCHAR(200) NOT NULL,
       [completed] BIT NOT NULL
   );
```

3. Added a new function `AddToDoSql` in `function_app.py` with the SQL output binding:

```python
   @app.sql_output(
       arg_name="todo",
       command_text="dbo.ToDo",
       connection_string_setting="SqlConnectionString"
   )
```

4. Created a valid `SqlConnectionString` using ADO.NET format and added it to:
   - `local.settings.json` for local testing
   - Azure Function App → **Configuration** section for deployment

5. Allow the client IP address in the **SQL Server firewall** to enable access.

6. Ran and tested the function locally using the following `curl` command:

```bash
   curl -X POST http://localhost:7071/api/addtodo \
     -H "Content-Type: application/json" \
     -d '{
       "order": 1,
       "title": "Complete Lab 1",
       "url": "http://example.com",
       "completed": false
     }'
```
![terminal for curl command](https://github.com/Satkirat-kaur/AzureFunctions-Lab1/blob/main/Screenshots/item%20added%20to%20sql%20table%20via%20vs%20code%20terminal.png)

7. Verified that the row was inserted into the Azure SQL Database using the following SQL query:

```sql
   SELECT * FROM dbo.ToDo;
```
![SQL Output](https://github.com/Satkirat-kaur/AzureFunctions-Lab1/blob/main/Screenshots/sql%20query%20output%20in%20azure.png)

8. Deployed to Azure and tested live:

   `https://queueoutputfunction2.azurewebsites.net/api/addtodo?code=<function-key>`

   ![Function running in terminal](https://github.com/Satkirat-kaur/AzureFunctions-Lab1/blob/main/Screenshots/Terminal%20output%20for%20func%20start%20for%20step%202.png)

## Source Code – function_app.py

```python
import azure.functions as func
import json
import uuid

app = func.FunctionApp()

# --------------------------
# Queue Output Function
# --------------------------

@app.function_name(name="QueueOutputFunction")
@app.route(route="queueoutput")
@app.queue_output(
    arg_name="msg",
    queue_name="myqueue",
    connection="AzureWebJobsStorage"
)
def queue_output(req: func.HttpRequest, msg: func.Out[str]) -> func.HttpResponse:
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
            name = req_body.get('name')
        except ValueError:
            name = None

    if name:
        message = json.dumps({"name": name})
        msg.set(message)
        return func.HttpResponse(f"✅ Message '{message}' sent to the queue.")
    else:
        return func.HttpResponse("⚠️ Please pass a name in the query string or body.", status_code=400)

# --------------------------
# SQL Output Function
# --------------------------

@app.function_name(name="AddToDoSql")
@app.route(route="addtodo")
@app.sql_output(
    arg_name="todo",
    command_text="dbo.ToDo",  # Make sure table dbo.ToDo exists
    connection_string_setting="SqlConnectionString"  # Define this in local.settings.json
)
def add_to_sql(req: func.HttpRequest, todo: func.Out[func.SqlRow]) -> func.HttpResponse:
    try:
        req_body = req.get_json()

        row = func.SqlRow.from_dict({
            "Id": str(uuid.uuid4()),
            "order": req_body.get("order"),
            "title": req_body.get("title"),
            "url": req_body.get("url"),
            "completed": req_body.get("completed", False)
        })

        todo.set(row)
        return func.HttpResponse("✅ ToDo item added to SQL database.", status_code=201)

    except Exception as e:
        return func.HttpResponse(f"❌ Error: {str(e)}", status_code=400)
```

## Demo video

'https://youtu.be/vRjqIU--Wac'


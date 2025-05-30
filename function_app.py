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

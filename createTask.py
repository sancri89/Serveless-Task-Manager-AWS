# Serveless-Task-Manager-AWS
Serverless AWS task app with Cognito, API Gateway, Lambda, DynamoDB, and SNS
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/Tasks"
    },
    {
      "Effect": "Allow",
      "Action": "sns:Publish",
      "Resource": "arn:aws:sns:REGION:ACCOUNT_ID:task-notifications"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Task Manager</title>
</head>
<body>
  <div id="app">
    <h1>Task Manager</h1>

    <button id="loginBtn">Sign in</button>

    <div id="tasks" style="display: none;">
      <input id="taskTitle" placeholder="New task" maxlength="200">
      <button id="addTaskBtn">Add task</button>

      <p id="message"></p>
      <ul id="taskList"></ul>
    </div>
  </div>

  <script>
    const COGNITO_DOMAIN =
      "https://us-east-12cvj5e1hs.auth.us-east-1.amazoncognito.com";

    const CLIENT_ID = "5bi9s6j0d0v6lrqccqau592s90";

    const REDIRECT_URI = window.location.origin;

    const API_BASE =
      "https://vgfrvhxec0.execute-api.us-east-1.amazonaws.com/";

    function getTokensFromUrl() {
      const hash = window.location.hash.substring(1);
      const params = new URLSearchParams(hash);

      return {
        idToken: params.get("id_token"),
        accessToken: params.get("access_token")
      };
    }

    function showMessage(message) {
      document.getElementById("message").textContent = message;
    }

    document.getElementById("loginBtn").onclick = () => {
      const loginUrl =
        `${COGNITO_DOMAIN}/login` +
        `?client_id=${CLIENT_ID}` +
        `&response_type=token` +
        `&scope=openid+email` +
        `&redirect_uri=${encodeURIComponent(REDIRECT_URI)}`;

      window.location.href = loginUrl;
    };

    const { accessToken } = getTokensFromUrl();
    const token = accessToken;

    if (token) {
      document.getElementById("loginBtn").style.display = "none";
      document.getElementById("tasks").style.display = "block";
      loadTasks();
    }

    async function loadTasks() {
      try {
        const res = await fetch(`${API_BASE}/tasks`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        if (!res.ok) {
          throw new Error(`Could not load tasks: HTTP ${res.status}`);
        }

        const items = await res.json();

        document.getElementById("taskList").innerHTML =
          items.map(item => `<li>${item.title}</li>`).join("");

      } catch (error) {
        showMessage(error.message);
        console.error(error);
      }
    }

    document.getElementById("addTaskBtn").onclick = async () => {
      const input = document.getElementById("taskTitle");
      const title = input.value.trim();

      if (!title) {
        showMessage("Enter a task title first.");
        return;
      }

      try {
        const res = await fetch(`${API_BASE}/tasks`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ title })
        });

        if (!res.ok) {
          const errorBody = await res.text();
          throw new Error(
            `Could not create task: HTTP ${res.status} ${errorBody}`
          );
        }

        input.value = "";
        showMessage("Task created.");
        await loadTasks();

      } catch (error) {
        showMessage(error.message);
        console.error(error);
      }
    };
  </script>
</body>
</html>
import json, os, boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    claims = event['requestContext']['authorizer']['jwt']['claims']
    user_id = claims['sub']

    response = table.query(
        KeyConditionExpression=Key('userId').eq(user_id)
    )

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(response.get('Items', []))
    }

import json, os, time, uuid, boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])
sns = boto3.client('sns')

def lambda_handler(event, context):
    claims = event['requestContext']['authorizer']['jwt']['claims']
    user_id = claims['sub']
    body = json.loads(event.get('body') or '{}')
    title = body.get('title', '').strip()

    if not title:
        return {'statusCode': 400, 'body': json.dumps({'error': 'title is required'})}

    task_id = str(uuid.uuid4())
    item = {
        'userId': user_id,
        'taskId': task_id,
        'title': title,
        'createdAt': int(time.time()),
        'done': False,
    }
    table.put_item(Item=item)

    topic_arn = os.environ.get('TOPIC_ARN')
    if topic_arn:
        sns.publish(
            TopicArn=topic_arn,
            Subject='New task created',
            Message=f"User {claims.get('email', user_id)} created a task: {title}"
        )

    return {
        'statusCode': 201,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(item)
    }

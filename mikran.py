import os,json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
import db
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.message("nz")
def new_order(message, say):
    say(f"Nowe zamówienie")
    db.new_order()

@app.message("lz")
def orders_list(message, say):
    lzs = db.orders_list()
    blocks = []
    for lz in lzs:
        info = "Zamówienie z %s, nr (%s) dla %s. Utworzył %s" % (lz['date'],lz['order_id'],lz['customer_id'],lz['user'])
        block = {
            "type": "section",
            #"text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
            "text": {"type": "mrkdwn", "text": info},
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "Edutuj zamówienie"},
                "action_id": "button_click",
                "value":lz['order_id']
            }
        }
        blocks.append(block)
        if lz['comment']:
            block = {
                "type": "section",
                "text": {"type": "mrkdwn", "text": " > _%s_" % lz['comment']},
            }
            
            blocks.append(block)

    say(blocks=blocks)

@app.action("button_click")
def action_button_click(body, ack, say):
    print(json.dumps(body['actions'], indent=4, sort_keys=True))
    order_id = body['actions'][0]['value']
    order = db.get_order(order_id)
    ack()
    client.views_open(
        # Pass a valid trigger_id within 3 seconds of receiving it
        trigger_id=body['trigger_id'],
        # View payload
        view = {
	    "type": "modal",
	    "title": {
	        "type": "plain_text",
		"text": "Zamówienie %s" % order_id,
		"emoji": True
	    },
	    "submit": {
	        "type": "plain_text",
		"text": "Submit",
		"emoji": True
	    },
	    "close": {
	        "type": "plain_text",
	        "text": "Cancel",
	        "emoji": True
	    },
	    "blocks": [
                {
		    "type": "section",
		    "text": {
		        "type": "mrkdwn",
		        "text": "To jest zamówienie  %s " % str(order)
                    },
		    "accessory": {
		        "type": "image",
                        "image_url":"https://i.ytimg.com/vi/O-q9qi2F5yk/hqdefault.jpg",
		        "alt_text": "cute cat"
		    }
		}
	    ]
        }
    )
            

# Start your app
if __name__ == "__main__":
    db.init_db()
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

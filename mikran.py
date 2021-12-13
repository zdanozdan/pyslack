import os,json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
import db
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.command("/nowe-zamowienie")
#def test_command(body, client, ack, logger):
def new_order_command(body, ack, respond, client, logger):
    order = db.new_order()
    ack(
        text="Poszło!",
        blocks=[
            {
                "type": "section",
                "block_id": "b",
                "text": {
                    "type": "mrkdwn",
                    "text": ":white_check_mark: Accepted!",
                },
            }
        ],
    )

    respond(
        blocks=[
            {
                "type": "section",
                "block_id": "b",
                "text": {
                    "type": "mrkdwn",
                    "text": ":white_check_mark: Nowe zamówienie utworzone. ",
                },
                "accessory": {
                    "type": "button",
                    "action_id": "nowe-zamowienie",
                    "text": {"type": "plain_text", "text": "Edytuj zamówienie"},
                    "action_id": "button_click",
                    "value":order['order_id']
                },
            }
        ]
    )

@app.command("/nowe-zamowienie-x")
def handle_orders_list(ack, body, logger):
    #ack(f"Tworzę nowe zamówienie")
    #order = db.new_order()
    #info = "Zamówienie z %s, nr (%s) dla %s. Utworzył %s" % (order['date'],order['order_id'],order['customer_id'],order['user'])
    #ack(info)

    block = {
        "blocks": [
            {
		"type": "section",
		"text": {
		    "type": "plain_text",
		    "text": "This is a plain text section block.",
		    "emoji": True
		}
	    },
	    {
	        "type": "divider"
	    },
        ]
    }
        

    #print(block)
    ack(blocks=[block,])

@app.command("/lista-zamowien")
def handle_orders_list(ack, body, logger):
#    print(body)
#def orders_list(message, say):
    lzs = db.orders_list()
    blocks = []
    for order in lzs:
        info = "Zamówienie z %s, nr (%s) dla %s. Utworzył %s" % (order['date'],order['order_id'],order['customer_id'],order['user'])
        block = {
            "type": "section",
            #"text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
            "text": {"type": "mrkdwn", "text": info},
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "Edutuj zamówienie"},
                "action_id": "button_click",
                "value":order['order_id']
            }
        }
        blocks.append(block)
        if order['comment']:
            block = {
                "type": "section",
                "text": {"type": "mrkdwn", "text": " > _%s_" % order['comment']},
            }
            
            blocks.append(block)

    ack(blocks=blocks)

@app.action("button_click")
def action_button_click(body, ack, say):
    #print(json.dumps(body['actions'], indent=4, sort_keys=True))
    order_id = body['actions'][0]['value']
    order = db.get_order(order_id)
    ack()
    client.views_open(
        # Pass a valid trigger_id within 3 seconds of receiving it
        trigger_id=body['trigger_id'],
        # View payload
        view = {
	    "type": "modal",
            "callback_id": "view-id",
	    "title": {
	        "type": "plain_text",
		"text": "Zamówienie %s" % order_id,
		"emoji": True
	    },
	    "submit": {
	        "type": "plain_text",
		"text": "Zapisz",
		"emoji": True
	    },
	    "close": {
	        "type": "plain_text",
	        "text": "Anuluj",
	        "emoji": True
	    },
	    "blocks": [
                {
                    "type":"input",
                    "block_id":"find-customer",
                    "element":{
			"type": "external_select",
                        "action_id": "action-find-customer",
			"placeholder": {"type": "plain_text","text": "Znajdź kontrahenta",},
                        "min_query_length": 3,
		    },
                    "label": {"type": "plain_text", "text": "Wyszukaj kontrahenta"},
                },
                {
                    "type": "input",
                    "block_id": "mes_b",
                    "element": {
                        "type": "multi_external_select",
                        "action_id": "action-find-product",
                        "placeholder": {"type": "plain_text", "text": "Wybierz produkt"},
                        "min_query_length": 3,
                    },
                    "label": {"type": "plain_text", "text": "Wyszukaj produkt"},
                },
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
                },
                {
                    "type": "divider",
	        },
                {
		    "type": "section",
		    "text": {
			"type": "mrkdwn",
			"text": "Usuń"
		    },
                    "accessory": {
                        "type": "checkboxes",
			"options": [
			    {
				"text": {
				    "type": "mrkdwn",
				    "text": "*Usuń*"
				},
				"description": {
				    "type": "mrkdwn",
				    "text": "*Zaznacz żeby usunąć to zamówinie i zapisz*"
				},
				"value": order_id,
			    },
			],
                        "action_id": "checkbox-delete-action"
		    }
		}
	    ]
        }
    )

@app.options("action-find-product")
def show_multi_options(ack):
    ack(
        {
            "option_groups": [
                {
                    "label": {"type": "plain_text", "text": "Group 1"},
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "produkt #1"},
                            "value": "1-1",
                        },
                        {
                            "text": {"type": "plain_text", "text": "produkt #2"},
                            "value": "1-2",
                        },
                    ],
                },
                {
                    "label": {"type": "plain_text", "text": "Group 2"},
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "#produkt 1. Produkt z bardzo dlugim opisem, nazwa, PLU, stan magazynowy, "},
                            "value": "2-1",
                        },
                    ],
                },
            ]
        }
    )

@app.view("view-id")
def view_submission(ack, body, logger):
    ack({"response_action": "clear"})
    #print(json.dumps(body['view']['state']['values'], indent=4, sort_keys=True))
    values = body['view']['state']['values']
    for key,value in values.items():
        try:
            checkbox = value['checkbox-delete-action']
            if len(checkbox['selected_options']) > 0:
                order_id = checkbox['selected_options'][0]['value']
                db.delete_order(order_id)
                ack({
                    "response_action": "update",
                    "view": {
                        "type": "modal",
                        "title": {
                            "type": "plain_text",
                            "text": "Updated view"
                        },
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "plain_text",
                                "text": "Naprawdę zmieniłem się i nigdy nie będe taki sam !"
                            }
                        }
                    ]
                    }
                })
        except:
            pass


@app.options("action-find-customer")
def handle_some_options(ack):
    ack(
        {
            "options": [
                {
                    "text": {
                        "type": "plain_text","text": "Unexpected sentience",
                    },
                    "value": "v1"
                },
                {
                    "text": {
                        "type": "plain_text", "text": "Bot biased toward other bots"
                    },
                    "value": "v2"
                },
                {
                    "text": {
                        "type": "plain_text", "text": "Bot broke my toaster, Bot biased toward other bots."
                    },
                    "value": "v3"
                }
            ]
        }
    )


# Start your app
if __name__ == "__main__":
    db.init_db()
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

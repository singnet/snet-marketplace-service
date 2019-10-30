NETWORKS = {'db': {"HOST": "localhost",
                   "USER": "root",
                   "PASSWORD": "password",
                   "NAME": "pub_sub",
                   "PORT": 3306,
                   }
            }

NET_ID = 3

EVENT_SUBSCRIPTIONS = {"OrganizationCreated": [{"name": "", "type": "webhook", "url": "https://subsribedpai1"},{"tyoe": "lambda_arn", "url": "https://subsribedpai1"}]}

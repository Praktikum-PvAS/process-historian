import opcua


class SubscriptionHandler:
    def __init__(self):
        self.data_callback = callable()

    def datachange_notification(self, node: opcua.Node, value, raw_data):
        # TODO
        pass

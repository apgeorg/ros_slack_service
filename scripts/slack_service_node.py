#!/usr/bin/env python

import os
import json
import requests
import rospy
from slack_service.srv import POSTRequestMessage, POSTRequestMessageResponse


class SlackService:

    def __init__(self, name):
        # Init ROS node
        rospy.init_node(name)
        rospy.loginfo('{} node started...'.format(rospy.get_name()))
        # Configuration parameterss
        self._webhook = rospy.get_param('~webhook', os.environ["SLACK_WEBHOOK"])
        self._channel = rospy.get_param('~channel', '#general')
        self._username = rospy.get_param('~username', 'bot')
        if not self._webhook:
            raise ValueError('Must provide Slack webhook. Can use environment variable "SLACK_WEBHOOK".')
        # Define service
        self.post_message_srv = rospy.Service(rospy.get_name()+'/post_request', POSTRequestMessage, self.post_request)
        

    # Service handler
    def post_request(self, request):
        if request.text and isinstance(request.text, str):
            channel = request.channel if request.channel else self._channel
            data = {'username': self._username, 'channel': channel, 'text': request.text}
            response = requests.post(self._webhook, data=json.dumps(data))
            success = False if response.status_code != 200 else True
            if not success:
                rospy.logerr('Error {} occured on request. {}'.format(response.status_code, response.text))
            return POSTRequestMessageResponse(success)
        return POSTRequestMessageResponse(False)


if __name__ == '__main__':
    try:
        SlackService(name="slack")
        rospy.spin()
    except rospy.ROSInterruptException as e:
        rospy.logerr(e)

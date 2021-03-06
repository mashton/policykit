import logging

import requests
from django.conf import settings
from integrations.metagov.models import MetagovProcess, MetagovProcessData

logger = logging.getLogger(__name__)

class Metagov:
    """
    Metagov client library to be exposed to policy author
    """

    def __init__(self, policy, action):
        self.policy = policy
        self.action = action
        self.headers = {"X-Metagov-Community": policy.community.metagov_slug}

        # If a GovernanceProcess is created for this Policy+Action evaluation, it will be attached here
        if action.action_type == "PlatformAction":
            try:
                self.process = MetagovProcess.objects.get(policy=policy, action=action)
            except MetagovProcess.DoesNotExist:
                self.process = None
        else:
            self.process = None

    def start_process(self, process_name, payload) -> MetagovProcessData:
        """
        Kick off a governance process in Metagov. The process is tied to this policy evaluation for this action.
        """
        model = MetagovProcess.objects.create(policy=self.policy, action=self.action)

        logger.info(f"Starting Metagov process '{process_name}' for {self.action} governed by {self.policy}")
        logger.info(payload)

        url = f"{settings.METAGOV_URL}/api/internal/process/{process_name}"
        payload["callback_url"] = f"{settings.SERVER_URL}/metagov/internal/outcome/{model.pk}"

        # Kick off process in Metagov
        response = requests.post(url, json=payload, headers=self.headers)
        if not response.ok:
            model.delete()
            raise Exception(f"Error starting process: {response.status_code} {response.reason} {response.text}")
        location = response.headers.get("location")
        if not location:
            model.delete()
            raise Exception("Response missing location header")

        model.location = f"{settings.METAGOV_URL}{location}"

        response = requests.get(model.location)
        if not response.ok:
            raise Exception(f"Error getting process: {response.status_code} {response.reason} {response.text}")
        logger.info(response.text)
        model.json_data = response.text
        model.save()
        self.process = model
        return model.data

    def close_process(self) -> MetagovProcessData:
        if self.process:
            self.process.close()
            return self.process.data
        return None

    def get_process(self) -> MetagovProcessData:
        if self.process:
            return self.process.data
        return None

    def perform_action(self, action_type, parameters):
        """
        Perform an action through Metagov. If the requested action belongs to a plugin that is
        not active for the current community, this will throw an exception.
        """
        url = f"{settings.METAGOV_URL}/api/internal/action/{action_type}"
        response = requests.post(url, json={"parameters": parameters}, headers=self.headers)
        if not response.ok:
            raise Exception(
                f"Error performing action {action_type}: {response.status_code} {response.reason} {response.text}"
            )
        data = response.json()
        return data

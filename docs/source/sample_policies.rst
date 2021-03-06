.. _start:


Sample Policies
###############

This is a library of example Platform Policies to get started.

Slack Policies
==============

Vote on renaming a channel
--------------------------

**Filter:**

.. code-block:: python

  return action.action_codename == "slackrenameconversation"

**Initialize:** ``pass``

**Check:**

.. code-block:: python

  yes_votes = action.proposal.get_yes_votes().count()
  no_votes = action.proposal.get_no_votes().count()
  debug(f"{yes_votes} for, {no_votes} against")
  if yes_votes >= 1:
    return PASSED
  elif no_votes >= 1:
    return FAILED

  debug("No votes yet....")
  return None

**Notify:**

.. code-block:: python

  message = f"Should this channel be renamed to #{action.name}? Vote with :thumbsup: or :thumbsdown: on this post."
  action.community.initiate_vote(action, policy, template=message)

**Pass:**

.. code-block:: python

  text = f"Proposal to rename this channel to #{action.name} passed."
  action.community.post_message(text=text, channel=action.channel, thread_ts=action.community_post)
  action.execute()

**Fail:**

.. code-block:: python

  text = f"Proposal to rename this channel to #{action.name} failed."
  action.community.post_message(text=text, channel=action.channel, thread_ts=action.community_post)


Don't allow posts in channel
----------------------------

This could be extended to add any logic to determine who can post in a given channel.
Posts in the channel are auto-deleted, and the user is notified about why it happened.

**Filter:**

.. code-block:: python

  return action.action_codename == "slackpostmessage" and action.channel == "ABC123"

**Initialize:** ``pass``

**Check:** ``return FAILED``

**Notify:** ``pass``

**Pass:** ``pass``

**Fail:**

.. code-block:: python

  # create an ephemeral post that is only visible to the poster
  message = f"Post was deleted because of policy '{policy.name}'"
  action.community.post_message(
    channel=action.channel,
    users=[action.initiator],
    post_type="ephemeral",
    template=message
  )


Discourse Policies
==================

Add examples here

Discord Policies
================

Message Filter
---------------------------

In this tutorial, we will introduce policy creation by creating a policy that filters messages for a set of banned words.

::

 Note: In this tutorial, and the following tutorials, we will make use of the DiscordIntegration.
 If you are new to PolicyKit, we recommend following along in the DiscordIntegration so as not to
 become lost. However, it shouldn't pose too much of a challenge to emulate the steps in this
 tutorial in another integration, if you are up to the task.

To begin, we must log into the PolicyKit dashboard. You can use either our test server at `https://policykit.org/main/ <https://policykit.org/main/>`_ or your own custom PolicyKit server. To set up PolicyKit with your local Discord guild, please see our tutorial on setting up PolicyKit with Discord. Once you have finished setting up PolicyKit with Discord, you should install PolicyKit to your Discord server. For practice purposes, you should use the Testing starter kit, as it will allow you to instantly pass any policy you propose. When you have installed PolicyKit to your Discord server, you can sign in with Discord to view the PolicyKit dashboard.

From there, you should click the Propose Action button on the top right of the dashboard. On the following Actions screen, you should click the Platform Policies menu to drop down the list of platform policy actions. Select the Add Platform Policy option to view the Policy Editor.

Finally, you will be on the Policy Editor page, and we can begin creating our policy! First, choose a name and description for your policy. You can leave the description blank if you wish.

In PolicyKit, incoming actions are checked against the Filter block of each active policy. Each policy is only executed on the action if the policy's Filter block returns True. The Filter block returns False by default.

We only want our Message Filter policy to run on actions which are messages posted to the Discord channel we are monitoring. To check if the action is a posted message, we can check a property of the ``action`` object called ``action_codename``. The codename for posting a message on Discord is ``"discordpostmessage"``. Thus, our Filter block is::

  if action.action_codename == "discordpostmessage":
    return True

We want to check all posted messages to see if they contain any blacklisted words. For example, suppose we want to ban the words "minecraft", "amazon", and "facebook" (due to repeated spam). In the Check block of the policy, we can check the ``text`` property of the ``action`` object and see if a substring of the text is a banned word. If so, the policy will fail the action (``return FAILED``). Otherwise, it will pass the action (``return PASSED``). If we don't return anything, ``PROPOSED`` will be returned by default, representing an intermediate state. Our Check block is::

  for banned_word in ["minecraft", "amazon", "facebook"]:
    if banned_word in action.text:
      return FAILED
  return PASSED

All other fields can be left as their defaults; there is no need to modify them. Once you have finished typing this code into the policy editor, click "Propose Policy" to propose the policy to your community. Once it passes, try it out! See how you can extend the policy further. A couple ideas:
 * Check ``action.text`` against Google's Perspective API (which checks for spam, hate speech, etc.).
 * Instead of removing posts which violate the Message Filter, allow the community to vote on whether the post should be shown. Or wait for moderator approval before displaying the post.

Great job! You have created your first policy.

Dice Rolling
------------------

This will allow the user to roll a dice by typing the following command:
     !roll d[num_faces] +[num_modifier]
where num refers to a positive non-zero integer value. This command simulates rolling a dice with num_faces faces (e.g. d100 is a dice with 100 faces). The user can optionally add a modifier, which adds an integer value to the result of the dice roll. For example, +7 would add 7 to the result of the dice roll.

**Filter:**

.. code-block:: python

  if action.action_type != "DiscordPostMessage":
    return False
  tokens = action.text.split()
  if tokens[0] != "!roll":
    return False
  if len(tokens) < 2 or len(tokens) > 3:
    action.community.post_message(text='not right number of tokens: should be 2 or 3', channel = "733209360549019688")
    return False
  return True

**Initialize:** ``pass``

**Check:**

.. code-block:: python

  import random
  tokens = action.text.split()
  channel = 733209360549019691
  if tokens[1][0] != "d":
    action.community.post_message(text='not have d', channel=channel)
    return FAILED
  if tokens[1][1:].isnumeric() == False:
    action.community.post_message(text='not numeric num faces', channel=channel)
    return FAILED
  num_faces = int(tokens[1][1:])
  num_modifier = 0
  if len(tokens) == 3:
    if tokens[2][0] != "+":
      action.community.post_message(text='not have +', channel=channel)
      return FAILED
    if tokens[2][1:].isnumeric() == False:
      action.community.post_message(text='not numeric num modifier', channel=channel)
      return FAILED
    num_modifier = int(tokens[2][1:])
  roll_unmodified = random.randint(1, num_faces)
  roll_modified = roll_unmodified + num_modifier
  action.data.set('roll_unmodified', roll_unmodified)
  action.data.set('roll_modified', roll_modified)
  return PASSED

**Notify:** ``pass``

**Pass:**

.. code-block:: python

  text = 'Roll: ' + str(action.data.get('roll_unmodified')) + " , Result: " + str(action.data.get('roll_modified'))
  action.community.post_message(text=text, channel = "733209360549019688")

**Fail:**

.. code-block:: python

  text = 'Error: Make sure you format your dice roll command correctly!'
  action.community.post_message(text=text, channel = "733209360549019688")

Lottery / Raffle
------------------------

Allow users to vote on a "lottery" message, pick a random user as the lottery winner, and automatically notify the channel.

**Filter:**

.. code-block:: python

  if action.action_type != "DiscordPostMessage":
    return False
  tokens = action.text.split(" ", 1)
  if tokens[0] != "!lottery":
    return False
  if len(tokens) != 2:
    action.community.post_message(text='need a lottery message', channel = "733209360549019688")
    return False
  action.data.set('message', tokens[1])
  return True

**Initialize:** ``pass``

**Notify:**

.. code-block:: python

  message = action.data.get('message')
  action.community.initiate_vote(action, policy, template=message, channel = "733209360549019688")

**Check:**

.. code-block:: python

  all_votes = action.proposal.get_yes_votes()
  num_votes = len(all_votes)
  if num_votes >= 3:
    return PASSED

**Pass:**

.. code-block:: python

  import random

  all_votes = action.proposal.get_yes_votes()
  num_votes = len(all_votes)
  winner = random.randint(0, num_votes)
  winner_name = all_votes[winner].user.readable_name
  message = "Congratulations! " + winner_name + " has won the lottery!"
  action.community.post_message(text=message, channel = "733209360549019688")

**Fail:** ``pass``

Metagov Policies
================

Metagov policies can be defined for any community.
It doesn't matter whether the PolicyKit instance is installed to Slack, Discourse, Discord, or Reddit, as long as
Metagov is enabled and the required Plugins are enabled and configured in the PolicyKit settings page.

Use SourceCred to gate posts on a Discourse topic
-------------------------------------------------

When a user makes a post on Discourse topic 116, look up their Cred value.
If they don't have at least 1 Cred, delete the post, and
send them a message explaining why.

**Required Metagov Plugins**: ``sourcecred`` ``discourse``

**Filter:**

.. code-block:: python

    return action.action_codename == "metagovaction" and \
        action.event_type == "discourse.post_created" and \
        action.event_data["topic_id"] == 116

**Initialize:**

.. code-block:: python

    # store the required cred threshold so we can access it later
    action.data.set("required_cred", 1)

**Notify:** ``pass``

**Check:**

.. code-block:: python

    username = action.initiator.metagovuser.external_username
    params = {"username": username}
    result = metagov.perform_action("sourcecred.user-cred", params)
    user_cred = result["value"]

    # store the user cred value so we can access it later
    action.data.set("cred", user_cred)

    return PASSED if user_cred >= action.data.get("required_cred") else FAILED


**Pass:** ``pass``

**Fail:**

.. code-block:: python

    # Delete the post
    metagov.perform_action("discourse.delete-post", {"id": action.event_data["id"]})

    # Let the user know why
    user_cred = action.data.get("cred")
    required_cred = action.data.get("required_cred")
    post_url = action.event_data["url"]
    discourse_username = action.initiator.metagovuser.external_username
    params = {
        "title": "PolicyKit deleted your post",
        "raw": f"The following post was deleted because you only have {user_cred} Cred, and at least {required_cred} Cred is required for posting on that topic: {post_url}",
        "is_warning": False,
        "target_usernames": [discourse_username]
    }
    metagov.perform_action("discourse.create-message", params)


Vote on Open Collective expense in Open Collective
--------------------------------------------------

**Required Metagov Plugins**: ``opencollective``

**Filter:**

.. code-block:: python

    return action.action_codename == "metagovaction" and \
        action.event_type == "opencollective.expense_created"

**Initialize:**

.. code-block:: python

    # Kick off the Metagov governance process called "opencollective.vote"

    expense_url = action.event_data['url']
    description = action.event_data['description']
    parameters = {
        "title": f"Vote on expense '{description}'",
        "details": f"Thumbs-up or thumbs-down react to vote on expense {expense_url}"
    }
    result = metagov.start_process("opencollective.vote", parameters)
    vote_url = result.outcome.get("vote_url")
    # [elided] optionally, message users on whatever platform to tell them to vote at vote_url

**Notify:** ``pass``


**Check:**

.. code-block:: python

    # When 60 minutes has passed, close the process and decide whether this policy has PASSED or FAILED

    import datetime

    if action.proposal.get_time_elapsed() > datetime.timedelta(minutes=60):
        result = metagov.close_process()
        yes_votes = result.outcome["votes"]["yes"]
        no_votes = result.outcome["votes"]["no"]
        return PASSED if yes_votes >= no_votes else FAILED

    return None


**Pass:**

.. code-block:: python

    # Approve the expense

    parameters = {
        "expense_id": action.event_data["id"],
        "action": "APPROVE"
    }
    metagov.perform_action("opencollective.process-expense", parameters)

**Fail:**

.. code-block:: python

    # Reject the expense

    parameters = {
        "expense_id": action.event_data["id"],
        "action": "REJECT"
    }
    metagov.perform_action("opencollective.process-expense", parameters)


Add a NEAR DAO proposal
-----------------------

When a new Discourse topic is created with tag ``dao-proposal``, add a new proposal to the community's NEAR DAO.
Uses the `near.call <https://metagov.policykit.org/redoc/#operation/near.call>`_ action.

**Required Metagov Plugins**: ``discourse`` ``near``

**Filter:**

.. code-block:: python

    return action.action_codename == "metagovaction" and \
        action.event_type == "discourse.topic_created" and \
        "dao-proposal" in action.event_data["tags"]

**Initialize:** ``pass``

**Notify:** ``pass``

**Check:** ``return PASSED``

**Pass:**

.. code-block:: python

    title = action.event_data["title"]
    topic_url = action.event_data["url"]

    # How we find the wallet ID for the Discourse user? Hard-coding the target for this example.
    discourse_username = action.initiator.metagovuser.external_username


    params = {
        "method_name": "add_proposal",
        "args": {
            "proposal": {
                "description": f"Pay {discourse_username} for {title}. Link: {topic_url}",
                "kind": {"type": "Payout",  "amount": "100" },
                "target": "dev.mashton.testnet"
            }
        },
        "gas": 100000000000000,
        "amount": 100000000000000
    }

    result = metagov.perform_action("near.call", params)
    debug(f"NEAR call: {result.get('status')}")

**Fail:** ``pass``


Vote on Discourse Proposal in Loomio
------------------------------------

When a new Discourse topic is created with tag ``special-proposal``, start a new vote in Loomio
to decide whether to accept or reject the proposal. If rejected, delete the topic. This example
uses the Metagov ``discourse`` plugin, which is distinct from the PolicyKit Discourse integration.
This policy can be defined for any PolicyKit community (a Slack community, for example).

**Required Metagov Plugins**: ``discourse`` ``loomio``

**Filter:**

.. code-block:: python

    return action.action_codename == "metagovaction" and \
        action.event_type == "discourse.topic_created" and \
        "special-proposal" in action.event_data["tags"]

**Initialize:**

.. code-block:: python

    title = action.event_data["title"]
    discourse_username = action.initiator.metagovuser.external_username
    topic_url = action.event_data["url"]

    import datetime
    closing_at = (action.proposal.proposal_time + datetime.timedelta(days=3)).strftime("%Y-%m-%d")

    # Kick off a vote in Loomio
    parameters = {
        "title": f"Vote on adding proposal '{title}'",
        "details": f"proposed by {discourse_username} on Discourse: {topic_url}",
        "options": ["agree", "disagree"],
        "closing_at": closing_at
    }
    result = metagov.start_process("loomio.poll", parameters)
    poll_url = result.outcome.get("poll_url")

    # Make a post in Discourse to let people know where to vote
    params = {
        "topic_id": action.event_data["id"],
        "raw": f"Loomio vote started at {poll_url}",
    }
    metagov.perform_action("discourse.create-post", params)

**Notify:** ``pass``

**Check:**

.. code-block:: python

    result = metagov.get_process()

    # send debug log of intermediate results. visible in PolicyKit app at /logs.,
    debug("Loomio result: " + str(result))

    if result.status == "completed":
        agrees = result.outcome["votes"]["agree"]
        disagrees = result.outcome["votes"]["disagree"]
        outcome_text = f"{agrees} people agreed, and {disagrees} people disagreed."
        action.data.set("outcome_text", outcome_text)

        return PASSED if agrees > disagrees else FAILED

    return None # pending




**Pass:**

.. code-block:: python

    text = action.data.get('outcome_text')
    params = {
        "topic_id": action.event_data["id"],
        "raw": f"{text} The proposal is approved!",
    }
    metagov.perform_action("discourse.create-post", params)

**Fail:**

.. code-block:: python

    text = action.data.get('outcome_text')
    params = {
        "topic_id": action.event_data["id"],
        "raw": f"{text} The proposal is rejected. Deleting this topic."
    }
    metagov.perform_action("discourse.create-post", params)

    # Delete the topic
    metagov.perform_action("discourse.delete-topic", {"id": action.event_data["id"]})

Vote on Adding Payment Pointers to a Web Monetization Rev Share config
----------------------------------------------------------------------

When a Discourse user adds a wallet to their profile, start a vote on whether to add the wallet to the community's `probabilistic revenue share config <https://webmonetization.org/docs/probabilistic-rev-sharing/>`_.
This policy assumes that there is a custom `User Field <https://meta.discourse.org/t/how-to-create-and-configure-custom-user-fields/113192>`_ in Discourse in position "1" that holds an UpHold or GateHub wallet payment pointer.
This policy also assumes that the Discourse server has the experimental `Metagov Web Monetization Discourse plugin <https://github.com/metagov/discourse-web-monetization>`_ installed, to generate revenue from forum content in the form of Web Monetization micropayments. All content generated on Discourse will be split equally between all wallets rev share config, which is stored in Metagov.

**Required Metagov Plugins**: ``discourse``

**Filter:**

.. code-block:: python

    is_user_fields_changed = action.action_codename == "metagovaction" and action.event_type == "discourse.user_fields_changed"
    if not is_user_fields_changed:
      return False

    user = action.event_data["username"]
    custom_wallet_field_key = "1"
    old_wallet = action.event_data.get("old_user_fields", {}).get(custom_wallet_field_key)
    new_wallet = action.event_data.get("user_fields", {}).get(custom_wallet_field_key)
    if old_wallet == new_wallet:
      debug(f"no wallet change for {user}, they must have changed another field. skipping.")
      return False

    debug(f"User {user} changed their wallet from '{old_wallet}' to '{new_wallet}'")
    action.data.set("old_wallet", old_wallet)
    action.data.set("new_wallet", new_wallet)
    return True

**Initialize:** ``pass``

**Notify:**

.. code-block:: python

    user = action.event_data["username"]

    old_wallet = action.data.get("old_wallet")
    new_wallet = action.data.get("new_wallet")
    if not new_wallet:
      debug("wallet was removed, no need to vote")
      return

    #get the current config
    response = metagov.perform_action("revshare.get-config", {})
    debug(f"get-config response: {response}")

    parameters = {
        "title": f"Add '{new_wallet}' to revshare config - test",
        "details": f"{user} proposes to add wallet '{new_wallet}' and remove wallet '{old_wallet or ''}'. The current revshare configuraton is: {response}",
       "options": ["approve", "disapprove"],
       "topic_id": 133
    }
    result = metagov.start_process("discourse.poll", parameters)
    poll_url = result.outcome.get("poll_url")
    debug(f"Vote at {poll_url}")


    params = {
        "title": f"Request to add '{new_wallet}' under review",
        "raw": f"Vote occurring at {poll_url}",
        "target_usernames": [user]
    }
    response = metagov.perform_action("discourse.create-message", params)
    action.data.set("dm_topic_id", response["topic_id"])





**Check:**

.. code-block:: python

    new_wallet = action.data.get("new_wallet")
    if not new_wallet:
      debug("wallet was removed, no need to vote")
      return PASSED


    result = metagov.get_process()
    if not result:
      return None

    debug(f"Discourse Poll ({result.status}) outcome: {result.outcome}")

    agrees = result.outcome.get("votes", {}).get("approve", 0)
    disagrees = result.outcome.get("votes", {}).get("disapprove", 0)

    if (agrees >= 1) or (disagrees >= 3):
      # custom closing condition was met, close the poll in Discourse
      metagov.close_process()
      return PASSED if agrees > disagrees else FAILED
    elif result.status == "completed":
      # the poll was "closed" on discourse by a user
      return PASSED if agrees > disagrees else FAILED

    return None # pending




**Pass:**

.. code-block:: python

     user = action.event_data["username"]
     old_wallet = action.data.get("old_wallet")
     new_wallet = action.data.get("new_wallet")

     debug(f"APPROVED: User {user} changed their wallet from '{old_wallet}' to '{new_wallet}'")

     # remove old pointer.
     if old_wallet:
       response = metagov.perform_action("revshare.remove-pointer", {"pointer": old_wallet})
       debug(f"remove-pointer response: {response}")

     if new_wallet:
       # add new pointer.
       response = metagov.perform_action("revshare.add-pointer", {"pointer": new_wallet, "weight": 1})
       debug(f"add-pointer response: {response}")


       params = {
           "raw": f"Your new payment pointer was added to the revshare config $$$! Current config is {response}",
           "target_usernames": [user],
           "topic_id": action.data.get("dm_topic_id")
       }
       metagov.perform_action("discourse.create-message", params)



**Fail:**

.. code-block:: python

    user = action.event_data["username"]
    old_wallet = action.data.get("old_wallet")
    new_wallet = action.data.get("new_wallet")

    debug(f"FAILED: User {user} changed their wallet from '{old_wallet}' to '{new_wallet}'")

    params = {
        "raw": f"Your request to get $$ was rejected",
        "target_usernames": [user],
       "topic_id": action.data.get("dm_topic_id")
    }
    metagov.perform_action("discourse.create-message", params)




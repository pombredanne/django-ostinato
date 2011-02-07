from django.dispatch import Signal
from django.conf import settings

class InvalidAction(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

sm_pre_action = Signal(providing_args=['action', 'user'])
sm_post_action = Signal(providing_args=['action', 'user'])

class StateMachine(object):
    """
    Any model that wishes to use this statemachine can simply
    inherrit from it.

    Note that this model assumes you have a ``_sm_state`` CharField
    defined in your main model.

    TODO: How to handle permissions?
    """
    SM_ACTIONS = [
        {'action': 'submit',
         'help_text': 'Submit document for review',
         'target': 'review',
         'groups': '', # This is how we will define group permissions for now
        },
        {'action': 'publish',
         'help_text': 'Publish this document',
         'target': 'published'
        },
        {'action': 'reject',
         'help_text': 'Reject the document based',
         'target': 'private'
        },
        {'action': 'archive',
         'help_text': 'Archive this document',
         'target': 'archived'
        },
    ]
    SM_STATEMACHINE = [
        {'state': 'private', 'actions': ['submit', 'publish']},
        {'state': 'review', 'actions': ['publish', 'reject']},
        {'state': 'published', 'actions': ['retract', 'archive']},
        {'state': 'archived', 'actions': ['retract']},
    ]

    def _get_state(self):
        return self._sm_state
    def _set_state(self, what):
        self._sm_state = what
    sm_state = property(_get_state, _set_state)

    def sm_state_actions(self):
        """
        Returns a list of actions available for the current state.
        """
        return self._get_state_obj(self.sm_state)['actions']

    def _get_action(self, action):
        for item in self.SM_ACTIONS:
            if action == item['action']: return item

    def _get_state_obj(self, state):
        """ Get a specific state dict from the statemachine """
        for item in self.SM_STATEMACHINE:
            if state == item['state']: return item

    def sm_take_action(self, action, **kwargs):
        """
        Take an action to change the state and send the apropriate signals.

        ``kwargs`` can be used to pass along extra data to the ``pre_action()``
        and ``post_action()`` methods, and is ideal for passing along data to
        update other fields in the model before saving.
        """
        if action in self.sm_state_actions():
            self.sm_pre_action(action=action, **kwargs)
            self.sm_state = self._get_action(action)['target']
            self.sm_post_action(action=action, **kwargs)
        else:
            raise InvalidAction('Invalid action, %s. Choices are, %s' % (
                action, ','.join(self.sm_state_actions())))

    def sm_pre_action(self, **kwargs):
        """
        Method can be used to do some extra stuff to our model before the
        action is taken and saved.
        Just override in your model if you need it.
        """
        sm_pre_action.send(sender=self, instance=self, **kwargs)

    def sm_post_action(self, **kwargs):
        """
        Method can be used to do some extra stuff to our model after the
        action is saved.
        Just override in your model if you need it.
        """
        sm_post_action.send(sender=self, instance=self, **kwargs)

    # Admin Callables
    def sm_state_admin(self):
        return self.sm_state
    sm_state_admin.description = "The current state for the items"

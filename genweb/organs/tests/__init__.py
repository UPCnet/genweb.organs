import unittest2 as unittest
from plone import api


class organsTestBase(unittest.TestCase):

    def create_organ(self, id='organ-govern', name=u'organ-govern', organ_type='Closed'):
        """ Creates the community, it assumes the current logged in user """
        if api.user.is_anonymous():
            self.assertTrue(False, msg='Tried to create an Organ without permissions.')

        if 'Secretari' not in api.user.get_roles():
            self.assertTrue(False, msg='Tried to create an Organ but the user has not enough permissions to do so.')

        # self.portal.invokeFactory('genweb.organs.organsfolder', id,
        #                           title=name,
        #                           community_type=organ_type,)
        return self.portal[id]
